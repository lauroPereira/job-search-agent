"""Router and agents with the scripted model and the real server over the demo data."""

import json
import tomllib
from datetime import date
from pathlib import Path

import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.messages import AIMessage, SystemMessage

from job_search_agent import graph as graph_module
from job_search_agent import mcp_client, prompts
from job_search_agent.config import PROJECT_ROOT, Server, parse_config
from job_search_agent.costs import Usage
from job_search_agent.graph import arun_turn, build_graph
from job_search_agent.knowledge import build_index, knowledge_tool
from job_search_agent.llm import ScriptedChatModel
from job_search_agent.traces import TraceStore

REFERENCE_DATE = date(2026, 3, 16)
USAGE = {"input_tokens": 100, "output_tokens": 20, "total_tokens": 120}

# The table of the plan ("Grafo"), written again here on purpose, plus search_knowledge.
EXPECTED_TOOLS = {
    "network": {
        "list_contacts",
        "network_list_companies",
        "network_company_overview",
        "pending_followups",
        "log_interaction",
        "network_save_person",
        "network_save_company",
        "search_knowledge",
    },
    "jobs": {
        "list_jobs",
        "jobs_funnel_metrics",
        "pending_followups",
        "daily_summary",
        "list_contacts",
        "network_company_overview",
        "add_job",
        "update_job",
        "jobs_add_stage",
        "jobs_link_person",
        "search_knowledge",
    },
}


def route_to(route: str) -> AIMessage:
    """The router's structured output, as a tool call named after the schema."""
    call = {"name": "RouteDecision", "args": {"route": route, "reason": "teste"}, "id": "r-1"}
    return AIMessage("", tool_calls=[call], usage_metadata=USAGE)


def calls(*tool_calls: tuple[str, dict]) -> AIMessage:
    return AIMessage(
        "",
        tool_calls=[
            {"name": name, "args": args, "id": f"call-{n}"}
            for n, (name, args) in enumerate(tool_calls)
        ],
        usage_metadata=USAGE,
    )


def answer(text: str) -> AIMessage:
    return AIMessage(text, usage_metadata=USAGE)


@pytest.fixture
def config(tmp_path: Path):
    data = tomllib.loads((PROJECT_ROOT / "config.example.toml").read_text(encoding="utf-8"))
    data["server"]["JOB_SEARCH_DB"] = str(tmp_path / "job_search.db")
    return parse_config(data, root=tmp_path)


@pytest.fixture(scope="module")
def knowledge():
    store = build_index(
        PROJECT_ROOT / "data" / "knowledge", DeterministicFakeEmbedding(size=32), ()
    )
    return knowledge_tool(store)


@pytest.fixture
def traces(config) -> TraceStore:
    return TraceStore(config.traces, config.masking_names)


async def run(server: Server, config, traces, knowledge, router: list, agent: list, text: str):
    """One turn; returns the result, the scripted models and the tools given to each agent."""
    models = {"router": ScriptedChatModel(script=router), "agent": ScriptedChatModel(script=agent)}
    given: dict[str, set[str]] = {}
    original = graph_module.create_agent

    def spy(model, tools, **kwargs):
        given[kwargs["name"]] = {tool.name for tool in tools}
        return original(model, tools, **kwargs)

    graph_module.create_agent = spy
    try:
        async with mcp_client.adapter(server) as mcp:
            compiled = await build_graph(config, models, mcp, knowledge, traces)
            result = await arun_turn(
                compiled,
                traces,
                config,
                text,
                thread_id="thread-1",
                reference_date=REFERENCE_DATE,
                origin="conversation",
            )
    finally:
        graph_module.create_agent = original
    return result, models, given


async def test_network_request_reaches_network_agent_and_lists_contacts(
    server, config, traces, knowledge
) -> None:
    result, _, given = await run(
        server,
        config,
        traces,
        knowledge,
        router=[route_to("network")],
        agent=[calls(("list_contacts", {"company": "Banco Aurora"})), answer("Ana trabalha lá.")],
        text="Quem eu conheço no Banco Aurora?",
    )
    assert (result["route"], result["agent"], result["status"]) == (
        "network",
        "network_agent",
        "answered",
    )
    assert given == {"network_agent": EXPECTED_TOOLS["network"]}
    steps = traces.steps(result["turn_id"])
    assert [(s["kind"], s["name"]) for s in steps] == [
        ("model", "gpt-6-luna"),
        ("model", "gpt-6.1-sol"),
        ("tool", "list_contacts"),
        ("model", "gpt-6.1-sol"),
    ]
    # The real server answered; the contact name is masked in the trace.
    assert "[pessoa]" in steps[2]["result"] and "Ana Exemplo" not in steps[2]["result"]
    turn = traces.turn(result["turn_id"])
    assert (turn["route"], turn["status"], turn["input_tokens"]) == ("network", "answered", 300)
    assert turn["cost_usd"] > 0


