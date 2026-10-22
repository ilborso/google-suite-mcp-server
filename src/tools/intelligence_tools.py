"""Intelligence and Market Analysis Tools for Google Suite MCP Server.

Wraps:
- ilborso/google-trending-now
- ilborso/google-trending-historical-data
- ilborso/google-maps-fast-scraper
"""

from __future__ import annotations

import json
from typing import Any

from src.utils.apify_runner import (
    TIMEOUT_AI_TRENDS,
    TIMEOUT_SCRAPING,
    run_actor_with_timeout,
)


def register_intelligence_tools(mcp: Any) -> None:
    """Register intelligence and trends tools with the MCP server instance."""

    @mcp.tool()
    async def google_trending_now(
        geo: str = "US",
        max_items: int = 10,
        hl: str = "en",
        hours: str = "24",
        cat: str = "0",
        sort: str = "relevance",
        status: str = "all",
        ai_marketing_intelligence: bool = False,
    ) -> str:
        """Fetch real-time Google Trending searches with optional Gemini marketing intelligence.

        Powered by the Actor 'ilborso/google-trending-now'.
        Enforces low-latency execution and context trimming.

        Args:
            geo: Two-letter country code for geographic filtering (e.g. 'US', 'IT', 'GB', 'DE', 'FR'). Default is 'US'.
            max_items: Maximum trending topics to return (default: 10 for low latency).
            hl: Language code for the response (default: 'en').
            hours: Timeframe window in hours to look back for trends (e.g. '4', '24', '48'). Default is '24'.
            cat: Category ID to filter trends (use '0' for all categories). Default is '0'.
            sort: Sorting order for trends: 'relevance', 'title', or 'volume'. Default is 'relevance'.
            status: Filter by trend status: 'all', 'active', or 'historical'. Default is 'all'.
            ai_marketing_intelligence: If True, enriches trending results with Gemini AI marketing insights. Default is False.

        Returns:
            JSON formatted string containing real-time trending queries, search volumes, and news headlines.
        """
        run_input = {
            "geo": geo,
            "max_items": max_items,
            "hl": hl,
            "hours": hours,
            "cat": cat,
            "sort": sort,
            "status": status,
            "AI_Marketing_Intelligence": ai_marketing_intelligence,
        }

        result = await run_actor_with_timeout(
            actor_id="ilborso/google-trending-now",
            run_input=run_input,
            timeout_secs=TIMEOUT_AI_TRENDS,
            max_items=max_items,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def google_trending_historical(
        q: str,
        geo: str = "",
        date: str = "today 12-m",
        hl: str = "en",
        data_type: str = "",
        cat: str = "0",
        gprop: str = "",
        region: str = "",
        max_results: int = 10,
    ) -> str:
        """Retrieve historical Google Trends data: interest over time, regional interest, and related queries.

        Powered by the Actor 'ilborso/google-trending-historical-data'.

        Args:
            q: Search keyword to analyze on Google Trends (e.g. 'artificial intelligence', 'bitcoin', 'remote work').
            geo: Location code (e.g. 'US', 'GB', 'IT', 'US-CA'). Defaults to empty for worldwide.
            date: Time range for trends analysis (e.g. 'now 7-d', 'today 1-m', 'today 3-m', 'today 12-m', 'today 5-y'). Default is 'today 12-m'.
            hl: Language code for UI and categories (e.g. 'en', 'it', 'es'). Default is 'en'.
            data_type: Widget filter: 'TIMESERIES', 'GEO_MAP', or empty for both. Default is empty.
            cat: Category ID to narrow results (use '0' for all categories). Default is '0'.
            gprop: Google property to search: '' (Web Search default), 'images', 'news', 'youtube', 'froogle'. Default is empty.
            region: Geo granularity: 'COUNTRY', 'REGION', 'DMA', 'CITY'. Default is empty (auto).
            max_results: Maximum records to return. Default is 10 for low latency.

        Returns:
            JSON formatted string with historical timeline summary, regional interest breakdown, and related queries.
        """
        run_input = {
            "q": q,
            "geo": geo,
            "date": date,
            "hl": hl,
            "data_type": data_type,
            "cat": cat,
            "gprop": gprop,
            "region": region,
            "max_results": max_results,
        }

        result = await run_actor_with_timeout(
            actor_id="ilborso/google-trending-historical-data",
            run_input=run_input,
            timeout_secs=TIMEOUT_AI_TRENDS,
            max_items=max_results,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def google_maps_search(
        search: str,
        max_results: int = 5,
        location_constraint: str | None = None,
        language: str = "en",
        geo_location: str = "us",
        google_domain: str = "google.com",
        place_info: bool = False,
        reviews: bool = False,
        ai_enabled: bool = False,
        ai_prompt: str | None = None,
    ) -> str:
        """Extract Google Maps local business data, contact info, ratings, and locations at high speed.

        Powered by the Actor 'ilborso/google-maps-fast-scraper'.
        Optimized with low-latency defaults (reviews and deep place info disabled by default).

        Args:
            search: Search query for Google Maps (e.g. 'pizza new york', 'hotels milan', 'plumbers near me').
            max_results: Maximum number of Google Maps places to extract. Default is 5 for low latency.
            location_constraint: Precise coordinates & zoom level in '@lat,lng,zoom' format (e.g. '@40.7128,-74.0060,13z').
            language: Language code for results (e.g. 'en', 'it', 'es'). Default is 'en'.
            geo_location: Country code for geolocation (e.g. 'us', 'it', 'de'). Default is 'us'.
            google_domain: Google domain to perform search on (e.g. 'google.com', 'google.it'). Default is 'google.com'.
            place_info: Set True to retrieve enriched place details (menu, popular times). Kept False for low latency.
            reviews: Set True to retrieve user reviews. Kept False for low latency.
            ai_enabled: If True, runs Gemini AI analysis on results using 'ai_prompt'. Default is False.
            ai_prompt: Custom prompt for Gemini AI processing when ai_enabled is True.

        Returns:
            JSON formatted string containing businesses, addresses, phone numbers, ratings, websites, and coordinates.
        """
        run_input = {
            "search": search,
            "max_results": max_results,
            "location_constraint": location_constraint,
            "language": language,
            "geo_location": geo_location,
            "google_domain": google_domain,
            "place_info": place_info,
            "reviews": reviews,
            "ai_enabled": ai_enabled,
            "ai_prompt": ai_prompt,
        }

        result = await run_actor_with_timeout(
            actor_id="ilborso/google-maps-fast-scraper",
            run_input=run_input,
            timeout_secs=TIMEOUT_SCRAPING,
            max_items=max_results,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
