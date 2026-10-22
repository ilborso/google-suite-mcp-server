"""Tools collection for Google Suite MCP Server.

Exports modular tool registration functions for all 8 ilborso Apify Actors.
"""

from __future__ import annotations

from typing import Any

from .ai_tools import register_ai_tools
from .commerce_tools import register_commerce_tools
from .intelligence_tools import register_intelligence_tools
from .search_tools import register_search_tools


def register_all_tools(mcp: Any) -> None:
    """Register all 8 ilborso Google Suite tools with the given MCP server instance."""
    register_search_tools(mcp)
    register_intelligence_tools(mcp)
    register_commerce_tools(mcp)
    register_ai_tools(mcp)


__all__ = [
    "register_all_tools",
    "register_search_tools",
    "register_intelligence_tools",
    "register_commerce_tools",
    "register_ai_tools",
]
