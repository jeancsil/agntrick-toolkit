"""Shell fallback tool for commands not in curated set."""

import re

from mcp.server.fastmcp import FastMCP

from ..config import settings
from ..executor import run_command


def register_shell_tool(mcp: FastMCP) -> None:
    """Register shell fallback tool if enabled."""

    if not settings.toolbox_shell_enabled:
        return

    # Dangerous command patterns (blocklist approach)
    dangerous_patterns = [
        # System destruction
        r"\brm\s+-rf\s+/",
        r"\brm\s+-rf\s+/*",
        r"\brm\s+-rf\s+~",
        r"\bmkfs\b",
        r"\bdd\s+.*of=/dev/",
        r"\b:()\s*\{\s*:\|:&\s*\}",  # Fork bomb
        # Privilege escalation
        r"\bsudo\b",
        r"\bsu\b",
        r"\bchmod\s+777\b",
        r"\bchown\b.*root",
        # Network exfiltration (basic patterns)
        r"\bcurl\b.*\|\s*sh",
        r"\bwget\b.*\|\s*sh",
        r"\bnc\b.*-e\s+/bin",
        # System modification
        r"\biptables\b",
        r"\bsystemctl\b",
        r"\binit\b",
    ]

    @mcp.tool()
    async def run_shell(
        command: str,
        timeout: int = 30,
    ) -> str:
        """Execute a shell command for tools not in curated set.

        Use sparingly - prefer curated tools when available.
        Commands are confined to /workspace directory.

        Args:
            command: Shell command to execute
            timeout: Timeout in seconds (max 300)

        Returns:
            Command output or error message
        """
        # Validate command against dangerous patterns
        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return "Error: Command blocked by security policy"

        # Cap timeout
        timeout = min(timeout, 300)

        result = await run_command(
            ["sh", "-c", command],
            timeout=timeout,
            cwd=settings.toolbox_workspace,
        )

        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]: {result.stderr}"
        if result.truncated:
            output += "\n[output truncated due to size limit]"

        return output
