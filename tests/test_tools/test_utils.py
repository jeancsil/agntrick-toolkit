"""Tests for utility tools."""

import pytest
from unittest.mock import patch

from agntrick_toolbox.executor import CommandResult


class TestCurlFetch:
    """Tests for curl_fetch tool."""

    @pytest.mark.asyncio
    async def test_fetches_url(self, temp_workspace, monkeypatch):
        """Should fetch URL and return content."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.utils import register_utils_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_utils_tools(mcp)

        with patch("agntrick_toolbox.tools.utils.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="<html>content</html>",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            curl_tool = tools.get("curl_fetch")
            if curl_tool:
                result = await curl_tool.fn(url="https://example.com")
                assert "content" in result

    @pytest.mark.asyncio
    async def test_saves_to_file(self, temp_workspace, monkeypatch):
        """Should save response to file."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.utils import register_utils_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_utils_tools(mcp)

        with patch("agntrick_toolbox.tools.utils.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            curl_tool = tools.get("curl_fetch")
            if curl_tool:
                result = await curl_tool.fn(
                    url="https://example.com",
                    output_path="response.html",
                )
                assert "Successfully saved" in result

    @pytest.mark.asyncio
    async def test_supports_post_method(self, temp_workspace, monkeypatch):
        """Should support POST method."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.utils import register_utils_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_utils_tools(mcp)

        with patch("agntrick_toolbox.tools.utils.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout='{"status": "ok"}',
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            curl_tool = tools.get("curl_fetch")
            if curl_tool:
                result = await curl_tool.fn(
                    url="https://api.example.com",
                    method="POST",
                    data='{"key": "value"}',
                )
                assert "ok" in result

    @pytest.mark.asyncio
    async def test_rejects_path_outside_workspace(self, temp_workspace, monkeypatch):
        """Should reject paths outside workspace."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.utils import register_utils_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_utils_tools(mcp)

        tools = mcp._tool_manager._tools
        curl_tool = tools.get("curl_fetch")
        if curl_tool:
            result = await curl_tool.fn(
                url="https://example.com",
                output_path="/tmp/response.html",
            )
            assert "Error" in result


    @pytest.mark.asyncio
    async def test_truncates_large_response(self, temp_workspace, monkeypatch):
        """Should truncate large response body."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.utils import register_utils_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_utils_tools(mcp)

        large_body = "A" * 25_000

        with patch("agntrick_toolbox.tools.utils.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout=large_body,
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            curl_tool = tools.get("curl_fetch")
            if curl_tool:
                result = await curl_tool.fn(url="https://example.com/huge")
                assert "Response truncated" in result
                assert len(result) < 25_000
                # Should contain first part of the original content
                assert result.startswith("A" * 100)

    @pytest.mark.asyncio
    async def test_no_truncation_for_file_output(self, temp_workspace, monkeypatch):
        """Should not truncate when saving to file."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.utils import register_utils_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_utils_tools(mcp)

        with patch("agntrick_toolbox.tools.utils.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            curl_tool = tools.get("curl_fetch")
            if curl_tool:
                result = await curl_tool.fn(
                    url="https://example.com/huge",
                    output_path="response.html",
                )
                assert "Successfully saved" in result
                assert "truncated" not in result


class TestWgetDownload:
    """Tests for wget_download tool."""

    @pytest.mark.asyncio
    async def test_downloads_file(self, temp_workspace, monkeypatch):
        """Should download file."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.utils import register_utils_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_utils_tools(mcp)

        with patch("agntrick_toolbox.tools.utils.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            wget_tool = tools.get("wget_download")
            if wget_tool:
                result = await wget_tool.fn(url="https://example.com/file.zip")
                assert "Successfully downloaded" in result

    @pytest.mark.asyncio
    async def test_supports_resume(self, temp_workspace, monkeypatch):
        """Should support resume option."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.utils import register_utils_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_utils_tools(mcp)

        with patch("agntrick_toolbox.tools.utils.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            wget_tool = tools.get("wget_download")
            if wget_tool:
                result = await wget_tool.fn(
                    url="https://example.com/file.zip",
                    resume=True,
                )
                assert "Successfully downloaded" in result
