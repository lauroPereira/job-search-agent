"""The graph of a turn: day limit, router, `decline` and the Network and Jobs agents.

The nodes receive an `MCPAdapter` already open (the caller keeps `async with adapter(...)` for
the turn, or for the life of the app); no node opens the server. Proposals returned by write tools
go to `pending` and the turn ends as `awaiting_approval` (the approval node comes in task 06).
Every model call and tool call is written to the trace, masked, with tokens and cost.
"""

from datetime import date
from typing import Annotated, Any, Literal, TypedDict

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from job_search_agent import prompts
from job_search_agent.config import Config
from job_search_agent.costs import (
    Usage,
    day_limit_reached,
    model_cost_usd,
    over_turn_limit,
    usage_from_metadata,
)
from job_search_agent.mcp_client import AGENT_TOOLS, MCPAdapter, agent_tools, extract_proposal
from job_search_agent.traces import TraceStore

Route = Literal["network", "jobs", "refuse", "out_of_scope"]


class RouteDecision(BaseModel):
    """Structured output of the router."""

    route: Route
    reason: str


class TurnState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    route: str | None  # a Route, or "day_limit"
    agent: str | None
    origin: str | None
    reference_date: str
    pending: list[dict]
    usage: dict  # running total of the turn: tokens and cost_usd
    turn_id: int
    status: str | None


ZERO_USAGE = {"input_tokens": 0, "output_tokens": 0, "cached_tokens": 0, "cost_usd": 0.0}


def _add_usage(total: dict, usage: Usage, cost: float) -> dict:
    return {
        "input_tokens": total["input_tokens"] + usage.input_tokens,
        "output_tokens": total["output_tokens"] + usage.output_tokens,
        "cached_tokens": total["cached_tokens"] + usage.cached_tokens,
        "cost_usd": total["cost_usd"] + cost,
    }


