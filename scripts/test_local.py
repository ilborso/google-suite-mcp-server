"""Test utility script to verify and run MCP tools locally without an external client."""

import argparse
import asyncio
import json
import os
import sys
import time

# Ensure workspace root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure UTF-8 output encoding across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from src.main import create_mcp_server
from src.utils.apify_runner import get_apify_token


TOOL_EXAMPLES: dict[str, str] = {
    "google_search_ai_mode": (
        'python scripts/test_local.py --tool google_search_ai_mode --q "ultime novita intelligenza artificiale"'
    ),
    "google_search_serp": (
        'python scripts/test_local.py --tool google_search_serp --q "migliori smartphone 2026" --max_results 3'
    ),
    "google_news_content_crawler": (
        'python scripts/test_local.py --tool google_news_content_crawler --search_query "Nvidia" --days_back 1 --max_results 2'
    ),
    "google_trending_now": (
        'python scripts/test_local.py --tool google_trending_now --geo IT --max_items 3'
    ),
    "google_trending_historical": (
        'python scripts/test_local.py --tool google_trending_historical --q "bitcoin" --date "today 3-m" --max_results 5'
    ),
    "google_maps_search": (
        'python scripts/test_local.py --tool google_maps_search --search "pizzeria napoli" --max_results 2'
    ),
    "google_flights_search": (
        'python scripts/test_local.py --tool google_flights_search --departure_id FCO --arrival_id JFK --outbound_date 2026-11-20'
    ),
    "google_shopping_search": (
        'python scripts/test_local.py --tool google_shopping_search --query "Sony WH-1000XM5" --max_results 3'
    ),
    "gemini_flash_lite_generate": (
        'python scripts/test_local.py --tool gemini_flash_lite_generate --q "Spiega in 3 punti chiave la relativita ristretta"'
    ),
}


async def list_available_tools(server):
    """Print all registered tools, their parameters, and a dedicated test example for each."""
    tools = await server.list_tools()
    print("\n" + "=" * 70)
    print(f" Registered MCP Tools ({len(tools)} total)")
    print("=" * 70)
    for idx, tool in enumerate(tools, 1):
        print(f"\n[{idx}] {tool.name}")
        desc_first_line = tool.description.strip().split("\n")[0] if tool.description else ""
        print(f"    Description: {desc_first_line}")
        schema = getattr(tool, "inputSchema", getattr(tool, "input_schema", {}))
        required = schema.get("required", [])
        props = schema.get("properties", {})
        print(f"    Required: {required if required else 'None'}")
        print(f"    Available parameters: {list(props.keys())}")
        if tool.name in TOOL_EXAMPLES:
            print(f"    Example: {TOOL_EXAMPLES[tool.name]}")


async def run_tool_test(server, tool_name: str, args_dict: dict):
    """Invoke a specific tool directly and display output and timing."""
    print("\n" + "=" * 70)
    print(f" Executing Tool: {tool_name}")
    print(f" Arguments: {json.dumps(args_dict, indent=2, ensure_ascii=False)}")
    print("=" * 70)

    start_time = time.time()
    try:
        response = await server.call_tool(tool_name, args_dict)
        elapsed = time.time() - start_time
        print(f"\nExecution Time: {elapsed:.2f}s")
        print("\nResponse:")

        # Extract text content from MCP CallToolResult
        contents = getattr(response, "content", response)
        if isinstance(contents, list):
            for item in contents:
                if hasattr(item, "text"):
                    try:
                        parsed = json.loads(item.text)
                        print(json.dumps(parsed, indent=2, ensure_ascii=False))
                    except Exception:
                        print(item.text)
                else:
                    print(item)
        else:
            print(response)

    except Exception as exc:
        print(f"\nError calling tool '{tool_name}': {exc}", file=sys.stderr)


def parse_dynamic_flags(unknown_args: list[str]) -> dict:
    """Parse dynamic CLI flags like --q "something" --max_results 5 into a dict."""
    dynamic_args = {}
    i = 0
    while i < len(unknown_args):
        arg = unknown_args[i]
        if arg.startswith("--"):
            key = arg[2:]
            if i + 1 < len(unknown_args) and not unknown_args[i + 1].startswith("--"):
                val = unknown_args[i + 1]
                # Cast booleans and integers
                if val.lower() == "true":
                    dynamic_args[key] = True
                elif val.lower() == "false":
                    dynamic_args[key] = False
                elif val.isdigit():
                    dynamic_args[key] = int(val)
                else:
                    dynamic_args[key] = val
                i += 2
            else:
                dynamic_args[key] = True
                i += 1
        else:
            i += 1
    return dynamic_args


async def main():
    examples_str = "\n".join(f"  {cmd}" for cmd in TOOL_EXAMPLES.values())
    parser = argparse.ArgumentParser(
        description="Test Google Suite MCP Server Tools locally.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples for all 9 tools:
{examples_str}
""",
    )
    parser.add_argument("--list", action="store_true", help="List all available tools and parameters")
    parser.add_argument("--tool", type=str, help="Name of the tool to test")
    parser.add_argument("--args", type=str, help="Raw JSON string of arguments for the tool")

    parsed_args, unknown_args = parser.parse_known_args()
    token = get_apify_token()

    if not token:
        print("\n[WARNING] 'APIFY_TOKEN' environment variable is NOT set.", file=sys.stderr)
        print("          Live Actor runs will return an AUTHENTICATION_REQUIRED error.", file=sys.stderr)
        print("          Set it via: $env:APIFY_TOKEN=\"your_apify_token\"\n", file=sys.stderr)
    else:
        print(f"\n[INFO] Apify Token detected: {token[:8]}...{token[-4:]}")

    server = create_mcp_server()

    if parsed_args.list or not parsed_args.tool:
        await list_available_tools(server)
        print("\n" + "=" * 70)
        print(" Copy-Paste Examples for All 9 Tools (PowerShell):")
        print("=" * 70)
        for idx, (tool_k, ex_cmd) in enumerate(TOOL_EXAMPLES.items(), 1):
            print(f"\n[{idx}] {tool_k}:")
            print(f"  {ex_cmd}")
        print("\n" + "=" * 70 + "\n")
        return

    # 1. Parse JSON from --args if provided
    args_dict = {}
    if parsed_args.args:
        try:
            args_dict = json.loads(parsed_args.args)
        except json.JSONDecodeError:
            # If PowerShell split the JSON across spaces, try reassembling unknown_args
            combined = " ".join([parsed_args.args] + unknown_args)
            try:
                args_dict = json.loads(combined)
            except json.JSONDecodeError as err:
                print(f"[ERROR] Could not parse JSON in --args: {err}", file=sys.stderr)
                print("Tip: Use direct flags instead, e.g.: --q \"my query\"", file=sys.stderr)
                return

    # 2. Add/merge dynamic command-line flags (e.g. --q "...", --geo "IT", --max_results 5)
    dynamic_flags = parse_dynamic_flags(unknown_args)
    args_dict.update(dynamic_flags)

    await run_tool_test(server, parsed_args.tool, args_dict)


if __name__ == "__main__":
    asyncio.run(main())
