# server.py
import os
from dataclasses import dataclass
from typing import Callable

from hyperspell import Hyperspell
from mcp.server.fastmcp import FastMCP

token = os.getenv("HYPERSPELL_TOKEN")

if not token:
    raise ValueError("HYPERSPELL_TOKEN is not set")

# Expose resources or tools?
# Some MCP clients don't support resources well (looking at you, Claude Desktop),
# so we can expose them as tools instead.
resource_types = os.getenv("USE_RESOURCES", "false").lower()
use_tools = resource_types in ("false", "0", "both")
use_resources = resource_types in ("true", "1", "both")

# Create an MCP server
mcp = FastMCP("Hyperspell")
hyperspell = Hyperspell(api_key=token)


def tool_or_resource(uri: str, name: str | None = None):
    def decorator(fn: Callable):
        description = fn.__doc__
        if use_resources:
            mcp.resource(uri, name=name, description=description)(fn)
        if use_tools:
            mcp.add_tool(fn)
        return fn

    return decorator

