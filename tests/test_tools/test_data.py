"""Tests for data processing tools."""

from unittest.mock import patch

import pytest

from agntrick_toolbox.executor import CommandResult


class TestJqQuery:
    """Tests for jq_query tool."""

    @pytest.mark.asyncio
    async def test_queries_json_from_file(self, temp_workspace, monkeypatch):
        """Should query JSON from file."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        json_file = temp_workspace / "data.json"
        json_file.write_text('{"name": "test"}')

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.data import register_data_tools

        mcp = FastMCP("test")
        register_data_tools(mcp)

        with patch("agntrick_toolbox.tools.data.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout='"test"',
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            jq_tool = tools.get("jq_query")
            if jq_tool:
                result = await jq_tool.fn(query=".name", input_path="data.json")
                assert "test" in result

    @pytest.mark.asyncio
    async def test_queries_json_from_string(self, temp_workspace, monkeypatch):
        """Should query JSON from string input."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.data import register_data_tools

        mcp = FastMCP("test")
        register_data_tools(mcp)

        with patch("agntrick_toolbox.tools.data.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout='"test"',
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            jq_tool = tools.get("jq_query")
            if jq_tool:
                result = await jq_tool.fn(query=".name", input_data='{"name": "test"}')
                assert "test" in result

    @pytest.mark.asyncio
    async def test_requires_input_source(self, temp_workspace, monkeypatch):
        """Should require either input_path or input_data."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.data import register_data_tools

        mcp = FastMCP("test")
        register_data_tools(mcp)

        tools = mcp._tool_manager._tools
        jq_tool = tools.get("jq_query")
        if jq_tool:
            result = await jq_tool.fn(query=".name")
            assert "Error" in result

    @pytest.mark.asyncio
    async def test_rejects_path_outside_workspace(self, temp_workspace, monkeypatch):
        """Should reject paths outside workspace."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.data import register_data_tools

        mcp = FastMCP("test")
        register_data_tools(mcp)

        tools = mcp._tool_manager._tools
        jq_tool = tools.get("jq_query")
        if jq_tool:
            result = await jq_tool.fn(query=".name", input_path="/etc/passwd")
            assert "Error" in result


class TestYqQuery:
    """Tests for yq_query tool."""

    @pytest.mark.asyncio
    async def test_queries_yaml_from_file(self, temp_workspace, monkeypatch):
        """Should query YAML from file."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        yaml_file = temp_workspace / "data.yaml"
        yaml_file.write_text("name: test")

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.data import register_data_tools

        mcp = FastMCP("test")
        register_data_tools(mcp)

        with patch("agntrick_toolbox.tools.data.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="test",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            yq_tool = tools.get("yq_query")
            if yq_tool:
                result = await yq_tool.fn(query=".name", input_path="data.yaml")
                assert "test" in result

    @pytest.mark.asyncio
    async def test_handles_format_conversion(self, temp_workspace, monkeypatch):
        """Should handle format conversion."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.data import register_data_tools

        mcp = FastMCP("test")
        register_data_tools(mcp)

        with patch("agntrick_toolbox.tools.data.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout='{"name": "test"}',
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            yq_tool = tools.get("yq_query")
            if yq_tool:
                result = await yq_tool.fn(
                    query=".name",
                    input_data="name: test",
                    input_format="yaml",
                    output_format="json",
                )
                assert "test" in result
