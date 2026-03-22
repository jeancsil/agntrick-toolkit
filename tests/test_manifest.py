"""Tests for tool manifest."""



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
