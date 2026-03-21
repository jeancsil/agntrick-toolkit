"""Tests for shell fallback tool."""

import pytest
from unittest.mock import patch

from agntrick_toolbox.executor import CommandResult


class TestRunShell:
    """Tests for run_shell tool."""

    @pytest.mark.asyncio
    async def test_executes_command(self, temp_workspace, monkeypatch):
        """Should execute shell command."""
        import agntrick_toolbox.path_utils as path_utils
        import agntrick_toolbox.config as config_module

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))
        monkeypatch.setattr(config_module.settings, "toolbox_shell_enabled", True)

        from agntrick_toolbox.tools.shell import register_shell_tool
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_shell_tool(mcp)

        with patch("agntrick_toolbox.tools.shell.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="file1.txt\nfile2.txt",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            shell_tool = tools.get("run_shell")
            if shell_tool:
                result = await shell_tool.fn(command="ls -la")
                assert "file" in result

    @pytest.mark.asyncio
    async def test_includes_stderr_in_output(self, temp_workspace, monkeypatch):
        """Should include stderr in output."""
        import agntrick_toolbox.path_utils as path_utils
        import agntrick_toolbox.config as config_module

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))
        monkeypatch.setattr(config_module.settings, "toolbox_shell_enabled", True)

        from agntrick_toolbox.tools.shell import register_shell_tool
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_shell_tool(mcp)

        with patch("agntrick_toolbox.tools.shell.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="output",
                stderr="warning message",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            shell_tool = tools.get("run_shell")
            if shell_tool:
                result = await shell_tool.fn(command="some_command")
                assert "stderr" in result
                assert "warning" in result

    @pytest.mark.asyncio
    async def test_blocks_dangerous_commands(self, temp_workspace, monkeypatch):
        """Should block dangerous commands."""
        import agntrick_toolbox.path_utils as path_utils
        import agntrick_toolbox.config as config_module

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))
        monkeypatch.setattr(config_module.settings, "toolbox_shell_enabled", True)

        from agntrick_toolbox.tools.shell import register_shell_tool
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_shell_tool(mcp)

        tools = mcp._tool_manager._tools
        shell_tool = tools.get("run_shell")
        if shell_tool:
            # Test rm -rf /
            result = await shell_tool.fn(command="rm -rf /")
            assert "blocked" in result.lower()

            # Test sudo
            result = await shell_tool.fn(command="sudo rm file")
            assert "blocked" in result.lower()

    @pytest.mark.asyncio
    async def test_can_be_disabled(self, temp_workspace, monkeypatch):
        """Should be able to disable shell tool."""
        import agntrick_toolbox.path_utils as path_utils
        import agntrick_toolbox.config as config_module

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))
        monkeypatch.setattr(config_module.settings, "toolbox_shell_enabled", False)

        from agntrick_toolbox.tools.shell import register_shell_tool
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_shell_tool(mcp)

        tools = mcp._tool_manager._tools
        shell_tool = tools.get("run_shell")
        # Tool should not be registered when disabled
        assert shell_tool is None

    @pytest.mark.asyncio
    async def test_caps_timeout(self, temp_workspace, monkeypatch):
        """Should cap timeout at 300 seconds."""
        import agntrick_toolbox.path_utils as path_utils
        import agntrick_toolbox.config as config_module

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))
        monkeypatch.setattr(config_module.settings, "toolbox_shell_enabled", True)

        from agntrick_toolbox.tools.shell import register_shell_tool
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register_shell_tool(mcp)

        with patch("agntrick_toolbox.tools.shell.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="done",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            shell_tool = tools.get("run_shell")
            if shell_tool:
                await shell_tool.fn(command="long_command", timeout=500)
                # Check that timeout was capped
                call_args = mock_run.call_args
                assert call_args[1]["timeout"] == 300
