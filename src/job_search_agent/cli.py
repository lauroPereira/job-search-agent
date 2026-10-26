"""Command line entry point (`job-search-agent`)."""

import argparse
import os
import sys

from job_search_agent import __version__
from job_search_agent.config import ConfigError, load_config


def demo_db() -> int:
    """Create the server database of config.toml with the synthetic demo data (data/demo/)."""
    from job_search_agent.mcp_client import create_demo_db

    try:
        server = load_config().server
        print(create_demo_db(server))
    except (ConfigError, FileExistsError, FileNotFoundError, RuntimeError) as failure:
        print(failure, file=sys.stderr)
        return 1
    print(f"Demo database created at {server.db}.")
    return 0


def index() -> int:
    """Build the knowledge index (data/knowledge/) with the configured embeddings (OpenAI)."""
    from job_search_agent.knowledge import build_index, save_index
    from job_search_agent.llm import embeddings

    try:
        config = load_config()
    except ConfigError as failure:
        print(failure, file=sys.stderr)
        return 1
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set (put it in .env); index not built.", file=sys.stderr)
        return 2
    try:
        store = build_index(config.knowledge_dir, embeddings(config), config.masking_names)
    except (FileNotFoundError, ValueError) as failure:
        print(failure, file=sys.stderr)
        return 1
    save_index(store, config.knowledge_index)
    print(f"Indexed {len(store.store)} masked chunks into {config.knowledge_index}.")
    # The embeddings response through LangChain carries no usage.
    print("tokens de embeddings: desconhecidos")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="job-search-agent",
        description="Career agent over the job-search-mcp server.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command")
    commands.add_parser(
        "demo-db", help="create the server database (JOB_SEARCH_DB) with the synthetic demo data"
    )
    commands.add_parser(
        "index", help="index data/knowledge/ (masked) with the OpenAI embeddings; needs the key"
    )
    arguments = parser.parse_args(argv)
    if arguments.command == "demo-db":
        return demo_db()
    if arguments.command == "index":
        return index()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
