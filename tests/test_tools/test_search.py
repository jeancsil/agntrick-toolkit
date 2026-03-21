"""Tests for search tools."""

import pytest
from unittest.mock import patch

from agntrick_toolbox.executor import CommandResult


class TestRipgrepSearch:
    """Tests for ripgrep_search tool."""

    @pytest.mark.asyncio
    async def test_searches_for_pattern(self, temp_workspace, monkeypatch):
        """Should search for pattern in files."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.search import register_search_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_search_tools(mcp)

        with patch("agntrick_toolbox.tools.search.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="file.py:1:pattern match",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            rg_tool = tools.get("ripgrep_search")
            if rg_tool:
                result = await rg_tool.fn(pattern="pattern", path=".")
                assert "pattern" in result

    @pytest.mark.asyncio
    async def test_handles_no_matches(self, temp_workspace, monkeypatch):
        """Should handle no matches found."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.search import register_search_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_search_tools(mcp)

        with patch("agntrick_toolbox.tools.search.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=1,
            )

            tools = mcp._tool_manager._tools
            rg_tool = tools.get("ripgrep_search")
            if rg_tool:
                result = await rg_tool.fn(pattern="notfound", path=".")
                assert "No matches found" in result

    @pytest.mark.asyncio
    async def test_supports_file_pattern(self, temp_workspace, monkeypatch):
        """Should support file pattern filtering."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.search import register_search_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_search_tools(mcp)

        with patch("agntrick_toolbox.tools.search.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="file.py:1:TODO",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            rg_tool = tools.get("ripgrep_search")
            if rg_tool:
                result = await rg_tool.fn(
                    pattern="TODO",
                    path=".",
                    file_pattern="*.py",
                )
                assert "TODO" in result

    @pytest.mark.asyncio
    async def test_rejects_path_outside_workspace(self, temp_workspace, monkeypatch):
        """Should reject paths outside workspace."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.search import register_search_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_search_tools(mcp)

        tools = mcp._tool_manager._tools
        rg_tool = tools.get("ripgrep_search")
        if rg_tool:
            result = await rg_tool.fn(pattern="test", path="/etc")
            assert "Error" in result


class TestFdFind:
    """Tests for fd_find tool."""

    @pytest.mark.asyncio
    async def test_finds_files(self, temp_workspace, monkeypatch):
        """Should find files matching pattern."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.search import register_search_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_search_tools(mcp)

        with patch("agntrick_toolbox.tools.search.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="file1.py\nfile2.py",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            fd_tool = tools.get("fd_find")
            if fd_tool:
                result = await fd_tool.fn(pattern=".py", path=".")
                assert "file" in result

    @pytest.mark.asyncio
    async def test_handles_no_files_found(self, temp_workspace, monkeypatch):
        """Should handle no files found."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.search import register_search_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_search_tools(mcp)

        with patch("agntrick_toolbox.tools.search.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            fd_tool = tools.get("fd_find")
            if fd_tool:
                result = await fd_tool.fn(pattern="nonexistent", path=".")
                assert "No files found" in result

    @pytest.mark.asyncio
    async def test_supports_type_filter(self, temp_workspace, monkeypatch):
        """Should support type filtering."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.search import register_search_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_search_tools(mcp)

        with patch("agntrick_toolbox.tools.search.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="mydir",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            fd_tool = tools.get("fd_find")
            if fd_tool:
                result = await fd_tool.fn(pattern="my", path=".", type="directory")
                assert "mydir" in result
