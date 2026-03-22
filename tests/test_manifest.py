"""Tests for tool manifest."""

import pytest


class TestToolInfo:
    """Tests for ToolInfo model."""

    def test_tool_info_from_dict(self) -> None:
        """ToolInfo should be created from dict."""
        from agntrick_toolbox.manifest import ToolInfo

        data = {
            "name": "web_search",
            "category": "web",
            "description": "Search the web",
        }
        tool = ToolInfo.model_validate(data)
        assert tool.name == "web_search"
        assert tool.category == "web"
        assert tool.description == "Search the web"

    def test_tool_info_to_dict(self) -> None:
        """ToolInfo should serialize to dict."""
        from agntrick_toolbox.manifest import ToolInfo

        tool = ToolInfo(
            name="web_search",
            category="web",
            description="Search the web",
        )
        result = tool.model_dump()
        assert result["name"] == "web_search"
        assert result["category"] == "web"


class TestManifestEndpoint:
    """Tests for manifest MCP tool."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_manifest(self) -> None:
        """list_tools should return a valid manifest."""
        from agntrick_toolbox.server import mcp

        tools = mcp._tool_manager._tools
        list_tools = tools.get("list_tools")
        assert list_tools is not None

        result = await list_tools.fn()
        import json

        manifest = json.loads(result)

        assert "tools" in manifest or isinstance(manifest, list)
        # Should include the new web tools
        tools_list = manifest if isinstance(manifest, list) else manifest.get("tools", [])
        tool_names = [t["name"] if isinstance(t, dict) else t for t in tools_list]
        assert "web_search" in tool_names
        assert "hacker_news_top" in tool_names


class TestToolManifest:
    """Tests for ToolManifest model."""

    def test_manifest_from_tools(self) -> None:
        """ToolManifest should be created from tool list."""
        from agntrick_toolbox.manifest import ToolInfo, ToolManifest

        tools = [
            ToolInfo(name="web_search", category="web", description="Search"),
            ToolInfo(name="web_fetch", category="web", description="Fetch"),
        ]
        manifest = ToolManifest(tools=tools)
        assert len(manifest.tools) == 2
        assert manifest.version == "1.0.0"

    def test_get_tools_by_category(self) -> None:
        """ToolManifest should filter by category."""
        from agntrick_toolbox.manifest import ToolInfo, ToolManifest

        tools = [
            ToolInfo(name="web_search", category="web", description="Search"),
            ToolInfo(name="git_status", category="git", description="Status"),
        ]
        manifest = ToolManifest(tools=tools)
        web_tools = manifest.get_tools_by_category("web")
        assert len(web_tools) == 1
        assert web_tools[0].name == "web_search"
