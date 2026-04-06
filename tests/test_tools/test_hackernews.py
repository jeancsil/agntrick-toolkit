"""Tests for Hacker News tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestHackerNewsTop:
    """Tests for hacker_news_top tool."""

    @pytest.mark.asyncio
    async def test_hacker_news_top_returns_stories(self) -> None:
        """hacker_news_top should return formatted top stories."""
        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.hackernews import register_hackernews_tools

        mock_story_ids = [1, 2, 3]
        mock_stories = [
            {
                "id": 1,
                "title": "First Story",
                "url": "https://example.com/1",
                "score": 100,
                "descendants": 50,
            },
            {
                "id": 2,
                "title": "Second Story",
                "url": "https://example.com/2",
                "score": 80,
                "descendants": 30,
            },
            {
                "id": 3,
                "title": "Third Story",
                "url": "https://example.com/3",
                "score": 60,
                "descendants": 20,
            },
        ]

        with patch("agntrick_toolbox.tools.hackernews.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()

            # Mock responses for topstories and each item
            responses = []
            ids_response = AsyncMock()
            ids_response.json = MagicMock(return_value=mock_story_ids)
            responses.append(ids_response)

            for story in mock_stories:
                story_response = AsyncMock()
                story_response.json = MagicMock(return_value=story)
                responses.append(story_response)

            mock_client.get = AsyncMock(side_effect=responses)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_client)
            mock_context.__aexit__ = AsyncMock(return_value=False)

            mock_client_class.return_value = mock_context

            mcp = FastMCP("test")
            register_hackernews_tools(mcp)

            tools = mcp._tool_manager._tools
            hn_tool = tools.get("hacker_news_top")
            assert hn_tool is not None

            result = await hn_tool.fn(max_stories=3)

        assert "First Story" in result
        assert "100" in result  # score
        assert "https://example.com/1" in result

    @pytest.mark.asyncio
    async def test_hacker_news_top_handles_missing_url(self) -> None:
        """hacker_news_top should handle stories without URL (Ask HN)."""
        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.hackernews import register_hackernews_tools

        mock_story_ids = [1]
        mock_stories = [
            {"id": 1, "title": "Ask HN: Something", "score": 50, "descendants": 10},
        ]

        with patch("agntrick_toolbox.tools.hackernews.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()

            responses = []
            ids_response = AsyncMock()
            ids_response.json = MagicMock(return_value=mock_story_ids)
            responses.append(ids_response)

            for story in mock_stories:
                story_response = AsyncMock()
                story_response.json = MagicMock(return_value=story)
                responses.append(story_response)

            mock_client.get = AsyncMock(side_effect=responses)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_client)
            mock_context.__aexit__ = AsyncMock(return_value=False)

            mock_client_class.return_value = mock_context

            mcp = FastMCP("test")
            register_hackernews_tools(mcp)

            tools = mcp._tool_manager._tools
            hn_tool = tools.get("hacker_news_top")
            assert hn_tool is not None

            result = await hn_tool.fn(max_stories=1)

        assert "Ask HN" in result
        assert "news.ycombinator.com" in result  # Should link to HN item page


class TestHackerNewsItem:
    """Tests for hacker_news_item tool."""

    @pytest.mark.asyncio
    async def test_hacker_news_item_returns_details(self) -> None:
        """hacker_news_item should return item details."""
        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.hackernews import register_hackernews_tools

        mock_item = {
            "id": 12345,
            "title": "Test Story",
            "by": "testuser",
            "score": 42,
            "url": "https://example.com/test",
            "text": "<p>This is <b>bold</b> text.</p>",
        }

        with patch("agntrick_toolbox.tools.hackernews.httpx.AsyncClient") as mock_client_class:
            mock_response = AsyncMock()
            mock_response.json = MagicMock(return_value=mock_item)

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_client)
            mock_context.__aexit__ = AsyncMock(return_value=False)

            mock_client_class.return_value = mock_context

            mcp = FastMCP("test")
            register_hackernews_tools(mcp)

            tools = mcp._tool_manager._tools
            hn_tool = tools.get("hacker_news_item")
            assert hn_tool is not None

            result = await hn_tool.fn(item_id=12345)

        assert "Test Story" in result
        assert "testuser" in result
        assert "42" in result
        assert "https://example.com/test" in result
        # HTML should be stripped
        assert "<p>" not in result
        assert "<b>" not in result

    @pytest.mark.asyncio
    async def test_hacker_news_item_handles_not_found(self) -> None:
        """hacker_news_item should handle missing items."""
        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.hackernews import register_hackernews_tools

        with patch("agntrick_toolbox.tools.hackernews.httpx.AsyncClient") as mock_client_class:
            mock_response = AsyncMock()
            mock_response.json = MagicMock(return_value=None)

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_client)
            mock_context.__aexit__ = AsyncMock(return_value=False)

            mock_client_class.return_value = mock_context

            mcp = FastMCP("test")
            register_hackernews_tools(mcp)

            tools = mcp._tool_manager._tools
            hn_tool = tools.get("hacker_news_item")
            assert hn_tool is not None

            result = await hn_tool.fn(item_id=99999999)

        assert "not found" in result.lower()
