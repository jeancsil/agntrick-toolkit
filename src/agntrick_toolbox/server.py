"""FastMCP server entry point for agntrick-toolbox."""

import logging

from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP

from .config import settings
from .manifest import ToolInfo, ToolManifest
from .tools.data import register_data_tools
from .tools.document import register_document_tools
from .tools.git import register_git_tools
from .tools.hackernews import register_hackernews_tools
from .tools.media import register_media_tools
from .tools.search import register_search_tools
from .tools.shell import register_shell_tool
from .tools.utils import register_utils_tools
from .tools.web import register_web_tools

logging.basicConfig(level=getattr(logging, settings.toolbox_log_level))
logger = logging.getLogger(__name__)

mcp = FastMCP("agntrick-toolbox")
app = FastAPI(title="agntrick-toolbox")


# Register all tools by category
register_document_tools(mcp)  # 2 tools: pdf_extract_text, pandoc_convert
register_data_tools(mcp)  # 2 tools: jq_query, yq_query
register_media_tools(mcp)  # 2 tools: ffmpeg_convert, imagemagick_convert
register_utils_tools(mcp)  # 2 tools: curl_fetch, wget_download
register_search_tools(mcp)  # 2 tools: ripgrep_search, fd_find
register_git_tools(mcp)  # 2 tools: git_status, git_log
register_shell_tool(mcp)  # 1 fallback tool: run_shell
register_web_tools(mcp)  # 2 tools: web_search, web_fetch
register_hackernews_tools(mcp)  # 2 tools: hacker_news_top, hacker_news_item


@mcp.tool()
async def health_check() -> str:
    """Check if the toolbox server is healthy.

    Returns:
        'OK' if server is running correctly
    """
    return "OK"


@mcp.tool()
async def list_tools() -> str:
    """List all available tools in the toolbox.

    Returns:
        JSON string with tool names and descriptions
    """
    import json

    tools = [
        # Document tools
        {"name": "pdf_extract_text", "category": "document", "description": "Extract PDF text"},
        {"name": "pandoc_convert", "category": "document", "description": "Convert documents"},
        # Data tools
        {"name": "jq_query", "category": "data", "description": "Query JSON data"},
        {"name": "yq_query", "category": "data", "description": "Query YAML/JSON/XML"},
        # Media tools
        {"name": "ffmpeg_convert", "category": "media", "description": "Convert A/V files"},
        {"name": "imagemagick_convert", "category": "media", "description": "Transform images"},
        # Utils tools
        {"name": "curl_fetch", "category": "utils", "description": "Fetch via curl"},
        {"name": "wget_download", "category": "utils", "description": "Download files"},
        # Search tools
        {"name": "ripgrep_search", "category": "search", "description": "Search contents"},
        {"name": "fd_find", "category": "search", "description": "Find files"},
        # Git tools
        {"name": "git_status", "category": "git", "description": "Get git status"},
        {"name": "git_log", "category": "git", "description": "View git history"},
        # Shell fallback
        {"name": "run_shell", "category": "shell", "description": "Run shell (fallback)"},
        # Web tools
        {"name": "web_search", "category": "web", "description": "Search web (DDG)"},
        {"name": "web_fetch", "category": "web", "description": "Fetch URL content"},
        # Hacker News tools
        {"name": "hacker_news_top", "category": "hackernews", "description": "HN top stories"},
        {"name": "hacker_news_item", "category": "hackernews", "description": "HN item details"},
    ]
    return json.dumps(tools, indent=2)


@app.get("/manifest")
async def get_manifest() -> ToolManifest:
    """Get tool manifest for dynamic prompt generation.

    Returns:
        ToolManifest with all available tools and their categories.
    """
    tools = [
        ToolInfo(name="pdf_extract_text", category="document", description="Extract PDF text"),
        ToolInfo(name="pandoc_convert", category="document", description="Convert documents"),
        ToolInfo(name="jq_query", category="data", description="Query JSON data"),
        ToolInfo(name="yq_query", category="data", description="Query YAML/JSON/XML"),
        ToolInfo(name="ffmpeg_convert", category="media", description="Convert A/V files"),
        ToolInfo(name="imagemagick_convert", category="media", description="Transform images"),
        ToolInfo(name="curl_fetch", category="utils", description="Fetch via curl"),
        ToolInfo(name="wget_download", category="utils", description="Download files"),
        ToolInfo(name="ripgrep_search", category="search", description="Search contents"),
        ToolInfo(name="fd_find", category="search", description="Find files"),
        ToolInfo(name="git_status", category="git", description="Get git status"),
        ToolInfo(name="git_log", category="git", description="View git history"),
        ToolInfo(name="run_shell", category="shell", description="Run shell (fallback)"),
        ToolInfo(name="web_search", category="web", description="Search web (DDG)"),
        ToolInfo(name="web_fetch", category="web", description="Fetch URL content"),
        ToolInfo(name="hacker_news_top", category="hackernews", description="HN top stories"),
        ToolInfo(name="hacker_news_item", category="hackernews", description="HN item details"),
    ]
    return ToolManifest(tools=tools)


def main() -> None:
    """Start the MCP server using FastMCP's built-in SSE server with FastAPI."""
    import uvicorn
    from starlette.applications import Starlette
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware
    from starlette.routing import Mount

    logger.info(f"Starting agntrick-toolbox on port {settings.toolbox_port}")
    logger.info(f"Workspace: {settings.toolbox_workspace}")
    logger.info(f"Shell fallback enabled: {settings.toolbox_shell_enabled}")

    # Create a combined app with SSE and FastAPI routes
    # SSE routes are merged directly, FastAPI is mounted to preserve context
    combined_app = Starlette(
        middleware=[
            Middleware(
                CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
            ),
        ],
        routes=[
            *mcp.sse_app().routes,  # SSE app routes: /sse, /messages
            Mount("/api", app=app),  # FastAPI routes at /api/manifest, etc.
        ],
    )

    uvicorn.run(
        combined_app,
        host="0.0.0.0",
        port=settings.toolbox_port,
        log_level=settings.toolbox_log_level.lower(),
    )


if __name__ == "__main__":
    main()
