"""Tests for server module."""

import pytest
from unittest.mock import patch, MagicMock


class TestServerModule:
    """Tests for server module functions."""

    def test_imports_successfully(self):
        """Should import server module without errors."""
        from agntrick_toolbox import server
        assert server is not None

    def test_mcp_instance_created(self):
        """Should create FastMCP instance."""
        from agntrick_toolbox.server import mcp
        assert mcp is not None
        assert mcp.name == "agntrick-toolbox"

    def test_health_check_tool_registered(self):
        """Should register health_check tool."""
        from agntrick_toolbox.server import mcp
        tools = mcp._tool_manager._tools
        assert "health_check" in tools

    def test_list_tools_tool_registered(self):
        """Should register list_tools tool."""
        from agntrick_toolbox.server import mcp
        tools = mcp._tool_manager._tools
        assert "list_tools" in tools

    @pytest.mark.asyncio
    async def test_health_check_returns_ok(self):
        """Health check should return OK."""
        from agntrick_toolbox.server import mcp
        tools = mcp._tool_manager._tools
        health_tool = tools.get("health_check")
        if health_tool:
            result = await health_tool.fn()
            assert result == "OK"

    @pytest.mark.asyncio
    async def test_list_tools_returns_json(self):
        """list_tools should return JSON."""
        import json
        from agntrick_toolbox.server import mcp
        tools = mcp._tool_manager._tools
        list_tool = tools.get("list_tools")
        if list_tool:
            result = await list_tool.fn()
            # Should be valid JSON
            parsed = json.loads(result)
            assert isinstance(parsed, list)
            assert len(parsed) > 0
            # Each tool should have name and category
            for tool in parsed:
                assert "name" in tool
                assert "category" in tool

    def test_all_core_tools_registered(self):
        """Should register all core tools."""
        from agntrick_toolbox.server import mcp
        tools = mcp._tool_manager._tools

        expected_tools = [
            "pdf_extract_text",
            "pandoc_convert",
            "jq_query",
            "yq_query",
            "ffmpeg_convert",
            "imagemagick_convert",
            "curl_fetch",
            "wget_download",
            "ripgrep_search",
            "fd_find",
            "git_status",
            "git_log",
            "run_shell",
            "health_check",
            "list_tools",
        ]

        for tool_name in expected_tools:
            assert tool_name in tools, f"Tool {tool_name} not registered"


class TestMainFunction:
    """Tests for main function."""

    def test_main_starts_server(self, monkeypatch):
        """Main should start uvicorn server."""
        import agntrick_toolbox.config as config_module

        monkeypatch.setattr(config_module.settings, "toolbox_port", 8080)
        monkeypatch.setattr(config_module.settings, "toolbox_log_level", "INFO")

        # Mock uvicorn before importing main
        import sys
        from unittest.mock import MagicMock

        mock_uvicorn = MagicMock()
        sys.modules["uvicorn"] = mock_uvicorn

        # Reimport to get mocked uvicorn
        import importlib
        import agntrick_toolbox.server as server_module

        importlib.reload(server_module)

        # Call main
        server_module.main()

        # Verify uvicorn.run was called
        assert mock_uvicorn.run.called
        call_args = mock_uvicorn.run.call_args
        assert call_args[1]["host"] == "0.0.0.0"
        assert call_args[1]["port"] == 8080
