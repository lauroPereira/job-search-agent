"""Tiny MCP server that reports the names of its environment variables (test only)."""

import os

from fastmcp import FastMCP

mcp = FastMCP("env-probe")


@mcp.tool
def environment() -> dict:
    return {"names": sorted(os.environ)}


if __name__ == "__main__":
    mcp.run(transport="stdio", show_banner=False)
