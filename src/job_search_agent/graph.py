"""The graph of a turn: day limit, router, `decline`, the Network and Jobs agents and approval.

The nodes receive an `MCPAdapter` already open (the caller keeps `async with adapter(...)` for
the turn, or for the life of the app); no node opens the server. Proposals returned by write tools
go to `pending`; the `approval` node pauses with one `interrupt` per proposal, in order, and after
the person's decision calls `changes_confirm` or `changes_discard` through the adapter's own
client (`MCPAdapter.client`, no second server start). Every model call, tool call and decision is
written to the trace, masked, with tokens and cost.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Annotated, Any, Literal, TypedDict

from fastmcp.exceptions import ToolError
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt
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
from job_search_agent.mcp_client import (
    AGENT_TOOLS,
    MCPAdapter,
    agent_tools,
    call,
    extract_proposal,
)
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
    pending: list[dict]  # proposals without a decision, in order
    decided: list[dict]  # proposal id, tool, decision and result code
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

    async def approval(state: TurnState) -> dict:
        # interrupt() is the first instruction: on resume the node runs again from the top, so
        # nothing with an effect may come before it.
        decision = interrupt({"proposal": state["pending"][0]})
        proposal = state["pending"][0]
        if decision not in ("confirm", "discard"):
            raise ValueError(f"Approval decision must be 'confirm' or 'discard', got {decision!r}")
        tool = "changes_confirm" if decision == "confirm" else "changes_discard"
        try:
            result = await call(mcp.client, tool, proposal_id=proposal["id"])
        except ToolError as failure:
            result = {"error": "tool_error", "detail": str(failure)}
        code = result.get("error", "ok") if isinstance(result, dict) else "ok"
        traces.add_step(
            state["turn_id"],
            "approval",
            proposal["tool"],
            args={"proposal_id": proposal["id"], "decision": decision, "result": code},
            result=result,
        )
        remaining = state["pending"][1:]
        decided = {"id": proposal["id"], "tool": proposal["tool"], "decision": decision}
        return {
            "messages": [AIMessage(prompts.decision_message(proposal, decision, result))],
            "pending": remaining,
            "decided": [*state.get("decided", []), decided | {"result": code}],
            "status": "awaiting_approval" if remaining else "answered",
        }

    def after_proposals(state: TurnState) -> str:
        return "approval" if state.get("pending") else END

    builder = StateGraph(TurnState)
    builder.add_node("check_day_limit", check_day_limit)
    builder.add_node("route", route)
    builder.add_node("decline", decline)
    builder.add_node("network_agent", agent_node("network"))
    builder.add_node("jobs_agent", agent_node("jobs"))
    builder.add_node("approval", approval)
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
    builder.add_edge("decline", END)
    # One interrupt per proposal: the edge goes back to approval while any is pending.
    for node in ("network_agent", "jobs_agent", "approval"):
        builder.add_conditional_edges(node, after_proposals, ["approval", END])
    # interrupt() and aget_state need a checkpointer; without one (tests), it lives in memory.
    return builder.compile(checkpointer=checkpointer or InMemorySaver())


@asynccontextmanager
async def open_checkpointer(path: Path) -> AsyncIterator[AsyncSqliteSaver]:
    """Checkpointer in SQLite (`data/local/checkpoints.db`), kept open while in use."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    async with AsyncSqliteSaver.from_conn_string(str(path)) as saver:
        yield saver


def input_enabled(state: dict | None) -> bool:
    """The chat input is enabled only when no proposal waits for a decision."""
    return not (state or {}).get("pending")


async def arun_turn(
    graph,
    traces: TraceStore,
    config: Config,
    text: str | None = None,
    *,
    thread_id: str,
    reference_date: date | None = None,
    origin: str | None = None,
    resume: str | None = None,
) -> dict:
    """Run a new turn (`text`) or resume the pending approval (`resume` = "confirm" or "discard")
    and close the turn in the trace.

    Returns answer, status, route, agent, the next proposal waiting for a decision (or None),
    the decided proposals and the usage (tokens and cost) of the turn.
    """
    run_config = {"configurable": {"thread_id": thread_id}}
    if resume is not None:
        values = (await graph.aget_state(run_config)).values
        if not values.get("pending"):
            raise ValueError(f"Thread {thread_id!r} has no proposal waiting for a decision")
        turn_id = values["turn_id"]
        graph_input: Any = Command(resume=resume)
    else:
        if text is None or reference_date is None:
            raise ValueError("A new turn needs text and reference_date")
        turn_id = traces.start_turn(thread_id, text, origin, reference_date)
        graph_input = {
            "messages": [HumanMessage(text)],
            "route": None,
            "agent": None,
            "origin": origin,
            "reference_date": reference_date.isoformat(),
            "pending": [],
            "decided": [],
            "usage": dict(ZERO_USAGE),
            "turn_id": turn_id,
            "status": None,
        }
    try:
        await graph.ainvoke(graph_input, run_config)
    except Exception:
        traces.finish_turn(turn_id, "error")
        raise
    state = (await graph.aget_state(run_config)).values
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
    pending = state.get("pending", [])
    return {
        "turn_id": turn_id,
        "answer": state["messages"][-1].text,
        "status": state["status"],
        "route": state["route"],
        "agent": state.get("agent"),
        "proposal": pending[0] if pending else None,
        "decided": state.get("decided", []),
        "usage": totals,
    }
