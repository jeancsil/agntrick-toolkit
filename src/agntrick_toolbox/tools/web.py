"""Web search and fetch tools using proven libraries."""

import logging
from typing import Any

import httpx
from ddgs import DDGS
from mcp.server.fastmcp import FastMCP

from ..config import settings

logger = logging.getLogger(__name__)


def _extract_headings(markdown_text: str, max_chars: int = 3_000) -> str:
    """Extract headings and first paragraph from markdown text.

    Keeps only lines starting with # (headings) and the first
    non-heading paragraph after each heading. Ideal for news sites.
    """
    lines = markdown_text.split("\n")
    result: list[str] = []
    paragraph_lines: list[str] = []
    in_first_paragraph = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            if paragraph_lines:
                result.append(" ".join(paragraph_lines))
                paragraph_lines = []
            result.append(stripped)
            in_first_paragraph = True
        elif in_first_paragraph and stripped:
            paragraph_lines.append(stripped)
        elif not stripped:
            if paragraph_lines:
                result.append(" ".join(paragraph_lines))
                paragraph_lines = []
            in_first_paragraph = False

    if paragraph_lines:
        result.append(" ".join(paragraph_lines))

    output = "\n\n".join(result)
    if len(output) > max_chars:
        output = output[:max_chars] + "\n\n[...truncated]"
    return output


def _is_rss_url(url: str) -> bool:
    """Check if URL looks like an RSS/Atom feed."""
    rss_indicators = ["/rss", "/feed", "/atom.xml", ".rss", ".xml"]
    url_lower = url.lower()
    return any(indicator in url_lower for indicator in rss_indicators)


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
            body = r.get("body", "")[:300]
            formatted.append(f"**{title}**\n{href}\n{body}")

        return "\n\n---\n\n".join(formatted)

    @mcp.tool()
    async def web_fetch(url: str, timeout: int = 30, mode: str = "article") -> str:
        """Fetch and extract text content from a URL.

        Uses Jina Reader API for clean text extraction (free, no API key).

        Args:
            url: The URL to fetch.
            timeout: Request timeout in seconds.
            mode: Extraction mode.
                - "article": Full article text (default, max 15000 chars)
                - "headlines": Extract only headings and first paragraph (max 3000 chars)

        Returns:
            Extracted text content from the page, truncated if too large.
        """
        # Auto-detect RSS feeds and switch to headlines mode
        if _is_rss_url(url) and mode == "article":
            mode = "headlines"

        jina_url = f"https://r.jina.ai/{url}"

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(jina_url)
                response.raise_for_status()
                text = response.text

            if not text or not text.strip():
                logger.warning(f"web_fetch: Jina returned empty body for {url} (status={response.status_code})")
                return f"Error: No content returned for {url}. The site may block automated access or require JavaScript rendering."

            logger.info(f"web_fetch: {url} -> {len(text)} chars (status={response.status_code}, mode={mode})")

            if mode == "headlines":
                text = _extract_headings(text)

            max_size = settings.toolbox_web_response_max_size
            if len(text) > max_size:
                original_len = len(response.text)
                text = text[:max_size] + f"\n\n[Response truncated at {max_size} chars. Original size: {original_len} chars]"

            return text
        except httpx.TimeoutException:
            return f"Error: Request timed out after {timeout} seconds."
        except httpx.HTTPStatusError as e:
            return f"Error: HTTP {e.response.status_code}"
        except Exception as e:
            logger.error(f"Fetch failed for {url}: {e}")
            return f"Error fetching URL: {e}"
