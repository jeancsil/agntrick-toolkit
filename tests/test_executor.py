"""Tests for command execution module."""

import pytest

from agntrick_toolbox.executor import run_command


class TestRunCommand:
    """Tests for run_command function."""

    @pytest.mark.asyncio
    async def test_successful_command(self):
        """Should execute a successful command."""
        result = await run_command(["echo", "hello"])

        assert result.success is True
        assert "hello" in result.stdout
        assert result.exit_code == 0

    @pytest.mark.asyncio
    async def test_failed_command(self):
        """Should handle failed commands."""
        result = await run_command(["ls", "/nonexistent/path"])

        assert result.success is False
        assert result.exit_code != 0
        assert result.stderr != ""

    @pytest.mark.asyncio
    async def test_command_not_found(self):
        """Should handle command not found."""
        result = await run_command(["nonexistent_command_xyz"])

        assert result.success is False
        assert result.exit_code == -1
        assert "not found" in result.stderr.lower()

    @pytest.mark.asyncio
    async def test_command_with_input(self):
        """Should handle stdin input."""
        result = await run_command(["cat"], input_data="test input")

        assert result.success is True
        assert "test input" in result.stdout

    @pytest.mark.asyncio
    async def test_command_timeout(self, monkeypatch):
        """Should handle command timeout."""
        import agntrick_toolbox.executor as executor_module

        monkeypatch.setattr(executor_module.settings, "toolbox_timeout_default", 1)

        result = await run_command(["sleep", "10"])

        assert result.success is False
        assert "timed out" in result.stderr.lower()
        assert result.exit_code == -1

    @pytest.mark.asyncio
    async def test_custom_timeout(self):
        """Should respect custom timeout."""
        result = await run_command(["sleep", "5"], timeout=1)

        assert result.success is False
        assert "timed out" in result.stderr.lower()

    @pytest.mark.asyncio
    async def test_working_directory(self, tmp_path):
        """Should execute in specified working directory."""
        result = await run_command(["pwd"], cwd=str(tmp_path))

        assert result.success is True
        assert str(tmp_path) in result.stdout
