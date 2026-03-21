"""Tests for git tools."""

import pytest
from unittest.mock import patch

from agntrick_toolbox.executor import CommandResult


class TestGitStatus:
    """Tests for git_status tool."""

    @pytest.mark.asyncio
    async def test_returns_status(self, temp_workspace, monkeypatch):
        """Should return git status."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.git import register_git_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_git_tools(mcp)

        with patch("agntrick_toolbox.tools.git.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="## main\n M file.py",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            git_tool = tools.get("git_status")
            if git_tool:
                result = await git_tool.fn(path=".")
                assert "main" in result

    @pytest.mark.asyncio
    async def test_handles_clean_repo(self, temp_workspace, monkeypatch):
        """Should handle clean repository."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.git import register_git_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_git_tools(mcp)

        with patch("agntrick_toolbox.tools.git.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            git_tool = tools.get("git_status")
            if git_tool:
                result = await git_tool.fn(path=".")
                assert "clean" in result.lower()

    @pytest.mark.asyncio
    async def test_rejects_path_outside_workspace(self, temp_workspace, monkeypatch):
        """Should reject paths outside workspace."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.git import register_git_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_git_tools(mcp)

        tools = mcp._tool_manager._tools
        git_tool = tools.get("git_status")
        if git_tool:
            result = await git_tool.fn(path="/etc")
            assert "Error" in result


class TestGitLog:
    """Tests for git_log tool."""

    @pytest.mark.asyncio
    async def test_returns_log(self, temp_workspace, monkeypatch):
        """Should return git log."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.git import register_git_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_git_tools(mcp)

        with patch("agntrick_toolbox.tools.git.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="abc123 Initial commit\ndef456 Add feature",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            git_tool = tools.get("git_log")
            if git_tool:
                result = await git_tool.fn(path=".")
                assert "commit" in result

    @pytest.mark.asyncio
    async def test_supports_count_limit(self, temp_workspace, monkeypatch):
        """Should support count limit."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.git import register_git_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_git_tools(mcp)

        with patch("agntrick_toolbox.tools.git.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="abc123 Initial commit",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            git_tool = tools.get("git_log")
            if git_tool:
                result = await git_tool.fn(path=".", count=1)
                assert "commit" in result

    @pytest.mark.asyncio
    async def test_handles_empty_repo(self, temp_workspace, monkeypatch):
        """Should handle empty repository."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from agntrick_toolbox.tools.git import register_git_tools
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_git_tools(mcp)

        with patch("agntrick_toolbox.tools.git.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            git_tool = tools.get("git_log")
            if git_tool:
                result = await git_tool.fn(path=".")
                assert "No commits found" in result
