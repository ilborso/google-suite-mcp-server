# Google Suite MCP Server

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-orange?logo=apify)](https://apify.com/ilborso)
[![MCP Version](https://img.shields.io/badge/MCP-Protocol%202.x-blue)](https://modelcontextprotocol.io)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An autonomous, production-ready **Model Context Protocol (MCP)** server built in Python that exposes as LLM Tools **EXCLUSIVELY** the 9 high-performance Google scraping, intelligence, news, and AI Actors developed by [ilborso](https://apify.com/ilborso) on the Apify platform.

---

## 🎯 Architecture & Key Features

* **Dual Transport Architecture:** Supports standard **`stdio`** (default for Claude Desktop, Cursor, and CLI agents) and **`sse` / `streamable-http`** (for hosted containers and Apify Standby mode).
* **Strict Low-Latency Default Configuration:** Tools feature conservative query and pagination defaults (e.g., `max_results: 5` or `10`, `max_page: 1`) and strictly disable heavy crawling (`include_html: False`, reviews/place_info disabled by default).
* **Robust Timeout Management:**
  * **45s timeout** on web scraping runs (`Google Search`, `News`, `Maps`, `Flights`, `Shopping`).
  * **25s timeout** on LLM and Trends queries (`Gemini Flash Lite`, `Trending Now`, `Historical Trends`).
* **Graceful Degradation (No MCP Crash):** If an Apify Actor execution takes longer than the allotted low-latency threshold, the server intercepts the timeout and returns a structured JSON payload with status `RUNNING` along with the direct Apify Run URL (`https://console.apify.com/view/runs/{run_id}`). This allows the LLM to inform the user instead of hanging or crashing the MCP connection.
* **Intelligent Payload Trimming:** Prevents LLM context window saturation by stripping raw HTML, base64 images, tracking tokens, and deep debug fields, extracting only semantic fields (`title`, `price`, `rating`, `snippet`, `ai_overview`, `sources`, etc.).
* **Flexible Authentication:** Automatically detects and resolves authentication tokens from Actor input (`apifyToken`) or the `APIFY_TOKEN` environment variable.

---

## 🛠️ The 9 Exposed Tools

| Category | Tool Name | Apify Actor | Description | Default Timeout |
| :--- | :--- | :--- | :--- | :--- |
| **Search** | `google_search_ai_mode` | [`ilborso/google-search-ai-mode`](https://apify.com/ilborso/google-search-ai-mode) | Synthesized AI answers, text overviews, and source citations from Google AI Mode. | 45s |
| **Search** | `google_search_serp` | [`ilborso/google-search-fast-complete-result`](https://apify.com/ilborso/google-search-fast-complete-result) | Comprehensive Google SERP: organic rankings, Knowledge Graph, and People Also Ask. | 45s |
| **News** | `google_news_content_crawler` | [`ilborso/ai-news-content-crawler`](https://apify.com/ilborso/ai-news-content-crawler) | Clean, full-text news articles and content from Google News without paywalls or subscriptions. | 45s |
| **Intelligence** | `google_trending_now` | [`ilborso/google-trending-now`](https://apify.com/ilborso/google-trending-now) | Real-time trending searches with optional Gemini marketing intelligence enrichment. | 25s |
| **Intelligence** | `google_trending_historical` | [`ilborso/google-trending-historical-data`](https://apify.com/ilborso/google-trending-historical-data) | Historical Google Trends: interest over time, regional interest, and related queries. | 25s |
| **Intelligence** | `google_maps_search` | [`ilborso/google-maps-fast-scraper`](https://apify.com/ilborso/google-maps-fast-scraper) | Fast extraction of Google Maps local business data, ratings, addresses, and contacts. | 45s |
| **Commerce** | `google_flights_search` | [`ilborso/google-flights-api`](https://apify.com/ilborso/google-flights-api) | Live flight fares, airlines, layovers, durations, and carbon emission insights. | 45s |
| **Commerce** | `google_shopping_search` | [`ilborso/google-shopping-now`](https://apify.com/ilborso/google-shopping-now) | Real-time product search, merchant pricing, reviews, and discount tracking. | 45s |
| **AI** | `gemini_flash_lite_generate` | [`ilborso/gemini-flash-lite-latest`](https://apify.com/ilborso/gemini-flash-lite-latest) | High-speed text generation, summarization, and data extraction using Gemini Flash Lite. | 25s |

---

## 📁 Project Structure

```text
├── .actor/
│   ├── actor.json              # Apify Actor metadata configuration
│   └── input_schema.json       # Actor input schema (token, transport, host, port)
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastMCP server initialization & stdio/SSE runner
│   ├── tools/
│   │   ├── __init__.py         # Modular tool aggregator
│   │   ├── search_tools.py      # AI mode & SERP scraping tools
│   │   ├── intelligence_tools.py # Trending Now, Historical Trends, & Maps
│   │   ├── commerce_tools.py    # Flights & Shopping search tools
│   │   └── ai_tools.py          # Gemini Flash Lite tool
│   └── utils/
│       ├── __init__.py
│       └── apify_runner.py      # Async runner, timeout handling & payload trimmers
├── Dockerfile                  # Container definition for Apify Actor deployment
├── requirements.txt            # Python dependencies (apify, mcp, pydantic, uvicorn)
└── README.md                   # Full documentation and usage guide
```

---

## 🚀 Getting Started

### 1. Prerequisites

* **Python 3.11+** installed.
* An active **Apify Account** and **API Token** ([obtain here](https://console.apify.com/account/integrations)).

### 2. Local Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/ilborso/google-suite-mcp-server.git
cd google-suite-mcp-server
python -m pip install -r requirements.txt
```

Set your Apify API Token:

```bash
# On Linux/macOS
export APIFY_TOKEN="apify_api_your_token_here"

# On Windows (PowerShell)
$env:APIFY_TOKEN="apify_api_your_token_here"

# On Windows (CMD)
set APIFY_TOKEN=apify_api_your_token_here
```

Test launching the MCP server in `stdio` mode:

```bash
python -m src.main
```

---

## 🔌 Client Integrations

### Claude Desktop Integration

Add the server to your `claude_desktop_config.json`:

* **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "google-suite": {
      "command": "python",
      "args": [
        "-m",
        "src.main"
      ],
      "cwd": "C:/path/to/google-suite-mcp-server",
      "env": {
        "APIFY_TOKEN": "apify_api_your_personal_token"
      }
    }
  }
}
```

*Or run directly via Docker:*

```json
{
  "mcpServers": {
    "google-suite": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "APIFY_TOKEN=apify_api_your_personal_token",
        "ilborso/google-suite-mcp-server"
      ]
    }
  }
}
```

### Cursor IDE Integration

In Cursor:
1. Open **Cursor Settings** -> **Features** -> **MCP Servers**.
2. Click **Add New MCP Server**.
3. Name: `google-suite`
4. Type: `command`
5. Command: `python -m src.main` (or full path to python executable)
6. Environment Variables:
   * Key: `APIFY_TOKEN`
   * Value: `apify_api_your_personal_token`

---

## ☁️ Deployment on Apify Platform

You can deploy and run this server directly on the Apify platform:

1. Install the Apify CLI:
   ```bash
   npm install -g apify-cli
   ```
2. Log in to your Apify account:
   ```bash
   apify login
   ```
3. Push the Actor to your account:
   ```bash
   apify push
   ```

### Standby & SSE Web Service Mode

When running on Apify in Standby mode or behind an HTTP proxy, specify the transport in the Actor input or CLI:

```bash
python -m src.main --transport sse --port 8080 --host 0.0.0.0
```

The MCP SSE endpoint will be available at `http://0.0.0.0:8080/sse`.

---

## 🛡️ Error Handling & Graceful Degradation Details

When an Apify Actor call takes longer than the configured timeout:

```json
{
  "status": "RUNNING",
  "actor_id": "ilborso/google-maps-fast-scraper",
  "run_id": "W4k2Lm98QpLzx",
  "run_url": "https://console.apify.com/view/runs/W4k2Lm98QpLzx",
  "message": "Execution exceeded the strict low-latency timeout of 45 seconds. The scraper task is still executing safely in the background on Apify. The user can track its live progress or download results once finished at: https://console.apify.com/view/runs/W4k2Lm98QpLzx"
}
```

If the authentication token is missing:

```json
{
  "status": "ERROR",
  "error": "AUTHENTICATION_REQUIRED",
  "message": "Apify API token is not configured. Please supply 'apifyToken' in the Actor input or set the 'APIFY_TOKEN' environment variable. You can generate a token at https://console.apify.com/account/integrations"
}
```

---

## 📜 License

Distributed under the MIT License. Developed with pride by [ilborso](https://apify.com/ilborso).
