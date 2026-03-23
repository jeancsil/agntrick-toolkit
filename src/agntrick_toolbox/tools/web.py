"""Web search and fetch tools using proven libraries."""

import logging
from typing import Any

import httpx
from ddgs import DDGS
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_web_tools(mcp: FastMCP) -> None:
    """Register web search and fetch tools."""

    @mcp.tool()
    async def web_search(query: str, max_results: int = 5) -> str:
        """Search the web using DuckDuckGo.

        Args:
            query: The search query.
            max_results: Maximum number of results (default 5, max 10).

        Returns:
            Formatted search results with titles, URLs, and snippets.
        """
        max_results = min(max_results, 10)  # Cap at 10
        results: list[dict[str, Any]] = []

        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append(r)
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return f"Search error: {e}"

        if not results:
            return "No results found."

        formatted = []
        for r in results:
            title = r.get("title", "No title")
            href = r.get("href", "")
            body = r.get("body", "")
            formatted.append(f"**{title}**\n{href}\n{body}")

        return "\n\n---\n\n".join(formatted)

    @mcp.tool()
    async def web_fetch(url: str, timeout: int = 30) -> str:
        """Fetch and extract text content from a URL.

        Uses Jina Reader API for clean text extraction (free, no API key).

        Args:
            url: The URL to fetch.
            timeout: Request timeout in seconds.

        Returns:
            Extracted text content from the page.
        """
        jina_url = f"https://r.jina.ai/{url}"

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(jina_url)
                response.raise_for_status()
                return response.text
        except httpx.TimeoutException:
            return f"Error: Request timed out after {timeout} seconds."
        except httpx.HTTPStatusError as e:
            return f"Error: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Fetch failed for {url}: {e}")
            return f"Error fetching URL: {e}"
