from __future__ import annotations

import os
from typing import Any
from dotenv import load_dotenv  # ← add this

load_dotenv()

import httpx
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP, Context

GNEWS_BASE_URL = "https://gnews.io/api/v4"
API_KEY_ENV = "b8142168b163bbd5ce0710ac3262587d"

mcp = FastMCP(
    name="GNews API MCP Server",
    instructions=(
        "Expose the GNews Search and Top Headlines API to MCP clients. "
        "Requires a valid GNEWS_API_KEY environment variable."
    ),
    json_response=True,
    host_header_validation=False
)


class GNewsSource(BaseModel):
    name: str | None = None
    url: str | None = None


class GNewsArticle(BaseModel):
    title: str
    description: str | None = None
    content: str | None = None
    url: str
    image: str | None = None
    publishedAt: str | None = None
    source: GNewsSource | None = None


class GNewsResponse(BaseModel):
    totalArticles: int
    articles: list[GNewsArticle] = []


def get_api_key() -> str:
    api_key = os.environ.get("GNEWS_API_KEY")
    if not api_key:
        raise RuntimeError(
        )
    return api_key


async def fetch_gnews(endpoint: str, params: dict[str, Any]) -> dict[str, Any]:
    params = {k: v for k, v in params.items() if v is not None}
    params["apikey"] = get_api_key()
    url = f"{GNEWS_BASE_URL}/{endpoint}"

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


def format_articles(articles: list[dict[str, Any]]) -> str:
    formatted = []
    for article in articles:
        title = article.get("title", "(no title)")
        description = article.get("description") or ""
        url = article.get("url", "")
        published_at = article.get("publishedAt") or ""
        formatted.append(
            f"{title}\n{description}\n{url}\n{published_at}"
        )
    return "\n\n".join(formatted)


@mcp.tool()
async def search_news(
    q: str,
    lang: str | None = None,
    country: str | None = None,
    max: int = 10,
    page: int = 1,
    sortby: str = "publishedAt",
    in_: str | None = None,
    from_: str | None = None,
    to: str | None = None,
    truncate: str | None = None,
    nullable: str | None = None,
    ctx: Context | None = None,
) -> GNewsResponse:
    """Search GNews articles using the Search endpoint."""
    params = {
        "q": q,
        "lang": lang,
        "country": country,
        "max": max,
        "page": page,
        "sortby": sortby,
        "in": in_,
        "from": from_,
        "to": to,
        "truncate": truncate,
        "nullable": nullable,
    }
    data = await fetch_gnews("search", params)
    return GNewsResponse(**data)


@mcp.tool()
async def top_headlines(
    category: str = "general",
    q: str | None = None,
    lang: str | None = None,
    country: str | None = None,
    max: int = 10,
    page: int = 1,
    from_: str | None = None,
    to: str | None = None,
    truncate: str | None = None,
    nullable: str | None = None,
    ctx: Context | None = None,
) -> GNewsResponse:
    """Fetch top headlines from GNews."""
    params = {
        "category": category,
        "q": q,
        "lang": lang,
        "country": country,
        "max": max,
        "page": page,
        "from": from_,
        "to": to,
        "truncate": truncate,
        "nullable": nullable,
    }
    data = await fetch_gnews("top-headlines", params)
    return GNewsResponse(**data)


@mcp.resource("gnews://search/{query}/{lang}/{max}")
async def news_search_resource(
    query: str,
    lang: str = "en",
    max: int = 5,
) -> str:
    """Expose search results as an MCP resource for contextual loading."""
    data = await fetch_gnews(
        "search",
        {"q": query, "lang": lang, "max": max},
    )
    return format_articles(data.get("articles", []))


@mcp.resource("gnews://top-headlines/{category}/{lang}/{max}")
async def top_headlines_resource(
    category: str = "general",
    lang: str = "en",
    max: int = 5,
) -> str:
    """Expose top headlines as an MCP resource for contextual loading."""
    data = await fetch_gnews(
        "top-headlines",
        {"category": category, "lang": lang, "max": max},
    )
    return format_articles(data.get("articles", []))

