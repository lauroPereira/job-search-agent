"""Client of the real server: tools per agent, direct calls, proposals and environment."""

import sys
from pathlib import Path

import pytest
from fastmcp import Client
from langchain_core.messages import ToolMessage

from job_search_agent import mcp_client
from job_search_agent.config import Server
from job_search_agent.mcp_client import (
    APPROVAL_TOOLS,
    CLASSIFIED_TOOLS,
    JOBS_TOOLS,
    NETWORK_TOOLS,
    UnclassifiedToolError,
    agent_tools,
    call,
    extract_proposal,
)

# The table of the plan ("Grafo"), written out again on purpose.
EXPECTED_NETWORK = {
    "list_contacts",
    "network_list_companies",
    "network_company_overview",
    "pending_followups",
    "log_interaction",
    "network_save_person",
    "network_save_company",
}
EXPECTED_JOBS = {
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
}
NETWORK_WRITES = {"log_interaction", "network_save_person", "network_save_company"}


async def tool_names(server: Server, agent: str) -> set[str]:
    async with mcp_client.adapter(server) as mcp:
        return {tool.name for tool in await agent_tools(mcp, agent)}


async def test_each_agent_gets_exactly_its_tools(server: Server) -> None:
    network = await tool_names(server, "network")
    jobs = await tool_names(server, "jobs")
    assert network == EXPECTED_NETWORK
    assert jobs == EXPECTED_JOBS
    assert {"list_contacts", "network_company_overview"} <= jobs  # supporting reads (Q3)
    assert not jobs & NETWORK_WRITES
    assert not any(name.startswith("changes_") for name in network | jobs)


async def test_all_announced_tools_are_classified(server: Server) -> None:
    async with mcp_client.client(server) as client:
        announced = {tool.name for tool in await client.list_tools()}
    assert len(announced) == 17
    assert announced <= CLASSIFIED_TOOLS


async def test_unclassified_tool_fails(server: Server, monkeypatch) -> None:
    monkeypatch.setattr(mcp_client, "CLASSIFIED_TOOLS", CLASSIFIED_TOOLS - {"list_jobs"})
    with pytest.raises(UnclassifiedToolError, match="list_jobs"):
        await tool_names(server, "jobs")


def test_lists_match_the_plan() -> None:
    assert NETWORK_TOOLS == EXPECTED_NETWORK
    assert JOBS_TOOLS == EXPECTED_JOBS
    assert APPROVAL_TOOLS == {"changes_confirm", "changes_discard"}


async def test_add_job_changes_nothing_until_confirmed(fresh_server: Server) -> None:
    url = "https://vagas.example.com/empresa-teste/data-engineer"
    async with mcp_client.client(fresh_server) as client:
        before = await call(client, "list_jobs")
        result = await call(
            client, "add_job", company="Empresa Teste", title="Data Engineer", url=url
        )
        proposal = result["proposal"]
        assert proposal["tool"] == "add_job"
        assert await call(client, "list_jobs") == before

        confirmed = await call(client, "changes_confirm", proposal_id=proposal["id"])
        assert "error" not in confirmed
        after = await call(client, "list_jobs")
    assert url in str(after) and url not in str(before)


async def test_agent_tool_result_carries_the_proposal(fresh_server: Server) -> None:
    async with mcp_client.adapter(fresh_server) as mcp:
        tools = {tool.name: tool for tool in await agent_tools(mcp, "jobs")}
        message = await tools["add_job"].ainvoke(
            {
                "type": "tool_call",
                "id": "call-1",
                "name": "add_job",
                "args": {
                    "company": "Empresa Teste",
                    "title": "Data Engineer",
                    "url": "https://vagas.example.com/empresa-teste/data-engineer",
                },
            }
        )
        read = await tools["list_jobs"].ainvoke(
            {"type": "tool_call", "id": "call-2", "name": "list_jobs", "args": {}}
        )
    assert isinstance(message, ToolMessage)
    proposal = extract_proposal(message)
    assert proposal is not None and proposal["tool"] == "add_job"
    assert extract_proposal(read) is None


async def test_api_key_does_not_reach_the_server(server: Server, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "not-a-real-key")
    transport = mcp_client.transport(server)
    assert transport.env == {"JOB_SEARCH_DB": str(server.db)}
    # Same transport, same env; only the program is a probe that lists its variables.
    transport.command = sys.executable
    transport.args = [str(Path(__file__).with_name("env_probe_server.py"))]
    async with Client(transport) as client:
        names = (await client.call_tool("environment", {})).structured_content["names"]
    assert "JOB_SEARCH_DB" in names
    assert "OPENAI_API_KEY" not in names


def test_demo_db_refuses_existing_database(server: Server) -> None:
    with pytest.raises(FileExistsError):
        mcp_client.create_demo_db(server)
