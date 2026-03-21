"""Search tools: ripgrep, fd, etc."""

from mcp.server.fastmcp import FastMCP

from ..config import settings
from ..executor import run_command
from ..path_utils import PathValidationError, validate_workspace_path


def register_search_tools(mcp: FastMCP) -> None:
    """Register all search tools."""

    @mcp.tool()
    async def ripgrep_search(
        pattern: str,
        path: str = ".",
        case_insensitive: bool = False,
        file_pattern: str | None = None,
        max_results: int = 100,
        show_line_numbers: bool = True,
    ) -> str:
        """Search file contents using ripgrep (rg).

        Fast regex search through files.

        Args:
            pattern: Search pattern (regex supported)
            path: Directory or file to search within workspace
            case_insensitive: Case insensitive search
            file_pattern: Glob pattern to filter files (e.g., '*.py', '*.md')
            max_results: Maximum number of results to return
            show_line_numbers: Show line numbers in output

        Returns:
            Search results or error message
        """
        try:
            validated = validate_workspace_path(path)
        except PathValidationError as e:
            return f"Error: {e}"

        cmd = ["rg"]

        if case_insensitive:
            cmd.append("-i")

        if show_line_numbers:
            cmd.append("-n")

        if file_pattern:
            cmd.extend(["-g", file_pattern])

        cmd.extend(["-m", str(max_results)])
        cmd.append(pattern)
        cmd.append(str(validated))

        result = await run_command(cmd)
        if not result.success and result.exit_code != 1:  # exit code 1 = no matches
            return f"Error: {result.stderr}"

        return result.stdout or "No matches found"

    @mcp.tool()
    async def fd_find(
        pattern: str = "",
        path: str = ".",
        type: str | None = None,
        extension: str | None = None,
        max_depth: int | None = None,
        hidden: bool = False,
    ) -> str:
        """Find files and directories using fd.

        Fast, user-friendly alternative to find.

        Args:
            pattern: Search pattern (regex supported, empty matches all)
            path: Directory to search within workspace
            type: File type ('file', 'directory', 'symlink')
            extension: File extension to filter (e.g., 'py', 'md')
            max_depth: Maximum search depth
            hidden: Include hidden files

        Returns:
            List of matching paths or error message
        """
        try:
            validated = validate_workspace_path(path)
        except PathValidationError as e:
            return f"Error: {e}"

        cmd = ["fd"]

        if type:
            cmd.extend(["-t", type])
        if extension:
            cmd.extend(["-e", extension])
        if max_depth is not None:
            cmd.extend(["--max-depth", str(max_depth)])
        if hidden:
            cmd.append("-H")

        if pattern:
            cmd.append(pattern)

        cmd.append(str(validated))

        result = await run_command(cmd)
        if not result.success:
            return f"Error: {result.stderr}"

        return result.stdout or "No files found"
