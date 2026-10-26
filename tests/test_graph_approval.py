"""Approval: one interrupt per proposal, decisions through the server, checkpointer in SQLite."""

from contextlib import AsyncExitStack, asynccontextmanager
from datetime import date
from pathlib import Path

import pytest
from fastmcp.exceptions import ToolError
from test_graph_routing import answer, calls, route_to

from job_search_agent import graph as graph_module
from job_search_agent import mcp_client
from job_search_agent.graph import (
    arun_turn,
    build_graph,
    input_enabled,
    open_checkpointer,
)
from job_search_agent.llm import ScriptedChatModel
from job_search_agent.mcp_client import call
from job_search_agent.traces import TraceStore

REFERENCE_DATE = date(2026, 3, 16)
NEW_JOB_URL = "https://vagas.example.com/banco-aurora/analytics-engineer"


def update_status(status: str) -> tuple[str, dict]:
    return ("update_job", {"job_id": 1, "source": "conversation", "status": status})


def add_job() -> tuple[str, dict]:
    return (
        "add_job",
        {"company": "Banco Aurora", "title": "Analytics Engineer", "url": NEW_JOB_URL},
    )


@asynccontextmanager
async def session(server, config, knowledge, traces, agent_script, checkpoints=None):
    """An open adapter and a compiled graph (with the SQLite checkpointer at `checkpoints`, if
    given); the router always routes to jobs."""
    models = {
        "router": ScriptedChatModel(script=[route_to("jobs")]),
        "agent": ScriptedChatModel(script=agent_script),
    }
    async with AsyncExitStack() as stack:
        saver = (
            await stack.enter_async_context(open_checkpointer(checkpoints)) if checkpoints else None
        )
        mcp = await stack.enter_async_context(mcp_client.adapter(server))
        yield await build_graph(config, models, mcp, knowledge, traces, saver), mcp


async def turn(compiled, traces, config, text=None, resume=None, thread_id="thread-1"):
    return await arun_turn(
        compiled,
        traces,
        config,
        text,
        thread_id=thread_id,
        reference_date=REFERENCE_DATE,
        origin="conversation",
        resume=resume,
    )


async def job_one(mcp) -> dict:
    jobs = (await call(mcp.client, "list_jobs"))["jobs"]
    return next(job for job in jobs if job["id"] == 1)


async def test_discard_does_not_change_the_server(fresh_server, config, knowledge, traces):
    script = [calls(update_status("hr_interview")), answer("Proposta pronta.")]
    async with session(fresh_server, config, knowledge, traces, script) as (compiled, mcp):
        before = await call(mcp.client, "list_jobs")
        first = await turn(compiled, traces, config, "A vaga do Banco Aurora foi para o RH")
        assert first["status"] == "awaiting_approval"
        assert first["proposal"]["tool"] == "update_job"
        state = (await compiled.aget_state({"configurable": {"thread_id": "thread-1"}})).values
        assert not input_enabled(state)

        result = await turn(compiled, traces, config, resume="discard")
        after = await call(mcp.client, "list_jobs")
        state = (await compiled.aget_state({"configurable": {"thread_id": "thread-1"}})).values

    assert after == before
    assert input_enabled(state)
    assert result["status"] == "answered" and result["proposal"] is None
    assert result["answer"] == "Recusado (update_job): nada foi gravado."
    approval = [s for s in traces.steps(result["turn_id"]) if s["kind"] == "approval"]
    assert len(approval) == 1 and approval[0]["name"] == "update_job"
    assert '"decision": "discard"' in approval[0]["args"]
    assert traces.turn(result["turn_id"])["status"] == "answered"


async def test_confirm_writes_and_the_result_is_in_the_answer(
    fresh_server, config, knowledge, traces
):
    script = [calls(update_status("hr_interview")), answer("Proposta pronta.")]
    async with session(fresh_server, config, knowledge, traces, script) as (compiled, mcp):
        await turn(compiled, traces, config, "A vaga do Banco Aurora foi para o RH")
        result = await turn(compiled, traces, config, resume="confirm")
        job = await job_one(mcp)
    assert job["status"] == "hr_interview"
    assert result["answer"].startswith("Confirmado (update_job)")
    assert "hr_interview" in result["answer"]
    assert result["decided"][0]["result"] == "ok"


