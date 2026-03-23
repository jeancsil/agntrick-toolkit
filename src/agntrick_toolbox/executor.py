"""Async command execution with timeout and output limits."""

import asyncio
from dataclasses import dataclass

from .config import settings


@dataclass
class CommandResult:
    """Result of a command execution."""

    success: bool
    stdout: str
    stderr: str
    exit_code: int
    truncated: bool = False


async def run_command(
    cmd: list[str],
    timeout: int | None = None,
    input_data: str | None = None,
    cwd: str | None = None,
) -> CommandResult:
    """Execute a shell command with timeout and output limits.

    Args:
        cmd: Command and arguments as list
        timeout: Timeout in seconds (default from settings)
        input_data: Optional stdin input
        cwd: Working directory for command

    Returns:
        CommandResult with stdout, stderr, and status
    """
    timeout = timeout or settings.toolbox_timeout_default

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if input_data else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(input=input_data.encode() if input_data else None),
            timeout=timeout,
        )

        stdout_str = stdout.decode("utf-8", errors="replace")
        stderr_str = stderr.decode("utf-8", errors="replace")

        # Truncate if too large
        truncated = len(stdout_str) > settings.toolbox_max_output_size
        if truncated:
            stdout_str = stdout_str[: settings.toolbox_max_output_size] + "\n... [output truncated]"

        return CommandResult(
            success=process.returncode == 0,
            stdout=stdout_str,
            stderr=stderr_str,
            exit_code=process.returncode or 0,
            truncated=truncated,
        )

    except TimeoutError:
        return CommandResult(
            success=False,
            stdout="",
            stderr=f"Command timed out after {timeout} seconds",
            exit_code=-1,
        )
    except FileNotFoundError:
        return CommandResult(
            success=False,
            stdout="",
            stderr=f"Command not found: {cmd[0]}",
            exit_code=-1,
        )
    except Exception as e:
        return CommandResult(
            success=False,
            stdout="",
            stderr=f"Execution error: {e}",
            exit_code=-1,
        )
