"""Main entry point for Google Suite MCP Server Actor.

Supports stdio transport (default for Claude Desktop, Cursor, and CLI agentic frameworks)
as well as HTTP/SSE transport (for hosted Apify Standby containers and remote web connections).
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys

from apify import Actor

from src.tools import register_all_tools
from src.utils.apify_runner import set_apify_token

# Compatibility import for mcp 2.x and 1.x
try:
    from mcp.server.mcpserver import MCPServer as FastMCP
except ImportError:
    from mcp.server.fastmcp import FastMCP  # type: ignore

# Configure logging strictly to sys.stderr to protect MCP stdio JSON-RPC protocol
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
)
logger = logging.getLogger("google_suite_mcp")


def create_mcp_server() -> FastMCP:
    """Instantiate and configure the FastMCP server instance."""
    server = FastMCP(
        "google-suite-mcp-server",
        instructions=(
            "Google Suite MCP Server exposing 9 specialized Google scrapers, intelligence tools, "
            "Google News content extractor, and Gemini Flash Lite developed by ilborso. "
            "Designed for high reliability, low-latency timeouts (50s across all tools), "
            "and optimized LLM context window payloads."
        ),
    )
    register_all_tools(server)
    return server


async def load_actor_input() -> dict:
    """Load configuration from Apify Actor Key-Value store if running in an Actor environment."""
    if Actor.is_at_home() or os.environ.get("APIFY_LOCAL_STORAGE_DIR") or os.environ.get("APIFY_TOKEN"):
        try:
            actor_input = await Actor.get_input()
            if isinstance(actor_input, dict):
                return actor_input
        except Exception as e:
            logger.debug(f"No Actor input found or failed to read input: {e}")
    return {}


async def main_async() -> None:
    """Async main routine to parse configuration, initialize Apify context, and run the server."""
    parser = argparse.ArgumentParser(
        description="Google Suite MCP Server - Powered by ilborso Apify Actors"
    )
    is_standby = bool(os.environ.get("ACTOR_STANDBY") or os.environ.get("ACTOR_WEB_SERVER_PORT"))
    default_transport = "sse" if is_standby else "stdio"
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse", "streamable-http"],
        default=os.environ.get("MCP_TRANSPORT", default_transport),
        help=f"MCP transport protocol (default: {default_transport})",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Host interface for SSE/HTTP modes (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("ACTOR_WEB_SERVER_PORT", os.environ.get("PORT", "8080"))),
        help="Port to bind in SSE/HTTP modes (default: 8080)",
    )

    args, _ = parser.parse_known_args()

    # Load Actor input if available
    actor_input = await load_actor_input()

    # Configure authentication token with priority: Actor input -> Environment variable
    token = actor_input.get("apifyToken")
    if token:
        set_apify_token(token)

    transport = actor_input.get("transport", args.transport)
    host = actor_input.get("host", args.host)
    port = int(actor_input.get("port", args.port))

    server = create_mcp_server()

    logger.info(
        f"Starting Google Suite MCP Server with transport='{transport}' on {host}:{port}..."
    )

    if transport == "stdio":
        # Stdio transport handles asynchronous standard I/O streams
        if hasattr(server, "run_stdio_async"):
            await server.run_stdio_async()
        else:
            server.run(transport="stdio")
    elif transport == "sse":
        if hasattr(server, "run_sse_async"):
            await server.run_sse_async(host=host, port=port)
        else:
            server.run(transport="sse", host=host, port=port)
    elif transport == "streamable-http":
        if hasattr(server, "run_streamable_http_async"):
            await server.run_streamable_http_async(host=host, port=port)
        else:
            server.run(transport="streamable-http", host=host, port=port)
    else:
        raise ValueError(f"Unsupported MCP transport: {transport}")


def main() -> None:
    """Synchronous entry point."""
    try:
        asyncio.run(main_async())
    except (KeyboardInterrupt, SystemExit):
        logger.info("MCP server stopped.")


if __name__ == "__main__":
    main()