async def test_two_proposals_are_two_interrupts_in_sequence(
    fresh_server, config, knowledge, traces
):
    script = [calls(update_status("hr_interview"), add_job()), answer("Duas propostas.")]
    async with session(fresh_server, config, knowledge, traces, script) as (compiled, mcp):
        first = await turn(compiled, traces, config, "Atualize e cadastre")
        assert first["proposal"]["tool"] == "update_job"
        second = await turn(compiled, traces, config, resume="confirm")
        assert second["status"] == "awaiting_approval"
        assert second["proposal"]["tool"] == "add_job"
        last = await turn(compiled, traces, config, resume="discard")
        job = await job_one(mcp)
        jobs = await call(mcp.client, "list_jobs")

    assert job["status"] == "hr_interview"
    assert NEW_JOB_URL not in str(jobs)
    assert last["status"] == "answered" and last["proposal"] is None
    assert [(d["tool"], d["decision"]) for d in last["decided"]] == [
        ("update_job", "confirm"),
        ("add_job", "discard"),
    ]
    steps = [s["name"] for s in traces.steps(last["turn_id"]) if s["kind"] == "approval"]
    assert steps == ["update_job", "add_job"]


async def test_stale_proposal_is_shown_without_retry(fresh_server, config, knowledge, traces):
    script = [
        calls(update_status("hr_interview"), update_status("tech_interview")),
        answer("Duas propostas para a mesma vaga."),
    ]
    async with session(fresh_server, config, knowledge, traces, script) as (compiled, mcp):
        await turn(compiled, traces, config, "Atualize duas vezes")
        await turn(compiled, traces, config, resume="confirm")
        result = await turn(compiled, traces, config, resume="confirm")
        job = await job_one(mcp)

    assert job["status"] == "hr_interview"
    assert "desatualizada" in result["answer"] and "nada foi gravado" in result["answer"]
    assert result["decided"][1]["result"] == "stale_proposal"
    assert result["status"] == "answered" and result["proposal"] is None
    approval = [s for s in traces.steps(result["turn_id"]) if s["kind"] == "approval"]
    assert len(approval) == 2  # no automatic retry


async def test_tool_error_gives_a_clear_message(
    fresh_server, config, knowledge, traces, monkeypatch
):
    async def failing_call(*args, **kwargs):
        raise ToolError("server crashed")

    script = [calls(update_status("hr_interview")), answer("Proposta pronta.")]
    async with session(fresh_server, config, knowledge, traces, script) as (compiled, _):
        await turn(compiled, traces, config, "A vaga foi para o RH")
        monkeypatch.setattr(graph_module, "call", failing_call)
        result = await turn(compiled, traces, config, resume="confirm")
    assert result["decided"][0]["result"] == "tool_error"
    assert "Falha ao falar com o servidor" in result["answer"]


async def test_resume_after_reopening_the_checkpointer(
    fresh_server, config, knowledge, tmp_path: Path
):
    path = tmp_path / "local" / "checkpoints.db"
    traces = TraceStore(config.traces, config.masking_names)
    script = [calls(update_status("hr_interview")), answer("Proposta pronta.")]
    async with session(fresh_server, config, knowledge, traces, script, path) as (g, _):
        first = await turn(g, traces, config, "A vaga foi para o RH", thread_id="t-9")
    assert first["proposal"]["tool"] == "update_job"

    # A new process: new checkpointer connection, new adapter, new graph, no model needed.
    async with session(fresh_server, config, knowledge, traces, [], path) as (g, mcp):
        state = (await g.aget_state({"configurable": {"thread_id": "t-9"}})).values
        assert state["pending"][0]["id"] == first["proposal"]["id"]
        result = await turn(g, traces, config, resume="confirm", thread_id="t-9")
        job = await job_one(mcp)
    assert job["status"] == "hr_interview"
    assert result["turn_id"] == first["turn_id"] and result["status"] == "answered"


async def test_resume_without_pending_is_refused(server, config, knowledge, traces):
    async with session(server, config, knowledge, traces, []) as (compiled, _):
        with pytest.raises(ValueError, match="no proposal waiting"):
            await turn(compiled, traces, config, resume="confirm")
