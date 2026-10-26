"""Command line entry point (`job-search-agent`). The subcommands come in later tasks."""

import argparse

from job_search_agent import __version__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="job-search-agent",
        description="Career agent over the job-search-mcp server.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.parse_args(argv)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
