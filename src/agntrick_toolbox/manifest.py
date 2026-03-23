"""Tool manifest models for capability discovery."""

from typing import Any

from pydantic import BaseModel


class ToolInfo(BaseModel):
    """Information about a single tool."""

    name: str
    category: str
    description: str
    parameters: dict[str, Any] | None = None
    examples: list[str] | None = None


class ToolManifest(BaseModel):
    """Complete tool manifest from toolbox server."""

    version: str = "1.0.0"
    tools: list[ToolInfo]

    def get_tools_by_category(self, category: str) -> list[ToolInfo]:
        """Get all tools in a category."""
        return [t for t in self.tools if t.category == category]

    def get_tool(self, name: str) -> ToolInfo | None:
        """Get a tool by name."""
        for tool in self.tools:
            if tool.name == name:
                return tool
        return None

    def get_categories(self) -> list[str]:
        """Get all unique categories."""
        return sorted(set(t.category for t in self.tools))
