# Google Scraping Suite Mcp Server

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-orange?logo=apify)](https://apify.com/ilborso/google-suite-mcp-server)
[![MCP Version](https://img.shields.io/badge/MCP-Protocol%202.x-blue)](https://modelcontextprotocol.io)

A high-performance **Model Context Protocol (MCP)** server connecting Claude Desktop, Cursor, Antigravity IDE, Windsurf, and any MCP-compatible AI agent directly to the suite of 9 specialized Google scraping, intelligence, news, and AI Actors powered by Apify.

* **Instant GitHub Launch (`stdio` - Recommended):** Run directly from this public repository via `uvx` with zero cloning, zero manual venv management, and native low-latency stdio transport.
* **Remote Cloud Standby (SSE / HTTP):** Connect 24/7 to the cloud-hosted Apify Standby container without keeping any local processes running.
* **Zero Scraping Maintenance:** No proxy rotations, headless browsers, or anti-bot bypasses to manage.

---

## What is Google Suite MCP Server?

Google Suite MCP Server provides an AI-native interface to Google's public data ecosystem. Rather than maintaining custom web scrapers, residential proxies, or headless browsers, your AI assistant can directly query live Google services using standard natural language prompts:

* **Live AI Overviews:** Retrieve direct AI Mode answers, synthesized overviews, and source references.
* **Comprehensive Search SERP:** Access organic search rankings, Knowledge Graph cards, and People Also Ask questions.
* **Full-Text News Intelligence:** Crawl and extract clean, paywall-free full articles from global news sources.
* **Trends & Cultural Momentum:** Query real-time search trends enriched with Gemini marketing intelligence, plus historical multi-year interest graphs.
* **Local Business Data:** Extract Google Maps merchant profiles, coordinates, phone numbers, and ratings at scale.
* **Travel & Commerce:** Query live Google Flights airfares and Google Shopping merchant listings and pricing.
* **Fast Generative Intelligence:** Execute high-speed summarization, data extraction, and multi-modal tasks via Gemini Flash Lite.

---

## The 9 Exposed Tools

| Category | Tool Name | Apify Actor | Description | Example Prompt | Default Timeout |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Search** | `google_search_ai_mode` | [`ilborso/google-search-ai-mode`](https://apify.com/ilborso/google-search-ai-mode) | Synthesized AI answers, text overviews, and source citations from Google AI Mode. | "What are the latest breakthroughs in solid-state batteries according to Google AI?" | 50s |
| **Search** | `google_search_serp` | [`ilborso/google-search-fast-complete-result`](https://apify.com/ilborso/google-search-fast-complete-result) | Comprehensive Google SERP: organic rankings, Knowledge Graph, and People Also Ask. | "Find the top 5 ranked articles for quantum computing frameworks." | 50s |
| **News** | `google_news_content_crawler` | [`ilborso/ai-news-content-crawler`](https://apify.com/ilborso/ai-news-content-crawler) | Clean, full-text news articles and content from Google News without paywalls or subscriptions. | "Extract the full text of today's top 3 news stories about semiconductor manufacturing." | 50s |
| **Intelligence** | `google_trending_now` | [`ilborso/google-trending-now`](https://apify.com/ilborso/google-trending-now) | Real-time trending searches with optional Gemini marketing intelligence enrichment. | "Show me what is trending right now in Italy with AI marketing analysis." | 50s |
| **Intelligence** | `google_trending_historical` | [`ilborso/google-trending-historical-data`](https://apify.com/ilborso/google-trending-historical-data) | Historical Google Trends: interest over time, regional interest, and related queries. | "Compare search interest trends between Python and Rust over the last 12 months." | 50s |
| **Intelligence** | `google_maps_search` | [`ilborso/google-maps-fast-scraper`](https://apify.com/ilborso/google-maps-fast-scraper) | Fast extraction of Google Maps local business data, ratings, addresses, and contacts. | "Find top rated Italian restaurants in Zurich with their address and rating." | 50s |
| **Commerce** | `google_flights_search` | [`ilborso/google-flights-api`](https://apify.com/ilborso/google-flights-api) | Live flight fares, airlines, layovers, durations, and carbon emission insights. | "Find one-way flights from Rome (FCO) to New York (JFK) on November 20." | 50s |
| **Commerce** | `google_shopping_search` | [`ilborso/google-shopping-now`](https://apify.com/ilborso/google-shopping-now) | Real-time product search, merchant pricing, reviews, and discount tracking. | "Search for Sony WH-1000XM5 headphones and list prices across different sellers." | 50s |
| **AI** | `gemini_flash_lite_generate` | [`ilborso/gemini-flash-lite-latest`](https://apify.com/ilborso/gemini-flash-lite-latest) | High-speed text generation, summarization, and data extraction using Gemini Flash Lite. | "Summarize this technical specification into 3 concise bullet points." | 50s |

---

## How to Connect in 3 Steps

Connecting your AI assistant to the Google Suite MCP Server takes less than two minutes.

### Step 1: Obtain Your Apify API Token

1. Sign in to your [Apify Console](https://console.apify.com/). If you do not have an account, you can create one for free.
2. Navigate to [Settings -> Integrations](https://console.apify.com/settings/integrations).
3. Copy your personal **API Token**.

### Step 2: Add the Server to Your MCP Client

#### Method 1: Local `stdio` from GitHub via `uvx` (Recommended ⭐)

The recommended connection method uses **`uvx`** to run the server over standard input/output (`stdio`). `uvx` automatically fetches the code from GitHub, installs dependencies in an isolated cache, and runs the server at maximum speed with zero manual maintenance:

```json
{
  "mcpServers": {
    "google-suite": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/ilborso/google-suite-mcp-server.git",
        "google-suite-mcp-server"
      ],
      "env": {
        "APIFY_TOKEN": "YOUR_APIFY_TOKEN"
      }
    }
  }
}
```

> [!TIP]
> **Corporate Networks / Custom SSL:** If you are behind an enterprise proxy that inspects HTTPS traffic, include `--system-certs`:
> `"args": ["--system-certs", "--from", "git+https://github.com/ilborso/google-suite-mcp-server.git", "google-suite-mcp-server"]`

#### Method 2: Remote Cloud Standby (SSE / HTTP)

If your client runs in a cloud environment or requires a remote URL endpoint, connect to the hosted 24/7 Apify Standby actor:

```text
https://ilborso--google-suite-mcp-server.apify.actor/sse?token=YOUR_APIFY_TOKEN
```

Replace `YOUR_APIFY_TOKEN` with the personal token copied in Step 1.

### Step 3: Start Prompting

Open your AI assistant and prompt naturally:

> "Use Google Search AI Mode to summarize the latest developments in generative robotics."

Your assistant will query the MCP server, trigger the Actor on Apify, process the trimmed result, and formulate its response.

---

## Client Configuration Examples

### Option A: Local `stdio` via `uvx` directly from GitHub (Recommended ⭐)

No local git clone or manual environment setup required. `uvx` pulls the latest release from GitHub and executes in high-performance `stdio` mode.

#### Claude Desktop & Antigravity IDE
Edit your configuration file:
* **Antigravity IDE:** `~/.gemini/config/mcp_config.json`
* **Claude Desktop (Windows):** `%APPDATA%\Claude\claude_desktop_config.json`
* **Claude Desktop (macOS):** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "google-suite": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/ilborso/google-suite-mcp-server.git",
        "google-suite-mcp-server"
      ],
      "env": {
        "APIFY_TOKEN": "YOUR_APIFY_TOKEN"
      }
    }
  }
}
```

#### Cursor IDE
Open **Cursor Settings** -> **Features** -> **MCP Servers** or edit your workspace `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "google-suite": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/ilborso/google-suite-mcp-server.git",
        "google-suite-mcp-server"
      ],
      "env": {
        "APIFY_TOKEN": "YOUR_APIFY_TOKEN"
      }
    }
  }
}
```

#### Alternative: One-Time `pip` Installation from GitHub
If you prefer standard Python `pip` without `uv`:
```bash
pip install git+https://github.com/ilborso/google-suite-mcp-server.git
```
Then configure your client to run the installed CLI command directly:
```json
{
  "mcpServers": {
    "google-suite": {
      "command": "google-suite-mcp-server",
      "args": ["--transport", "stdio"],
      "env": {
        "APIFY_TOKEN": "YOUR_APIFY_TOKEN"
      }
    }
  }
}
```

#### Alternative: Docker Container from GitHub
```json
{
  "mcpServers": {
    "google-suite": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "APIFY_TOKEN=YOUR_APIFY_TOKEN",
        "-e", "MCP_TRANSPORT=stdio",
        "ghcr.io/ilborso/google-suite-mcp-server:latest"
      ]
    }
  }
}
```

---

### Option B: Cloud Standby (Remote SSE)

#### Claude Desktop
Edit your configuration file:
* **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "google-suite": {
      "type": "url",
      "url": "https://ilborso--google-suite-mcp-server.apify.actor/sse?token=YOUR_APIFY_TOKEN",
      "timeout": 60000
    }
  }
}
```

#### Cursor IDE
```json
{
  "mcpServers": {
    "google-suite": {
      "url": "https://ilborso--google-suite-mcp-server.apify.actor/sse?token=YOUR_APIFY_TOKEN",
      "requestTimeoutMs": 60000
    }
  }
}
```

### Windsurf

In Windsurf MCP Settings (`~/.codeium/windsurf/mcp_config.json`):

```json
{
  "mcpServers": {
    "google-suite": {
      "serverUrl": "https://ilborso--google-suite-mcp-server.apify.actor/sse?token=YOUR_APIFY_TOKEN"
    }
  }
}
```

### Continue.dev

In `~/.continue/config.json`:

```json
{
  "experimental": {
    "modelContextProtocolServers": [
      {
        "transport": {
          "type": "sse",
          "url": "https://ilborso--google-suite-mcp-server.apify.actor/sse?token=YOUR_APIFY_TOKEN",
          "requestTimeoutMs": 60000
        }
      }
    ]
  }
}
```

### Python Clients (LangChain / MCP SDK)

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "google-suite": {
        "transport": "sse",
        "url": "https://ilborso--google-suite-mcp-server.apify.actor/sse?token=YOUR_APIFY_TOKEN",
        "timeout": 60,
    }
})
```

---

## Client Compatibility & Timeouts

Live web scraping and multi-page news crawling involve dynamic browser rendering, proxy allocation, and network queries. While simple searches finish in 5 to 15 seconds, deep crawls or multi-result maps queries may take between 20 and 45 seconds.

Many MCP clients ship with an aggressive default timeout of 10 to 30 seconds. If your client closes the connection before the scrape completes, it will throw an interrupted connection or authentication error.

To ensure uninterrupted operation, configure your client's request timeout to **60 seconds or higher**.

### Recommended Timeout per Client

| Client | Default Timeout | Recommended Timeout | Configuration Method |
| :--- | :--- | :--- | :--- |
| **Claude Desktop** | 30s | 60s+ | Set `"timeout": 60000` in `claude_desktop_config.json` |
| **Cursor IDE** | 30s | 60s+ | Set `"requestTimeoutMs": 60000` in `mcp.json` |
| **Windsurf** | 60s | 60s+ | Default configuration is sufficient |
| **Continue.dev** | 30s | 60s+ | Set `requestTimeoutMs: 60000` in MCP server block |
| **Cline (VS Code)** | 30s | 60s+ | Extension Settings -> MCP Timeout |
| **LangChain MCP** | None | 60s+ | Set `timeout=60` in client initialization |
| **@modelcontextprotocol/sdk** | 30s | 60s+ | Set `requestTimeoutMs: 60000` in client options |

---

## Best Practices to Avoid Timeouts

1. **Sequential Tool Invocations:** Execute tool calls sequentially rather than firing multiple concurrent requests. Concurrent calls can trigger client transport closure before all streams finish.
2. **Use Conservative Pagination Defaults:** Start queries with focused parameter limits (e.g., `max_results: 3` to `5` or `days_back: 1` for news). Increase result counts only when extensive analysis is needed.
3. **Standby Mode Cold-Start:** When the Actor is idle in Apify Standby mode, the first incoming request initializes the container (cold-start takes 3 to 5 seconds). Subsequent requests within active standby share the warm container and respond immediately.

---

## Troubleshooting Common Issues

| Observed Error | Root Cause | Solution |
| :--- | :--- | :--- |
| **"Invalid or expired MCP authentication"** | The MCP client timed out before the scraping response arrived. This is a client-side timeout issue, not an authentication failure. | Increase your MCP client timeout to 60,000 ms (60 seconds) or more. |
| **"Interrupted network connection"** | The client closed the transport socket while waiting for the scraper. | Ensure client timeout is configured to 60s+ and avoid issuing parallel requests. |
| **"Tool call returned no content"** | Overlapping requests or dropped SSE stream. | Structure prompts so the assistant awaits each tool result sequentially. |
| **"AUTHENTICATION_REQUIRED"** | The `token` query parameter was omitted or invalid. | Verify that `?token=YOUR_APIFY_TOKEN` is appended to the Standby URL and your token is active. |
| **"Server returned non-200" on first request** | Standby cold-start latency exceeded the client handshake deadline. | Increase client request timeout to allow container initialization. |

---

## Payload Optimization & Graceful Degradation

### Context Window Protection

To prevent context window bloat and excessive LLM token usage, all scraper responses are automatically trimmed by the server:
* Raw HTML documents, base64 data URIs, and debug payloads are stripped.
* High-value semantic fields are retained: `title`, `url`, `snippet`, `price`, `rating`, `ai_overview`, and `sources`.
* Long text articles and descriptions are automatically condensed to essential passages.

### 50-Second Graceful Degradation

All tools enforce a strict internal timeout limit of **50 seconds**. If an Apify scraping task exceeds this limit, the MCP server does not crash or raise an unhandled exception. Instead, it returns a structured JSON status payload:

```json
{
  "status": "RUNNING",
  "actor_id": "ilborso/google-maps-fast-scraper",
  "run_id": "W4k2Lm98QpLzx",
  "run_url": "https://console.apify.com/view/runs/W4k2Lm98QpLzx",
  "message": "Execution exceeded the strict low-latency timeout of 50 seconds. The scraper task is still executing safely in the background on Apify. The user can track its live progress or download results once finished at: https://console.apify.com/view/runs/W4k2Lm98QpLzx"
}
```

This ensures the AI assistant can explain to the user that the task is still progressing safely in the cloud, providing the direct Apify Run URL without breaking the MCP session.

---