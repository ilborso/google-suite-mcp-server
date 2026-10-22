"""Search and News Tools for Google Suite MCP Server.

Wraps:
- ilborso/google-search-ai-mode
- ilborso/google-search-fast-complete-result
- ilborso/ai-news-content-crawler
"""

from __future__ import annotations

import json
from typing import Any

from src.utils.apify_runner import TIMEOUT_SCRAPING, run_actor_with_timeout


def register_search_tools(mcp: Any) -> None:
    """Register search tools with the MCP server instance."""

    @mcp.tool()
    async def google_search_ai_mode(
        q: str,
        gl: str = "us",
        hl: str = "en",
        device: str = "desktop",
        location: str | None = None,
        google_domain: str = "google.com",
        safe: str | None = None,
        max_results: int = 5,
    ) -> str:
        """Fetch AI-generated answers, synthesized text overviews, and source references from Google AI Mode.

        Powered by the Actor 'ilborso/google-search-ai-mode'.
        Enforces low-latency execution and structured context trimming (HTML stripped).

        Args:
            q: Search query to ask Google AI Mode (e.g. 'best noise cancelling headphones 2026', 'how does quantum computing work').
            gl: Country perspective ISO 3166-1 alpha-2 code (e.g. 'us', 'it', 'uk', 'de'). Default is 'us'.
            hl: UI & language ISO 639-1 code (e.g. 'en', 'it', 'es', 'fr'). Default is 'en'.
            device: Device layout format: 'desktop' or 'mobile'. Default is 'desktop'.
            location: Canonical location string (e.g. 'New York,New York,United States').
            google_domain: Google domain to query (e.g. 'google.com', 'google.it'). Default is 'google.com'.
            safe: Set to 'active' to enforce SafeSearch adult filtering. Default is None.
            max_results: Maximum source/shopping items to return (default: 5 for low latency).

        Returns:
            JSON formatted string containing AI synthesized answer, cited sources, and shopping references.
        """
        run_input = {
            "q": q,
            "gl": gl,
            "hl": hl,
            "device": device,
            "location": location,
            "google_domain": google_domain,
            "safe": safe,
            "include_html": False,  # Strict low-latency context protection
        }

        result = await run_actor_with_timeout(
            actor_id="ilborso/google-search-ai-mode",
            run_input=run_input,
            timeout_secs=TIMEOUT_SCRAPING,
            max_items=max_results,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def google_search_serp(
        q: str,
        max_page: int = 1,
        page_start: int = 1,
        gl: str = "us",
        hl: str = "en",
        device: str = "desktop",
        google_domain: str = "google.com",
        location: str | None = None,
        time_period: str | None = None,
        safe: str | None = None,
        max_results: int = 5,
    ) -> str:
        """Extract structured real-time Google Search Engine Results Pages (SERP).

        Powered by the Actor 'ilborso/google-search-fast-complete-result'.
        Retrieves organic rankings, Knowledge Graph cards, People Also Ask questions,
        and Top Stories without heavyweight HTML payloads.

        Args:
            q: The search query string (e.g. 'latest AI news', 'best mechanical keyboards').
            max_page: Maximum page number to retrieve. Default is 1 for low latency.
            page_start: The page number to retrieve (default is 1).
            gl: Country perspective (e.g. 'us', 'it', 'de', 'gb'). Default is 'us'.
            hl: Host language code (e.g. 'en', 'it', 'es'). Default is 'en'.
            device: Device layout: 'desktop' or 'mobile'. Default is 'desktop'.
            google_domain: Google domain (e.g. 'google.com', 'google.it'). Default is 'google.com'.
            location: Canonical city or region (e.g. 'San Francisco,California,United States').
            time_period: Recency filter (e.g. 'last_hour', 'last_day', 'last_week', 'last_month', 'last_year').
            safe: Send 'active' to filter adult content. Default is None.
            max_results: Maximum organic results to return in the response. Default is 5.

        Returns:
            JSON formatted string containing organic search results, Knowledge Graph, and PAA queries.
        """
        run_input = {
            "q": q,
            "max_page": max_page,
            "page_start": page_start,
            "gl": gl,
            "hl": hl,
            "device": device,
            "google_domain": google_domain,
            "location": location,
            "time_period": time_period,
            "safe": safe,
            "include_html": False,  # Strict low-latency context protection
        }

        result = await run_actor_with_timeout(
            actor_id="ilborso/google-search-fast-complete-result",
            run_input=run_input,
            timeout_secs=TIMEOUT_SCRAPING,
            max_items=max_results,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def google_news_content_crawler(
        search_query: str | None = None,
        topic: str = "DO_NOT_USE_TOPIC",
        language_region: str = "IT:it",
        days_back: int = 3,
        max_sites: int = 5,
        max_results: int = 5,
    ) -> str:
        """Extract clean, full-text news articles and content from Google News without paywalls or subscriptions.

        Powered by the Actor 'ilborso/ai-news-content-crawler'.
        Retrieves real-time plain text news articles to keep AI agents updated with the latest events.
        Provide either 'search_query' (keywords) or a predefined 'topic'.

        Args:
            search_query: Search keywords or query for Google News (e.g. 'Intelligenza Artificiale', 'Nvidia', 'SpaceX').
            topic: Predefined Google News topic: 'WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH', or 'DO_NOT_USE_TOPIC'. Default is 'DO_NOT_USE_TOPIC'.
            language_region: Country/language code pair (e.g. 'IT:it', 'US:en', 'GB:en', 'DE:de', 'FR:fr'). Default is 'IT:it'.
            days_back: Number of days back to search (e.g. 1 to 7). Default is 3 for recent breaking news.
            max_sites: Maximum number of unique news sites to crawl. Default is 5 for low latency.
            max_results: Maximum articles to return in the response. Default is 5.

        Returns:
            JSON formatted string containing article titles, publishers, URLs, publication dates, and clean extracted article texts.
        """
        run_input: dict[str, Any] = {
            "languageAndRegion": [language_region] if isinstance(language_region, str) else language_region,
            "daysBack": days_back,
            "maxSites": max_sites,
            "maxConcurrency": 10,
            "decodeInterval": 1,
        }
        if search_query:
            run_input["searchQuery"] = search_query
            run_input["topic"] = "DO_NOT_USE_TOPIC"
        elif topic and topic != "DO_NOT_USE_TOPIC":
            run_input["topic"] = topic
        else:
            # Default to TECHNOLOGY topic if neither is provided
            run_input["topic"] = "TECHNOLOGY"

        result = await run_actor_with_timeout(
            actor_id="ilborso/ai-news-content-crawler",
            run_input=run_input,
            timeout_secs=TIMEOUT_SCRAPING,
            max_items=max_results,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
