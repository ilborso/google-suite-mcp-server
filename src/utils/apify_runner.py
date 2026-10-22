"""Asynchronous Apify Actor Runner with Timeout Enforcement and Payload Trimming.

Handles authentication, Actor lifecycle, low-latency timeout management,
graceful degradation (RUNNING fallback with run_url), and context window optimization.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta
import json
import logging
import os
import sys
from typing import Any, Callable

from apify_client import ApifyClientAsync

# Standardize logging strictly to sys.stderr so MCP JSON-RPC on sys.stdout is never corrupted
logger = logging.getLogger("google_suite_mcp.runner")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        logging.Formatter("[%(asctime)s] [%(levelname)s] [ApifyRunner] %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Configurable timeout constants in seconds (increased to 50s)
TIMEOUT_SCRAPING: int = 50
TIMEOUT_AI_TRENDS: int = 50

# Internal global token cache if set via Actor input or programmatic config
_GLOBAL_APIFY_TOKEN: str | None = None


def set_apify_token(token: str | None) -> None:
    """Set or override the global Apify authentication token."""
    global _GLOBAL_APIFY_TOKEN
    if token and token.strip():
        _GLOBAL_APIFY_TOKEN = token.strip()
        logger.info("Apify API token updated from configuration.")


def get_apify_token() -> str | None:
    """Retrieve Apify API token from runtime configuration or environment."""
    if _GLOBAL_APIFY_TOKEN:
        return _GLOBAL_APIFY_TOKEN
    env_token = os.environ.get("APIFY_TOKEN")
    if env_token and env_token.strip():
        return env_token.strip()
    return None


def truncate_text(text: Any, max_len: int = 500) -> Any:
    """Truncate long text fields to conserve LLM context window tokens."""
    if isinstance(text, str) and len(text) > max_len:
        return text[:max_len] + "... [truncated]"
    return text


# -----------------------------------------------------------------------------
# Semantic Dataset Trimmers
# -----------------------------------------------------------------------------


def trim_google_search_ai(item: dict[str, Any]) -> dict[str, Any]:
    """Trim output from ilborso/google-search-ai-mode."""
    trimmed: dict[str, Any] = {}

    if "q" in item:
        trimmed["query"] = item["q"]
    elif "query" in item:
        trimmed["query"] = item["query"]

    # AI overview / summary
    for key in ("ai_overview", "text_blocks", "answer", "summary", "text"):
        if key in item and item[key]:
            trimmed["ai_overview"] = truncate_text(item[key], max_len=1500)
            break

    # References / Sources
    sources_raw = item.get("sources") or item.get("references") or item.get("citations") or []
    if isinstance(sources_raw, list):
        trimmed_sources = []
        for s in sources_raw[:6]:
            if isinstance(s, dict):
                trimmed_sources.append({
                    "title": truncate_text(s.get("title", ""), max_len=120),
                    "url": s.get("url") or s.get("link"),
                    "snippet": truncate_text(s.get("snippet", "") or s.get("text", ""), max_len=250),
                })
        if trimmed_sources:
            trimmed["sources"] = trimmed_sources

    # Shopping results if present
    shopping_raw = item.get("shopping_results") or item.get("shopping") or []
    if isinstance(shopping_raw, list):
        trimmed_shopping = []
        for p in shopping_raw[:4]:
            if isinstance(p, dict):
                trimmed_shopping.append({
                    "title": truncate_text(p.get("title", ""), max_len=100),
                    "price": p.get("price"),
                    "merchant": p.get("merchant") or p.get("source"),
                    "url": p.get("url") or p.get("link"),
                })
        if trimmed_shopping:
            trimmed["shopping_results"] = trimmed_shopping

    return trimmed or {k: truncate_text(v, max_len=300) for k, v in item.items() if k != "html"}


def trim_google_search_serp(item: dict[str, Any]) -> dict[str, Any]:
    """Trim output from ilborso/google-search-fast-complete-result."""
    trimmed: dict[str, Any] = {}

    if "search_parameters" in item:
        params = item["search_parameters"]
        trimmed["query"] = params.get("q")
        trimmed["country"] = params.get("gl")
        trimmed["language"] = params.get("hl")

    # AI Overview if present in SERP
    if item.get("ai_overview"):
        trimmed["ai_overview"] = truncate_text(item["ai_overview"], max_len=1200)

    # Knowledge Graph
    kg = item.get("knowledge_graph")
    if isinstance(kg, dict):
        trimmed["knowledge_graph"] = {
            "title": kg.get("title"),
            "type": kg.get("type"),
            "description": truncate_text(kg.get("description"), max_len=400),
            "attributes": kg.get("attributes"),
            "website": kg.get("website"),
        }

    # Organic Results (limited to top 5)
    organic = item.get("organic_results") or item.get("results") or []
    if isinstance(organic, list):
        trimmed_organic = []
        for res in organic[:5]:
            if isinstance(res, dict):
                trimmed_organic.append({
                    "position": res.get("position"),
                    "title": truncate_text(res.get("title"), max_len=120),
                    "url": res.get("url") or res.get("link"),
                    "snippet": truncate_text(res.get("snippet") or res.get("description"), max_len=300),
                })
        trimmed["organic_results"] = trimmed_organic

    # People Also Ask
    paa = item.get("people_also_ask") or item.get("related_questions") or []
    if isinstance(paa, list):
        trimmed_paa = []
        for q in paa[:4]:
            if isinstance(q, dict):
                trimmed_paa.append({
                    "question": q.get("question"),
                    "snippet": truncate_text(q.get("snippet") or q.get("answer"), max_len=200),
                })
        if trimmed_paa:
            trimmed["people_also_ask"] = trimmed_paa

    # Top Stories / News
    news = item.get("top_stories") or item.get("news") or []
    if isinstance(news, list):
        trimmed_news = []
        for n in news[:3]:
            if isinstance(n, dict):
                trimmed_news.append({
                    "title": truncate_text(n.get("title"), max_len=100),
                    "source": n.get("source"),
                    "url": n.get("url") or n.get("link"),
                    "date": n.get("date"),
                })
        if trimmed_news:
            trimmed["top_stories"] = trimmed_news

    return trimmed or {k: truncate_text(v, max_len=300) for k, v in item.items() if k != "html"}


def trim_google_maps(item: dict[str, Any]) -> dict[str, Any]:
    """Trim output from ilborso/google-maps-fast-scraper."""
    return {
        "title": item.get("title") or item.get("name"),
        "category": item.get("category") or item.get("category_name"),
        "address": item.get("address"),
        "phone": item.get("phone") or item.get("phone_number"),
        "website": item.get("website") or item.get("url"),
        "rating": item.get("rating") or item.get("total_score"),
        "reviews_count": item.get("reviews_count") or item.get("reviews"),
        "price_level": item.get("price_level"),
        "location": {
            "lat": item.get("latitude") or item.get("lat"),
            "lng": item.get("longitude") or item.get("lng"),
        } if (item.get("latitude") or item.get("lat")) else None,
        "hours": item.get("hours") or item.get("popular_times"),
        "ai_analysis": truncate_text(item.get("ai_analysis"), max_len=800) if item.get("ai_analysis") else None,
    }


def trim_google_flights(item: dict[str, Any]) -> dict[str, Any]:
    """Trim output from ilborso/google-flights-api."""
    return {
        "airline": item.get("airline") or item.get("airline_name") or item.get("name"),
        "flight_number": item.get("flight_number") or item.get("flight_no"),
        "price": item.get("price") or item.get("price_raw"),
        "departure_airport": item.get("departure_airport") or item.get("origin"),
        "departure_time": item.get("departure_time") or item.get("departure"),
        "arrival_airport": item.get("arrival_airport") or item.get("destination"),
        "arrival_time": item.get("arrival_time") or item.get("arrival"),
        "duration": item.get("duration") or item.get("flight_duration"),
        "stops": item.get("stops") or item.get("layovers"),
        "carbon_emissions": item.get("carbon_emissions"),
        "booking_token": item.get("booking_token"),
        "booking_url": item.get("booking_url") or item.get("url"),
    }


def trim_google_shopping(item: dict[str, Any]) -> dict[str, Any]:
    """Trim output from ilborso/google-shopping-now."""
    return {
        "title": truncate_text(item.get("title") or item.get("name"), max_len=140),
        "price": item.get("price") or item.get("extracted_price"),
        "currency": item.get("currency"),
        "seller": item.get("seller") or item.get("merchant") or item.get("source"),
        "rating": item.get("rating"),
        "reviews_count": item.get("reviews_count") or item.get("reviews"),
        "free_shipping": item.get("free_shipping"),
        "on_sale": item.get("on_sale"),
        "url": item.get("url") or item.get("link"),
        "snippet": truncate_text(item.get("snippet") or item.get("description"), max_len=200),
    }


def trim_google_trending_now(item: dict[str, Any]) -> dict[str, Any]:
    """Trim output from ilborso/google-trending-now."""
    trimmed: dict[str, Any] = {
        "query": item.get("query") or item.get("trend_name") or item.get("title"),
        "search_volume": item.get("search_volume") or item.get("volume"),
        "status": item.get("status"),
        "trend_sparkline": item.get("trend_sparkline") or item.get("sparkline"),
    }

    ai_intel = item.get("AI_Marketing_Intelligence") or item.get("ai_marketing_intelligence")
    if ai_intel:
        trimmed["marketing_intelligence"] = truncate_text(ai_intel, max_len=1000)

    news = item.get("news_articles") or item.get("articles") or []
    if isinstance(news, list):
        trimmed_news = []
        for article in news[:2]:
            if isinstance(article, dict):
                trimmed_news.append({
                    "title": truncate_text(article.get("title"), max_len=100),
                    "source": article.get("source"),
                    "url": article.get("url") or article.get("link"),
                })
        if trimmed_news:
            trimmed["news_articles"] = trimmed_news

    return trimmed


def trim_google_trending_historical(item: dict[str, Any]) -> dict[str, Any]:
    """Trim output from ilborso/google-trending-historical-data."""
    trimmed: dict[str, Any] = {
        "keyword": item.get("keyword") or item.get("query") or item.get("q"),
        "time_range": item.get("time_range") or item.get("date"),
        "geo": item.get("geo"),
    }

    # Interest over time (summarize or take latest/peak)
    iot = item.get("interest_over_time") or item.get("timeline_data")
    if isinstance(iot, list):
        if len(iot) > 10:
            # Provide first, middle, last and peak to save context
            peak = max(iot, key=lambda x: x.get("value", 0) if isinstance(x, dict) else 0)
            trimmed["interest_over_time_sample"] = [iot[0], peak, iot[-1]]
            trimmed["interest_over_time_total_points"] = len(iot)
        else:
            trimmed["interest_over_time"] = iot

    # Regional interest
    by_region = item.get("interest_by_region") or item.get("geo_map")
    if isinstance(by_region, list):
        trimmed["top_regions"] = by_region[:5]

    # Related queries
    related_q = item.get("related_queries") or item.get("queries")
    if isinstance(related_q, list):
        trimmed["related_queries"] = related_q[:5]

    return trimmed


def trim_gemini_flash_lite(item: dict[str, Any]) -> dict[str, Any]:
    """Trim output from ilborso/gemini-flash-lite-latest."""
    return {
        "prompt": truncate_text(item.get("q") or item.get("prompt"), max_len=200),
        "response": item.get("response") or item.get("text") or item.get("output") or item.get("content"),
        "model": item.get("model") or "gemini-flash-lite",
        "finish_reason": item.get("finish_reason"),
        "usage": item.get("usage"),
    }


def trim_ai_news_content(item: dict[str, Any]) -> dict[str, Any]:
    """Trim output from ilborso/ai-news-content-crawler."""
    content = item.get("text") or item.get("snippet")
    return {
        "title": item.get("title"),
        "source": item.get("domain") or item.get("source"),
        "url": item.get("url"),
        "date": item.get("published"),
        "snippet": item.get("snippet"),
        "topic": item.get("topic") if item.get("topic") != "DO_NOT_USE_TOPIC" else None,
        "text": truncate_text(content, max_len=1200) if content else None,
    }


def generic_trimmer(item: dict[str, Any]) -> dict[str, Any]:
    """Fallback trimmer for unmapped schemas."""
    cleaned = {}
    for k, v in item.items():
        if k in ("html", "rawHtml", "screenshot", "debug"):
            continue
        if v is not None:
            cleaned[k] = truncate_text(v, max_len=350)
    return cleaned


TRIMMER_MAP: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "ilborso/google-search-ai-mode": trim_google_search_ai,
    "ilborso/google-search-fast-complete-result": trim_google_search_serp,
    "ilborso/ai-news-content-crawler": trim_ai_news_content,
    "ilborso/google-maps-fast-scraper": trim_google_maps,
    "ilborso/google-flights-api": trim_google_flights,
    "ilborso/google-shopping-now": trim_google_shopping,
    "ilborso/google-trending-now": trim_google_trending_now,
    "ilborso/google-trending-historical-data": trim_google_trending_historical,
    "ilborso/gemini-flash-lite-latest": trim_gemini_flash_lite,
}


# -----------------------------------------------------------------------------
# Core Asynchronous Execution Engine
# -----------------------------------------------------------------------------


def _get_obj_field(obj: Any, *keys: str) -> Any:
    """Safely retrieve a field from either a dict or a Pydantic/dataclass object."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        for k in keys:
            if k in obj and obj[k] is not None:
                return obj[k]
    for k in keys:
        if hasattr(obj, k):
            val = getattr(obj, k)
            if val is not None:
                return val
    return None


