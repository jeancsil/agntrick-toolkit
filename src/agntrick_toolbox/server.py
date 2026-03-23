"""FastMCP server entry point for agntrick-toolbox."""

import logging

from mcp.server.fastmcp import FastMCP

from .config import settings
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


def main() -> None:
    """Start the MCP server using FastMCP's built-in SSE server."""
    import uvicorn

    logger.info(f"Starting agntrick-toolbox on port {settings.toolbox_port}")
    logger.info(f"Workspace: {settings.toolbox_workspace}")
    logger.info(f"Shell fallback enabled: {settings.toolbox_shell_enabled}")

    # Run the SSE app directly using uvicorn
    # This avoids Starlette Mount routing issues
    uvicorn.run(
        mcp.sse_app(),
        host="0.0.0.0",
        port=settings.toolbox_port,
        log_level=settings.toolbox_log_level.lower(),
    )


if __name__ == "__main__":
    main()
