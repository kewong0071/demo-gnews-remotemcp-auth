# GNews MCP Server

This repository contains an MCP server that integrates the GNews API using the `FastMCP` high-level Python interface.

## What it exposes

- `search_news` tool: calls the GNews Search endpoint
- `top_headlines` tool: calls the GNews Top Headlines endpoint
- `gnews://search/{query}` resource: returns summary text for a search query
- `gnews://top-headlines/{category}` resource: returns summary text for a headline category

## Setup

1. Set your GNews API key:

```powershell
$env:GNEWS_API_KEY = "your_api_key"
```

2. Install dependencies:

```powershell
uv add "mcp[cli]>=1.27.1" httpx
```

3. Run the server:

```powershell
uv run python main.py
```

## Usage

The server starts as a Streamable HTTP MCP server. You can connect an MCP client to:

- `http://localhost:8000/mcp`

### Example tools

- `search_news(q="bitcoin", lang="en", max=10)`
- `top_headlines(category="technology", lang="en", country="us", max=10)`

### Notes

- The server requires `GNEWS_API_KEY` in the environment.
- The integration uses `httpx` for async HTTP requests.