async def run_actor_with_timeout(
    actor_id: str,
    run_input: dict[str, Any],
    timeout_secs: int = TIMEOUT_SCRAPING,
    max_items: int = 5,
) -> dict[str, Any]:
    """Run an Apify Actor asynchronously with timeout enforcement and payload trimming.

    Args:
        actor_id: Target Apify Actor ID (e.g., 'ilborso/google-maps-fast-scraper').
        run_input: Input dictionary configured for the Actor.
        timeout_secs: Max seconds to wait for run completion before graceful degradation.
        max_items: Maximum dataset items to return.

    Returns:
        Structured response dictionary containing status, data/error, and metadata.
    """
    token = get_apify_token()
    if not token:
        logger.error("Execution failed: Missing Apify API token.")
        return {
            "status": "ERROR",
            "error": "AUTHENTICATION_REQUIRED",
            "message": (
                "Apify API token is not configured. Please supply 'apifyToken' in the Actor input "
                "or set the 'APIFY_TOKEN' environment variable. "
                "You can generate a token at https://console.apify.com/account/integrations"
            ),
        }

    # Filter out None/empty values from run_input to let Actor defaults kick in cleanly
    clean_input = {k: v for k, v in run_input.items() if v is not None}

    client = ApifyClientAsync(token=token)
    run_id: str | None = None
    run_url: str | None = None

    try:
        logger.info(f"Starting Actor '{actor_id}' (timeout: {timeout_secs}s)...")
        # Start the run asynchronously to immediately secure the run ID and tracking URL
        actor_client = client.actor(actor_id)
        started_run = await actor_client.start(run_input=clean_input)

        run_id = _get_obj_field(started_run, "id")
        run_url = f"https://console.apify.com/view/runs/{run_id}" if run_id else None
        logger.info(f"Actor '{actor_id}' run started: {run_id} -> {run_url}")

        # Wait for completion within the strict low-latency deadline
        try:
            finished_run = await asyncio.wait_for(
                client.run(run_id).wait_for_finish(wait_duration=timedelta(seconds=timeout_secs)),
                timeout=float(timeout_secs),
            )
        except (asyncio.TimeoutError, TimeoutError):
            logger.warning(f"Actor '{actor_id}' run {run_id} exceeded timeout of {timeout_secs}s.")
            return {
                "status": "RUNNING",
                "actor_id": actor_id,
                "run_id": run_id,
                "run_url": run_url,
                "message": (
                    f"Execution exceeded the strict low-latency timeout of {timeout_secs} seconds. "
                    "The scraper task is still executing safely in the background on Apify. "
                    f"The user can track its live progress or download results once finished at: {run_url}"
                ),
            }

        if not finished_run:
            return {
                "status": "RUNNING",
                "actor_id": actor_id,
                "run_id": run_id,
                "run_url": run_url,
                "message": f"Actor run is currently in progress. Track live status at {run_url}",
            }

        run_status = _get_obj_field(finished_run, "status")
        logger.info(f"Actor '{actor_id}' run {run_id} finished with status: {run_status}")

        if run_status != "SUCCEEDED":
            return {
                "status": run_status or "FAILED",
                "actor_id": actor_id,
                "run_id": run_id,
                "run_url": run_url,
                "message": (
                    f"Actor execution completed with status '{run_status}'. "
                    f"Inspect detailed execution logs at {run_url}"
                ),
            }

        # Fetch and trim dataset records
        dataset_id = _get_obj_field(finished_run, "default_dataset_id", "defaultDatasetId")
        if not dataset_id:
            return {
                "status": "SUCCEEDED",
                "actor_id": actor_id,
                "run_id": run_id,
                "run_url": run_url,
                "total_items": 0,
                "data": [],
            }

        dataset_client = client.dataset(dataset_id)
        items_page = await dataset_client.list_items(limit=max_items)
        raw_items = items_page.items

        trimmer = TRIMMER_MAP.get(actor_id, generic_trimmer)
        trimmed_items: list[dict[str, Any]] = []

        for item in raw_items:
            if isinstance(item, dict):
                trimmed_items.append(trimmer(item))
            else:
                trimmed_items.append({"value": item})

        return {
            "status": "SUCCEEDED",
            "actor_id": actor_id,
            "run_id": run_id,
            "run_url": run_url,
            "total_items": len(trimmed_items),
            "data": trimmed_items,
        }

    except Exception as exc:
        logger.exception(f"Unexpected error executing Actor '{actor_id}': {exc}")
        return {
            "status": "ERROR",
            "actor_id": actor_id,
            "run_id": run_id,
            "run_url": run_url,
            "error": exc.__class__.__name__,
            "message": str(exc),
        }
