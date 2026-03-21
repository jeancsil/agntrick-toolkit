"""Git version control tools."""

from mcp.server.fastmcp import FastMCP

from ..executor import run_command
from ..path_utils import PathValidationError, validate_workspace_path


def register_git_tools(mcp: FastMCP) -> None:
    """Register all git tools."""

    @mcp.tool()
    async def git_status(
        path: str = ".",
        short: bool = True,
        branch: bool = True,
    ) -> str:
        """Get git repository status.

        Args:
            path: Repository path within workspace
            short: Use short format output
            branch: Show branch information

        Returns:
            Git status output or error message
        """
        try:
            validated = validate_workspace_path(path)
        except PathValidationError as e:
            return f"Error: {e}"

        cmd = ["git", "-C", str(validated), "status"]

        if short:
            cmd.append("-s")

        if branch:
            cmd.append("-b")

        result = await run_command(cmd)
        if not result.success:
            return f"Error: {result.stderr}"

        return result.stdout or "Working tree clean"

    @mcp.tool()
    async def git_log(
        path: str = ".",
        count: int = 10,
        oneline: bool = True,
        author: str | None = None,
        since: str | None = None,
    ) -> str:
        """View git commit history.

        Args:
            path: Repository path within workspace
            count: Number of commits to show
            oneline: Use one-line format
            author: Filter by author
            since: Show commits since date (e.g., '2024-01-01', '2 weeks ago')

        Returns:
            Git log output or error message
        """
        try:
            validated = validate_workspace_path(path)
        except PathValidationError as e:
            return f"Error: {e}"

        cmd = ["git", "-C", str(validated), "log", f"-{count}"]

        if oneline:
            cmd.append("--oneline")

        if author:
            cmd.extend(["--author", author])

        if since:
            cmd.extend(["--since", since])

        result = await run_command(cmd)
        if not result.success:
            return f"Error: {result.stderr}"

        return result.stdout or "No commits found"
