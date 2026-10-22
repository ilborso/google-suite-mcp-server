"""AI Generation and Reasoning Tools for Google Suite MCP Server.

Wraps:
- ilborso/gemini-flash-lite-latest
"""

from __future__ import annotations

import json
from typing import Any

from src.utils.apify_runner import TIMEOUT_AI_TRENDS, run_actor_with_timeout


def register_ai_tools(mcp: Any) -> None:
    """Register AI processing tools with the MCP server instance."""

    @mcp.tool()
    async def gemini_flash_lite_generate(
        q: str,
        attachments: list[str] | None = None,
    ) -> str:
        """Process prompts, summarize content, or extract structured data using Google Gemini Flash Lite.

        Powered by the Actor 'ilborso/gemini-flash-lite-latest'.
        Engineered for ultra-fast response times in agentic workflows.

        Args:
            q: The text prompt, instructions, or document content to process with Gemini Flash Lite.
            attachments: Optional list of public file URLs (images, PDFs, audio, documents), Data URIs, or Base64 strings.

        Returns:
            JSON formatted string containing generated text response, model information, and token usage.
        """
        run_input = {
            "q": q,
            "attachments": attachments,
        }

        result = await run_actor_with_timeout(
            actor_id="ilborso/gemini-flash-lite-latest",
            run_input=run_input,
            timeout_secs=TIMEOUT_AI_TRENDS,
            max_items=1,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
