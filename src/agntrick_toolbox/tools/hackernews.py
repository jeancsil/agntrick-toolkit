"""Hacker News tools using HTTP API."""

import logging
from typing import Any

from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
import httpx

logger = logging.getLogger(__name__)

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"


def register_hackernews_tools(mcp: FastMCP) -> None:
    """Register Hacker News tools."""

    @mcp.tool()
    async def hacker_news_top(max_stories: int = 10) -> str:
        """Get top stories from Hacker News.

        Args:
            max_stories: Maximum number of stories to return (default 10, max 30).

        Returns:
            Formatted list of top stories with titles, URLs, and points.
        """
        max_stories = min(max_stories, 30)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Get top story IDs
                response = await client.get(f"{HN_API_BASE}/topstories.json")
                story_ids = response.json()[:max_stories]

                # Fetch each story
                stories: list[dict[str, Any]] = []
                for story_id in story_ids:
                    story_resp = await client.get(f"{HN_API_BASE}/item/{story_id}.json")
                    story = story_resp.json()
                    if story:
                        stories.append(story)

                if not stories:
                    return "No stories found."

                formatted = []
                for story in stories:
                    title = story.get("title", "No title")
                    url = story.get("url") or f"https://news.ycombinator.com/item?id={story.get('id')}"
                    score = story.get("score", 0)
                    comments = story.get("descendants", 0)

                    formatted.append(
                        f"**{title}**\n"
                        f"URL: {url}\n"
                        f"Points: {score} | Comments: {comments}"
                    )

                return "\n\n---\n\n".join(formatted)

        except Exception as e:
            logger.error(f"Failed to fetch HN stories: {e}")
            return f"Error fetching stories: {e}"

    @mcp.tool()
    async def hacker_news_item(item_id: int) -> str:
        """Get details of a specific Hacker News item.

        Args:
            item_id: The Hacker News item ID.

        Returns:
            Item details including title, URL, text, author, and points.
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{HN_API_BASE}/item/{item_id}.json")
                item = response.json()

                if not item:
                    return f"Item {item_id} not found."

                result = f"**{item.get('title', 'No title')}**\n"
                result += f"By: {item.get('by', 'unknown')} | Points: {item.get('score', 0)}\n"

                if item.get("url"):
                    result += f"URL: {item['url']}\n"

                if item.get("text"):
                    # Strip HTML tags from text
                    soup = BeautifulSoup(item["text"], "html.parser")
                    clean_text = soup.get_text()
                    result += f"\n{clean_text}"

                return result

        except Exception as e:
            logger.error(f"Failed to fetch HN item {item_id}: {e}")
            return f"Error fetching item: {e}"