async def build_graph(
    config: Config,
    models: dict[str, BaseChatModel],
    mcp: MCPAdapter,
    knowledge: BaseTool,
    traces: TraceStore,
    checkpointer: Any = None,
):
    """Compile the graph. `models` has the "router" and "agent" models (real or scripted)."""
    tools = {agent: [*await agent_tools(mcp, agent), knowledge] for agent in AGENT_TOOLS}
    router = models["router"].with_structured_output(RouteDecision, include_raw=True)

    def record_model(state: TurnState, role: str, message: AIMessage, total: dict) -> dict:
        """Write a model step and return the new running usage of the turn."""
        model = config.models[role]
        usage = usage_from_metadata(message.usage_metadata)
        cost = model_cost_usd(model, usage, config.pricing)
        names = [call["name"] for call in message.tool_calls]
        traces.add_step(
            state["turn_id"],
            "model",
            model,
            args={"tool_calls": names} if names else None,
            result=message.text or None,
            tokens=usage.total_tokens,
            cost_usd=cost,
        )
        return _add_usage(total, usage, cost)

    def check_day_limit(state: TurnState) -> dict:
        if day_limit_reached(traces.tokens_on(date.today()), config.limits):
            return {"route": "day_limit"}
        return {}

    async def route(state: TurnState) -> dict:
        request = state["messages"][-1]
        result = await router.ainvoke([SystemMessage(prompts.ROUTER), request])
        decision = result["parsed"]
        chosen = decision.route if isinstance(decision, RouteDecision) else "out_of_scope"
        usage = record_model(state, "router", result["raw"], state.get("usage", ZERO_USAGE))
        return {"route": chosen, "usage": usage}

    def decline(state: TurnState) -> dict:
        code = state["route"]
        status = "budget_exceeded" if code == "day_limit" else "declined"
        return {"messages": [AIMessage(prompts.DECLINE[code])], "status": status}

    def agent_node(name: str):
        async def run_agent(state: TurnState) -> dict:
            agent = create_agent(
                models["agent"],
                tools[name],
                system_prompt=prompts.agent_prompt(name, state["reference_date"]),
                name=f"{name}_agent",
            )
            history = state["messages"]
            last: dict = {"messages": history}
            exceeded = False
            try:
                # Values stream: on GraphRecursionError the steps already taken are still known.
                async for last in agent.astream(
                    {"messages": history},
                    {"recursion_limit": config.limits.recursion_limit},
                    stream_mode="values",
                ):
                    pass
            except GraphRecursionError:
                exceeded = True
            new = last["messages"][len(history) :]

            usage = state.get("usage", ZERO_USAGE)
            calls: dict[str, dict] = {}
            pending: list[dict] = []
            for message in new:
                if isinstance(message, AIMessage):
                    usage = record_model(state, "agent", message, usage)
                    calls |= {call["id"]: call for call in message.tool_calls}
                elif isinstance(message, ToolMessage):
                    call = calls.get(message.tool_call_id, {})
                    traces.add_step(
                        state["turn_id"],
                        "tool",
                        message.name or call.get("name", "?"),
                        args=call.get("args"),
                        result=message.text,
                    )
                    proposal = extract_proposal(message)
                    if proposal is not None:
                        pending.append(proposal)

            if exceeded:
                # The unfinished steps stay in the trace, not in the conversation (a tool call
                # without its result would break the next turn).
                return {
                    "messages": [AIMessage(prompts.BUDGET_EXCEEDED)],
                    "agent": f"{name}_agent",
                    "usage": usage,
                    "status": "budget_exceeded",
                }
            return {
                "messages": new,
                "agent": f"{name}_agent",
                "usage": usage,
                "pending": pending,
                "status": "awaiting_approval" if pending else "answered",
            }

        return run_agent

    builder = StateGraph(TurnState)
    builder.add_node("check_day_limit", check_day_limit)
    builder.add_node("route", route)
    builder.add_node("decline", decline)
    builder.add_node("network_agent", agent_node("network"))
    builder.add_node("jobs_agent", agent_node("jobs"))
    builder.add_edge(START, "check_day_limit")
    builder.add_conditional_edges(
        "check_day_limit",
        lambda state: "decline" if state.get("route") == "day_limit" else "route",
        ["decline", "route"],
    )
    builder.add_conditional_edges(
        "route",
        lambda state: {"network": "network_agent", "jobs": "jobs_agent"}.get(
            state["route"], "decline"
        ),
        ["network_agent", "jobs_agent", "decline"],
    )
    for node in ("decline", "network_agent", "jobs_agent"):
        builder.add_edge(node, END)
    return builder.compile(checkpointer=checkpointer)


async def arun_turn(
    graph,
    traces: TraceStore,
    config: Config,
    text: str,
    *,
    thread_id: str,
    reference_date: date,
    origin: str | None = None,
) -> dict:
    """Run one turn and close it in the trace. Returns answer, status, route, pending and usage."""
    turn_id = traces.start_turn(thread_id, text, origin, reference_date)
    start: TurnState = {
        "messages": [HumanMessage(text)],
        "route": None,
        "agent": None,
        "origin": origin,
        "reference_date": reference_date.isoformat(),
        "pending": [],
        "usage": dict(ZERO_USAGE),
        "turn_id": turn_id,
        "status": None,
    }
    try:
        state = await graph.ainvoke(start, {"configurable": {"thread_id": thread_id}})
    except Exception:
        traces.finish_turn(turn_id, "error")
        raise
    totals = state["usage"]
    usage = Usage(totals["input_tokens"], totals["output_tokens"], totals["cached_tokens"])
    traces.finish_turn(
        turn_id,
        state["status"],
        usage,
        totals["cost_usd"],
        route=state["route"],
        agent=state.get("agent"),
        over_turn_limit=over_turn_limit(usage, config.limits),
    )
    return {
        "turn_id": turn_id,
        "answer": state["messages"][-1].text,
        "status": state["status"],
        "route": state["route"],
        "agent": state.get("agent"),
        "pending": state.get("pending", []),
        "usage": totals,
    }
