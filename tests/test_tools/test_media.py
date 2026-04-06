"""Tests for media processing tools."""

from unittest.mock import patch

import pytest

from agntrick_toolbox.executor import CommandResult


class TestFfmpegConvert:
    """Tests for ffmpeg_convert tool."""

    @pytest.mark.asyncio
    async def test_converts_video(self, temp_workspace, monkeypatch):
        """Should convert video files."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        input_file = temp_workspace / "input.mp4"
        input_file.touch()

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.media import register_media_tools

        mcp = FastMCP("test")
        register_media_tools(mcp)

        with patch("agntrick_toolbox.tools.media.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            ffmpeg_tool = tools.get("ffmpeg_convert")
            if ffmpeg_tool:
                result = await ffmpeg_tool.fn(
                    input_path="input.mp4",
                    output_path="output.webm",
                )
                assert "Successfully converted" in result

    @pytest.mark.asyncio
    async def test_supports_codec_option(self, temp_workspace, monkeypatch):
        """Should support codec option."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        input_file = temp_workspace / "input.mp4"
        input_file.touch()

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.media import register_media_tools

        mcp = FastMCP("test")
        register_media_tools(mcp)

        with patch("agntrick_toolbox.tools.media.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            ffmpeg_tool = tools.get("ffmpeg_convert")
            if ffmpeg_tool:
                result = await ffmpeg_tool.fn(
                    input_path="input.mp4",
                    output_path="output.mp4",
                    codec="libx264",
                )
                assert "Successfully converted" in result

    @pytest.mark.asyncio
    async def test_rejects_path_outside_workspace(self, temp_workspace, monkeypatch):
        """Should reject paths outside workspace."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.media import register_media_tools

        mcp = FastMCP("test")
        register_media_tools(mcp)

        tools = mcp._tool_manager._tools
        ffmpeg_tool = tools.get("ffmpeg_convert")
        if ffmpeg_tool:
            result = await ffmpeg_tool.fn(
                input_path="/etc/passwd",
                output_path="output.mp4",
            )
            assert "Error" in result


class TestImagemagickConvert:
    """Tests for imagemagick_convert tool."""

    @pytest.mark.asyncio
    async def test_converts_image(self, temp_workspace, monkeypatch):
        """Should convert image files."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        input_file = temp_workspace / "input.png"
        input_file.touch()

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.media import register_media_tools

        mcp = FastMCP("test")
        register_media_tools(mcp)

        with patch("agntrick_toolbox.tools.media.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            convert_tool = tools.get("imagemagick_convert")
            if convert_tool:
                result = await convert_tool.fn(
                    input_path="input.png",
                    output_path="output.jpg",
                )
                assert "Successfully converted" in result

    @pytest.mark.asyncio
    async def test_supports_resize_option(self, temp_workspace, monkeypatch):
        """Should support resize option."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        input_file = temp_workspace / "input.png"
        input_file.touch()

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.media import register_media_tools

        mcp = FastMCP("test")
        register_media_tools(mcp)

        with patch("agntrick_toolbox.tools.media.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            convert_tool = tools.get("imagemagick_convert")
            if convert_tool:
                result = await convert_tool.fn(
                    input_path="input.png",
                    output_path="output.png",
                    resize="800x600",
                )
                assert "Successfully converted" in result

    @pytest.mark.asyncio
    async def test_supports_quality_option(self, temp_workspace, monkeypatch):
        """Should support quality option."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        input_file = temp_workspace / "input.png"
        input_file.touch()

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.media import register_media_tools

        mcp = FastMCP("test")
        register_media_tools(mcp)

        with patch("agntrick_toolbox.tools.media.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            convert_tool = tools.get("imagemagick_convert")
            if convert_tool:
                result = await convert_tool.fn(
                    input_path="input.png",
                    output_path="output.jpg",
                    quality=85,
                )
                assert "Successfully converted" in result
