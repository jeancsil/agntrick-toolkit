"""Tests for web tools."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestWebSearch:
    """Tests for web_search tool."""

    @pytest.mark.asyncio
    async def test_web_search_returns_formatted_results(self) -> None:
        """web_search should return formatted search results."""
        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.web import register_web_tools

        mock_results = [
            {"title": "Python Guide", "href": "https://example.com/python", "body": "Learn Python"},
            {
                "title": "Python Tutorial",
                "href": "https://example.com/tutorial",
                "body": "Best tutorial",
            },
        ]

        with patch("agntrick_toolbox.tools.web.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_instance.text.return_value = iter(mock_results)
            mock_ddgs.return_value = mock_instance

            mcp = FastMCP("test")
            register_web_tools(mcp)

            tools = mcp._tool_manager._tools
            search_tool = tools.get("web_search")
            assert search_tool is not None

            result = await search_tool.fn(query="python programming", max_results=2)

        assert "Python Guide" in result
        assert "https://example.com/python" in result
        assert "Learn Python" in result

    @pytest.mark.asyncio
    async def test_web_search_no_results_returns_message(self) -> None:
        """web_search should return a message when no results found."""
        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.web import register_web_tools

        with patch("agntrick_toolbox.tools.web.DDGS") as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=False)
            mock_instance.text.return_value = iter([])
            mock_ddgs.return_value = mock_instance

            mcp = FastMCP("test")
            register_web_tools(mcp)

            tools = mcp._tool_manager._tools
            search_tool = tools.get("web_search")
            assert search_tool is not None

            result = await search_tool.fn(query="zzzzzzzzzznonexistent")

        assert result == "No results found."


class TestWebFetch:
    """Tests for web_fetch tool."""

    @pytest.mark.asyncio
    async def test_web_fetch_returns_content(self) -> None:
        """web_fetch should return fetched content."""
        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.web import register_web_tools

        with patch("agntrick_toolbox.tools.web.httpx.AsyncClient") as mock_client_class:
            # Mock the response
            mock_response = AsyncMock()
            mock_response.text = "# Extracted Content\n\nThis is the page content."
            mock_response.raise_for_status = MagicMock()

            # Mock the client (returned by async with)
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)

            # Mock the context manager (returned by AsyncClient())
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_client)
            mock_context.__aexit__ = AsyncMock(return_value=False)

            mock_client_class.return_value = mock_context

            mcp = FastMCP("test")
            register_web_tools(mcp)

            tools = mcp._tool_manager._tools
            fetch_tool = tools.get("web_fetch")
            assert fetch_tool is not None

            result = await fetch_tool.fn(url="https://example.com/article")

        assert "Extracted Content" in result
        assert "r.jina.ai" not in result  # Should not expose internal URL

    @pytest.mark.asyncio
    async def test_web_fetch_handles_timeout(self) -> None:
        """web_fetch should handle timeout gracefully."""
        import httpx
        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.web import register_web_tools

        with patch("agntrick_toolbox.tools.web.httpx.AsyncClient") as mock_client:
            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
            mock_context.__aexit__ = AsyncMock(return_value=False)
            mock_client.return_value = mock_context

            mcp = FastMCP("test")
            register_web_tools(mcp)

            tools = mcp._tool_manager._tools
            fetch_tool = tools.get("web_fetch")
            assert fetch_tool is not None

            result = await fetch_tool.fn(url="https://example.com/slow")

        assert "Error" in result
        assert "timed out" in result.lower()

    @pytest.mark.asyncio
    async def test_web_fetch_truncates_large_response(self) -> None:
        """web_fetch should truncate responses exceeding the configured max size."""
        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.web import register_web_tools

        # Create a response larger than default 20_000 chars
        large_content = "x" * 25_000

        with patch("agntrick_toolbox.tools.web.httpx.AsyncClient") as mock_client_class:
            mock_response = AsyncMock()
            mock_response.text = large_content
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_client)
            mock_context.__aexit__ = AsyncMock(return_value=False)

            mock_client_class.return_value = mock_context

            mcp = FastMCP("test")
            register_web_tools(mcp)

            tools = mcp._tool_manager._tools
            fetch_tool = tools.get("web_fetch")
            assert fetch_tool is not None

            result = await fetch_tool.fn(url="https://example.com/huge-page")

        assert "Response truncated" in result
        assert len(result) < 25_000
        # Should contain first 20_000 chars of original content
        assert result.startswith("x" * 100)
        # The result should be max_size + truncation marker length
        assert len(result) <= 21_000  # 20_000 + marker text

    @pytest.mark.asyncio
    async def test_web_fetch_returns_error_for_empty_response(self) -> None:
        """web_fetch should return an error when Jina returns empty content."""
        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.web import register_web_tools

        with patch("agntrick_toolbox.tools.web.httpx.AsyncClient") as mock_client_class:
            mock_response = AsyncMock()
            mock_response.text = ""
            mock_response.status_code = 200
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_client)
            mock_context.__aexit__ = AsyncMock(return_value=False)

            mock_client_class.return_value = mock_context

            mcp = FastMCP("test")
            register_web_tools(mcp)

            tools = mcp._tool_manager._tools
            fetch_tool = tools.get("web_fetch")
            assert fetch_tool is not None

            result = await fetch_tool.fn(url="https://g1.globo.com")

        assert "Error" in result
        assert "No content" in result

    @pytest.mark.asyncio
    async def test_web_fetch_no_truncation_for_small_response(self) -> None:
        """web_fetch should not truncate small responses."""
        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.web import register_web_tools

        small_content = "Hello, this is a small page."

        with patch("agntrick_toolbox.tools.web.httpx.AsyncClient") as mock_client_class:
            mock_response = AsyncMock()
            mock_response.text = small_content
            mock_response.raise_for_status = MagicMock()

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)

            mock_context = AsyncMock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_client)
            mock_context.__aexit__ = AsyncMock(return_value=False)

            mock_client_class.return_value = mock_context

            mcp = FastMCP("test")
            register_web_tools(mcp)

            tools = mcp._tool_manager._tools
            fetch_tool = tools.get("web_fetch")
            assert fetch_tool is not None

            result = await fetch_tool.fn(url="https://example.com/small-page")

        assert result == small_content
        assert "truncated" not in result