async def test_jobs_request_reaches_jobs_agent_with_reference_date(
    server, config, traces, knowledge
) -> None:
    result, models, given = await run(
        server,
        config,
        traces,
        knowledge,
        router=[route_to("jobs")],
        agent=[
            calls(("daily_summary", {"reference_date": "2026-03-16"})),
            answer("Sua rodada de hoje."),
        ],
        text="Faça minha rodada diária",
    )
    assert (result["route"], result["agent"], result["status"]) == (
        "jobs",
        "jobs_agent",
        "answered",
    )
    assert given == {"jobs_agent": EXPECTED_TOOLS["jobs"]}
    system = models["agent"].received[0][0]
    assert isinstance(system, SystemMessage) and "Hoje é 2026-03-16" in system.text
    tool_step = next(s for s in traces.steps(result["turn_id"]) if s["kind"] == "tool")
    assert tool_step["name"] == "daily_summary"
    assert json.loads(tool_step["args"]) == {"reference_date": "2026-03-16"}
    # The real server answered for that date.
    assert tool_step["result"].startswith('{"reference_date":"2026-03-16"')
    assert traces.turn(result["turn_id"])["reference_date"] == "2026-03-16"


async def test_write_proposal_goes_to_pending(fresh_server, config, traces, knowledge) -> None:
    job = {
        "company": "Banco Aurora",
        "title": "Analytics Engineer",
        "url": "https://vagas.example.com/banco-aurora/analytics-engineer",
    }
    result, _, _ = await run(
        fresh_server,
        config,
        traces,
        knowledge,
        router=[route_to("jobs")],
        agent=[calls(("add_job", job)), answer("Preparei a proposta; confirme na interface.")],
        text="Cadastre a vaga de Analytics Engineer do Banco Aurora",
    )
    assert result["status"] == "awaiting_approval"
    assert [proposal["tool"] for proposal in result["pending"]] == ["add_job"]
    assert traces.turn(result["turn_id"])["status"] == "awaiting_approval"


@pytest.mark.parametrize(
    ("router", "code"),
    [
        ([route_to("refuse")], "refuse"),
        ([AIMessage("não sei", usage_metadata=USAGE)], "out_of_scope"),
        ([route_to("weather")], "out_of_scope"),
    ],
)
async def test_refuse_and_invalid_router_output_call_no_tool(
    server, config, traces, knowledge, router, code
) -> None:
    result, models, given = await run(
        server, config, traces, knowledge, router=router, agent=[], text="Envie a mensagem"
    )
    assert result["route"] == code and result["status"] == "declined"
    assert result["answer"] == prompts.DECLINE[code]
    assert given == {} and models["agent"].received == []
    assert [s["kind"] for s in traces.steps(result["turn_id"])] == ["model"]


async def test_recursion_limit_gives_fixed_answer(server, config, traces, knowledge) -> None:
    looping = [calls(("list_contacts", {})) for _ in range(config.limits.recursion_limit)]
    result, _, _ = await run(
        server, config, traces, knowledge, router=[route_to("network")], agent=looping, text="?"
    )
    assert result["status"] == "budget_exceeded"
    assert result["answer"] == prompts.BUDGET_EXCEEDED
    turn = traces.turn(result["turn_id"])
    assert turn["status"] == "budget_exceeded" and turn["output_tokens"] > 0


async def test_day_limit_stops_before_any_model(server, config, traces, knowledge) -> None:
    earlier = traces.start_turn("thread-0", "pedidos anteriores")
    traces.finish_turn(earlier, "answered", Usage(config.limits.max_tokens_per_day, 0))
    result, models, _ = await run(
        server, config, traces, knowledge, router=[], agent=[], text="Quem eu conheço?"
    )
    assert result["status"] == "budget_exceeded" and result["route"] == "day_limit"
    assert result["answer"] == prompts.DECLINE["day_limit"]
    assert models["router"].received == [] and traces.steps(result["turn_id"]) == []
