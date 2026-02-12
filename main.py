#!/usr/bin/env python3
"""
Confluence MCP server: create and manage Confluence pages via Confluence REST API v1.

Environment (or .env):
  CONFLUENCE_BASE_URL   Base URL (default: https://wiki.corp.adobe.com)
  CONFLUENCE_API_TOKEN  API token for Bearer auth (required)
  CONFLUENCE_SPACE_KEY  Default space key (optional; can be passed per call)
"""

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from confluence_tools import tools

load_dotenv(override=True)

# Initialize FastMCP server
mcp = FastMCP("confluence-mcp")


def main() -> None:
    for tool in tools:
        mcp.add_tool(tool)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
