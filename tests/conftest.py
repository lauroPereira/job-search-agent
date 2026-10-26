"""Real job-search-mcp server over stdio, with the synthetic demo data in a temporary database."""

from pathlib import Path

import pytest

from job_search_agent.config import Server
from job_search_agent.mcp_client import create_demo_db


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
