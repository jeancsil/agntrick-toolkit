"""Workspace path validation for security."""

import os
from pathlib import Path

from .config import settings


class PathValidationError(ValueError):
    """Raised when a path is outside the workspace."""


def validate_workspace_path(input_path: str) -> Path:
    """Validate that a path is within the workspace directory.

    Args:
        input_path: User-provided path (absolute or relative)

    Returns:
        Resolved absolute Path within workspace

    Raises:
        PathValidationError: If path escapes workspace
    """
    workspace = Path(settings.toolbox_workspace).resolve()

    # Handle relative vs absolute paths
    if os.path.isabs(input_path):
        target = Path(input_path).resolve()
    else:
        target = (workspace / input_path).resolve()

    # Check if target is within workspace (handles symlinks)
    try:
        target.relative_to(workspace)
    except ValueError:
        raise PathValidationError(
            f"Path '{input_path}' is outside workspace '{workspace}'. "
            "All file operations must be within /workspace."
        )

    return target


def validate_output_path(output_path: str) -> Path:
    """Validate and prepare an output path within workspace.

    Args:
        output_path: User-provided output path

    Returns:
        Validated Path for output

    Raises:
        PathValidationError: If path escapes workspace
    """
    validated = validate_workspace_path(output_path)

    # Ensure parent directory exists
    validated.parent.mkdir(parents=True, exist_ok=True)

    return validated
