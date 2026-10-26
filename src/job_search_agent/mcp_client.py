"""Connection to the job-search-mcp server over stdio.

- Agents: `MCPAdapter` (langchain.mcp, beta) only lists the tools, as LangChain tools; each agent
  gets only the names of its list below.
- Direct calls without a model (approval node and dashboard): `fastmcp.Client`.

Every use of langchain.mcp stays in this module. The server process only receives the variables
of `Server.env()` (plus the safe defaults of the MCP SDK, such as PATH): no API key.
"""

import shutil
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import StdioTransport
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool
from mcp.client.stdio import get_default_environment

from job_search_agent.config import PROJECT_ROOT, Server

with warnings.catch_warnings():
    # The namespace is in beta (accepted risk of the plan); the warning says only that.
    warnings.simplefilter("ignore")
    from langchain.mcp import MCPAdapter

DEMO_DIR = PROJECT_ROOT / "data" / "demo"

# Tools per consumer, as in the table of the plan ("Grafo").
NETWORK_TOOLS = frozenset(
    {
        "list_contacts",
        "network_list_companies",
        "network_company_overview",
        "pending_followups",
        "log_interaction",
        "network_save_person",
        "network_save_company",
    }
)
JOBS_TOOLS = frozenset(
    {
        "list_jobs",
        "jobs_funnel_metrics",
        "pending_followups",
        "daily_summary",
        # Supporting reads from Network (Q3): who of the network is at the company.
        "list_contacts",
        "network_company_overview",
        "add_job",
        "update_job",
        "jobs_add_stage",
        "jobs_link_person",
    }
)
APPROVAL_TOOLS = frozenset({"changes_confirm", "changes_discard"})
DASHBOARD_TOOLS = frozenset({"jobs_funnel_metrics", "pending_followups", "daily_summary"})
# Announced by the server and deliberately given to no one in v0.1.
UNUSED_TOOLS = frozenset({"changes_list_pending"})

AGENT_TOOLS = {"network": NETWORK_TOOLS, "jobs": JOBS_TOOLS}
CLASSIFIED_TOOLS = NETWORK_TOOLS | JOBS_TOOLS | APPROVAL_TOOLS | DASHBOARD_TOOLS | UNUSED_TOOLS


class UnclassifiedToolError(Exception):
    """The server announced a tool that is in no list of this module."""


def server_command(command: str) -> str:
    """Absolute path of the server executable: first next to this Python (the venv), then PATH."""
    found = shutil.which(command, path=str(Path(sys.executable).parent)) or shutil.which(command)
    if found is None:
        raise FileNotFoundError(
            f"Server executable {command!r} not found; install the project with "
            'pip install -e ".[dev]" in this virtual environment'
        )
    return found


def transport(server: Server) -> StdioTransport:
    """Stdio transport whose process lives only while a client context is open."""
    return StdioTransport(
        command=server_command(server.command), args=[], env=server.env(), keep_alive=False
    )


def adapter(server: Server) -> MCPAdapter:
    """Adapter for one turn: keep `async with adapter(...)` open during the turn."""
    return MCPAdapter(transport(server))


def client(server: Server) -> Client:
    """Client for direct calls: `async with client(...) as c: await call(c, ...)`."""
    return Client(transport(server))


async def agent_tools(mcp: MCPAdapter, agent: str) -> list[BaseTool]:
    """The tools of one agent ("network" or "jobs"). Fails on a tool no list classifies."""
    allowed = AGENT_TOOLS[agent]
    tools = await mcp.list_tools()
    unclassified = sorted({tool.name for tool in tools} - CLASSIFIED_TOOLS)
    if unclassified:
        raise UnclassifiedToolError(
            f"Server tools not classified in mcp_client.py: {', '.join(unclassified)}"
        )
    return [tool for tool in tools if tool.name in allowed]


async def call(mcp_client: Client, tool: str, **arguments: Any) -> dict:
    """Direct call without a model; returns the structured content (a business error is an
    object with 'error' and 'detail', returned as is)."""
    result = await mcp_client.call_tool(tool, arguments)
    return result.structured_content


def extract_proposal(message: ToolMessage) -> dict | None:
    """The proposal of a write tool result ({"proposal": {...}}), or None."""
    artifact = message.artifact
    content = artifact.get("structured_content") if isinstance(artifact, dict) else None
    if isinstance(content, dict) and isinstance(content.get("proposal"), dict):
        return content["proposal"]
    return None


def create_demo_db(server: Server, demo_dir: Path = DEMO_DIR) -> str:
    """Create the server database with the synthetic demo data, through the server import.

    Refuses an existing database file, so demo data never goes into a database in use.
    """
    if server.db.exists():
        raise FileExistsError(f"{server.db} already exists; point JOB_SEARCH_DB to a new file")
    server.db.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [server_command(server.command), "import", str(demo_dir), "--apply"],
        # The same variables a server process gets over stdio: safe defaults plus Server.env().
        env=get_default_environment() | server.env(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Demo import failed: {completed.stderr.strip()}")
    return completed.stdout
