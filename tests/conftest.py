"""Pytest fixtures for agntrick-toolbox tests."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_settings(temp_workspace, monkeypatch):
    """Mock settings with temporary workspace."""
    import agntrick_toolbox.config as config_module

    monkeypatch.setattr(
        config_module.settings,
        "toolbox_workspace",
        str(temp_workspace),
    )
    monkeypatch.setattr(
        config_module.settings,
        "toolbox_timeout_default",
        5,
    )
    yield config_module.settings
