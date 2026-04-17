"""Utility tools: curl, wget, compression, etc."""

from mcp.server.fastmcp import FastMCP

from ..config import settings
from ..executor import run_command
from ..path_utils import PathValidationError, validate_output_path


def register_utils_tools(mcp: FastMCP) -> None:
    """Register all utility tools."""

    @mcp.tool()
    async def curl_fetch(
        url: str,
        output_path: str | None = None,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        data: str | None = None,
        follow_redirects: bool = True,
        timeout: int = 60,
    ) -> str:
        """Raw HTTP client using curl — for API calls and custom HTTP requests.

        USE FOR: calling REST APIs, making POST/PUT/DELETE requests, setting
        custom headers, downloading files to disk, checking API status codes.
        DO NOT USE FOR: reading web page content (use web_fetch which extracts
        clean text), searching for information (use web_search), paywalled sites
        (delegate to paywall-remover agent).

        Args:
            url: URL to fetch
            output_path: Save response to file within workspace (optional)
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            headers: HTTP headers as key-value pairs
            data: Request body data
            follow_redirects: Follow HTTP redirects
            timeout: Request timeout in seconds

        Returns:
            Response body or error message
        """
        cmd = ["curl", "-s", "-X", method]

        if follow_redirects:
            cmd.append("-L")

        if headers:
            for key, value in headers.items():
                cmd.extend(["-H", f"{key}: {value}"])

        if data:
            cmd.extend(["-d", data])

        if output_path:
            try:
                validated = validate_output_path(output_path)
                cmd.extend(["-o", str(validated)])
            except PathValidationError as e:
                return f"Error: {e}"

        cmd.append(url)

        result = await run_command(cmd, timeout=timeout)
        if not result.success:
            return f"Error: {result.stderr}"

        if output_path:
            return f"Successfully saved {url} to {output_path}"

        # Truncate response body if too large
        text = result.stdout
        max_size = settings.toolbox_web_response_max_size
        if len(text) > max_size:
            original_len = len(text)
            text = (
                text[:max_size]
                + f"\n\n[Response truncated at {max_size} chars. "
                + f"Original size: {original_len} chars]"
            )

        return text

    @mcp.tool()
    async def wget_download(
        url: str,
        output_path: str | None = None,
        resume: bool = False,
        timeout: int = 60,
    ) -> str:
        """Download files using wget with resume support.

        Args:
            url: URL to download
            output_path: Save file to path within workspace (optional)
            resume: Resume interrupted download
            timeout: Download timeout in seconds

        Returns:
            Success message or error
        """
        cmd = ["wget", "-q"]

        if resume:
            cmd.append("-c")

        if output_path:
            try:
                validated = validate_output_path(output_path)
                cmd.extend(["-O", str(validated)])
            except PathValidationError as e:
                return f"Error: {e}"

        cmd.append(url)

        result = await run_command(cmd, timeout=timeout)
        if not result.success:
            return f"Error: {result.stderr}"

        dest = output_path or url.split("/")[-1]
        return f"Successfully downloaded {url} to {dest}"
