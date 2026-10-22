"""Commerce and Travel Tools for Google Suite MCP Server.

Wraps:
- ilborso/google-flights-api
- ilborso/google-shopping-now
"""

from __future__ import annotations

import json
from typing import Any

from src.utils.apify_runner import TIMEOUT_SCRAPING, run_actor_with_timeout


def register_commerce_tools(mcp: Any) -> None:
    """Register commerce and flight tools with the MCP server instance."""

    @mcp.tool()
    async def google_flights_search(
        departure_id: str,
        arrival_id: str,
        outbound_date: str,
        return_date: str | None = None,
        type: str | None = None,
        adults: int = 1,
        travel_class: str = "1",
        stops: str = "0",
        currency: str = "USD",
        hl: str = "en",
        gl: str = "us",
        max_results: int = 5,
    ) -> str:
        """Search Google Flights for real-time fares, schedules, airlines, durations, and layovers.

        Powered by the Actor 'ilborso/google-flights-api'.
        Trims heavy internal data to preserve LLM context window.

        Args:
            departure_id: Origin IATA airport code or comma-separated list (e.g. 'JFK', 'JFK,LGA,EWR', 'MXP').
            arrival_id: Destination IATA airport code (e.g. 'LHR', 'CDG', 'HND').
            outbound_date: Departure date in YYYY-MM-DD format (must be today or a future date).
            return_date: Optional return date in YYYY-MM-DD format (required for round trips).
            type: Trip type: '1' for round-trip, '2' for one-way. Auto-inferred from return_date if omitted.
            adults: Number of adult passengers (1-9). Default is 1.
            travel_class: Cabin class: '1' Economy, '2' Premium Economy, '3' Business, '4' First. Default is '1'.
            stops: Maximum stops filter: '0' Any number of stops, '1' Non-stop only, '2' 1 stop or fewer, '3' 2 stops or fewer. Default is '0'.
            currency: Currency code for prices (e.g. 'USD', 'EUR', 'GBP'). Default is 'USD'.
            hl: Language code for results (default: 'en').
            gl: Country code for regional pricing (default: 'us').
            max_results: Maximum flight itineraries to return. Default is 5 for low latency.

        Returns:
            JSON formatted string containing airlines, flight numbers, departure/arrival times, durations, prices, and booking links.
        """
        run_input = {
            "departure_id": departure_id,
            "arrival_id": arrival_id,
            "outbound_date": outbound_date,
            "return_date": return_date,
            "type": type,
            "adults": adults,
            "travel_class": travel_class,
            "stops": stops,
            "currency": currency,
            "hl": hl,
            "gl": gl,
            "show_hidden": False,  # Strict low-latency context protection
        }

        result = await run_actor_with_timeout(
            actor_id="ilborso/google-flights-api",
            run_input=run_input,
            timeout_secs=TIMEOUT_SCRAPING,
            max_items=max_results,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)

    @mcp.tool()
    async def google_shopping_search(
        query: str,
        max_results: int = 10,
        min_price: int | None = None,
        max_price: int | None = None,
        free_shipping: bool = False,
        on_sale: bool = False,
        sort_by: str | None = None,
        hl: str = "en",
        gl: str = "us",
        google_domain: str = "google.com",
    ) -> str:
        """Search Google Shopping for real-time product prices, sellers, discounts, and reviews.

        Powered by the Actor 'ilborso/google-shopping-now'.
        Trims unstructured descriptions and cleans price/seller fields.

        Args:
            query: Product search query (e.g. 'Sony WH-1000XM5', 'mechanical gaming keyboard').
            max_results: Maximum number of products to return (default: 10 for low latency).
            min_price: Minimum price filter in the target currency.
            max_price: Maximum price filter in the target currency.
            free_shipping: When True, only returns products offering free shipping. Default is False.
            on_sale: When True, only returns products currently on sale or discounted. Default is False.
            sort_by: Sorting preference: 'review', 'price_low_to_high', or 'price_high_to_low'.
            hl: Host language code (e.g. 'en', 'it', 'es'). Default is 'en'.
            gl: Country perspective (e.g. 'us', 'it', 'de', 'gb'). Default is 'us'.
            google_domain: Google domain to query (e.g. 'google.com', 'google.it'). Default is 'google.com'.

        Returns:
            JSON formatted string containing product titles, prices, merchants/sellers, ratings, and purchase links.
        """
        run_input = {
            "query": query,
            "max_results": max_results,
            "min_price": min_price,
            "max_price": max_price,
            "free_shipping": free_shipping,
            "on_sale": on_sale,
            "sort_by": sort_by,
            "hl": hl,
            "gl": gl,
            "google_domain": google_domain,
        }

        result = await run_actor_with_timeout(
            actor_id="ilborso/google-shopping-now",
            run_input=run_input,
            timeout_secs=TIMEOUT_SCRAPING,
            max_items=max_results,
        )
        return json.dumps(result, ensure_ascii=False, indent=2)
