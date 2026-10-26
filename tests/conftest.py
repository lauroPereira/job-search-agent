"""Real job-search-mcp server over stdio, with the synthetic demo data in a temporary database."""

import tomllib
from pathlib import Path

import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding

from job_search_agent.config import PROJECT_ROOT, Server, parse_config
from job_search_agent.knowledge import build_index, knowledge_tool
from job_search_agent.mcp_client import create_demo_db
from job_search_agent.traces import TraceStore


def demo_server(directory: Path) -> Server:
    server = Server(command="job-search-mcp", db=(directory / "job_search.db").resolve())
    create_demo_db(server)
    return server


@pytest.fixture(scope="session")
def server(tmp_path_factory) -> Server:
    """Shared demo database, for tests that only read."""
    return demo_server(tmp_path_factory.mktemp("server"))


@pytest.fixture
def fresh_server(tmp_path) -> Server:
    """A new demo database, for tests that write."""
    return demo_server(tmp_path)


@pytest.fixture
def config(tmp_path: Path):
    """The example configuration, with local paths under tmp_path."""
    data = tomllib.loads((PROJECT_ROOT / "config.example.toml").read_text(encoding="utf-8"))
    data["server"]["JOB_SEARCH_DB"] = str(tmp_path / "job_search.db")
    return parse_config(data, root=tmp_path)


@pytest.fixture(scope="session")
def knowledge():
    """search_knowledge over data/knowledge/ with fake embeddings (no network)."""
    store = build_index(
        PROJECT_ROOT / "data" / "knowledge", DeterministicFakeEmbedding(size=32), ()
    )
    return knowledge_tool(store)


@pytest.fixture
def traces(config) -> TraceStore:
    return TraceStore(config.traces, config.masking_names)
