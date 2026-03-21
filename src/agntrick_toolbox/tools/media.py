"""Media processing tools: ffmpeg, imagemagick, etc."""

from mcp.server.fastmcp import FastMCP

from ..executor import run_command
from ..path_utils import PathValidationError, validate_output_path, validate_workspace_path


def register_media_tools(mcp: FastMCP) -> None:
    """Register all media processing tools."""

    @mcp.tool()
    async def ffmpeg_convert(
        input_path: str,
        output_path: str,
        codec: str | None = None,
        bitrate: str | None = None,
        start_time: str | None = None,
        duration: str | None = None,
        extra_args: str | None = None,
    ) -> str:
        """Convert audio/video files using ffmpeg.

        Args:
            input_path: Source media file path within workspace
            output_path: Destination file path within workspace
            codec: Output codec (e.g., 'libx264', 'aac', 'mp3')
            bitrate: Output bitrate (e.g., '128k', '1M')
            start_time: Start time for trimming (e.g., '00:01:30' or '90')
            duration: Duration to encode (e.g., '00:02:00' or '120')
            extra_args: Additional ffmpeg arguments

        Returns:
            Success message or error
        """
        try:
            in_path = validate_workspace_path(input_path)
            out_path = validate_output_path(output_path)
        except PathValidationError as e:
            return f"Error: {e}"

        cmd = ["ffmpeg", "-y", "-i", str(in_path)]

        if start_time:
            cmd.extend(["-ss", start_time])
        if duration:
            cmd.extend(["-t", duration])
        if codec:
            cmd.extend(["-c:v" if ":" not in codec else "-c", codec])
        if bitrate:
            cmd.extend(["-b:v" if ":" not in bitrate else "-b", bitrate])

        if extra_args:
            # Split extra args safely (basic implementation)
            import shlex

            cmd.extend(shlex.split(extra_args))

        cmd.append(str(out_path))

        result = await run_command(cmd, timeout=300)  # Longer timeout for media
        if not result.success:
            return f"Error: {result.stderr}"
        return f"Successfully converted {input_path} to {output_path}"

    @mcp.tool()
    async def imagemagick_convert(
        input_path: str,
        output_path: str,
        resize: str | None = None,
        quality: int | None = None,
        format: str | None = None,
        extra_args: str | None = None,
    ) -> str:
        """Convert and transform images using ImageMagick.

        Args:
            input_path: Source image file path within workspace
            output_path: Destination file path within workspace
            resize: Resize dimensions (e.g., '800x600', '50%', '800x600!')
            quality: Output quality 1-100 (for JPEG, WebP, etc.)
            format: Output format (e.g., 'png', 'jpg', 'webp', 'gif')
            extra_args: Additional ImageMagick arguments

        Returns:
            Success message or error
        """
        try:
            in_path = validate_workspace_path(input_path)
            out_path = validate_output_path(output_path)
        except PathValidationError as e:
            return f"Error: {e}"

        cmd = ["convert", str(in_path)]

        if resize:
            cmd.extend(["-resize", resize])
        if quality is not None:
            cmd.extend(["-quality", str(quality)])
        if format:
            cmd.extend(["-format", format])

        if extra_args:
            import shlex

            cmd.extend(shlex.split(extra_args))

        cmd.append(str(out_path))

        result = await run_command(cmd, timeout=120)
        if not result.success:
            return f"Error: {result.stderr}"
        return f"Successfully converted {input_path} to {output_path}"
