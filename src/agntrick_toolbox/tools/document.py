"""Document processing tools: PDF, pandoc, etc."""

from mcp.server.fastmcp import FastMCP

from ..executor import run_command
from ..path_utils import PathValidationError, validate_output_path, validate_workspace_path


def register_document_tools(mcp: FastMCP) -> None:
    """Register all document processing tools."""

    @mcp.tool()
    async def pdf_extract_text(
        input_path: str,
        pages: str = "all",
        layout: bool = True,
    ) -> str:
        """Extract text from a PDF file.

        Args:
            input_path: Path to PDF file within workspace
            pages: Page range (e.g., '1-5', '1,3,5', 'all')
            layout: Preserve original layout

        Returns:
            Extracted text content or error message
        """
        try:
            validated = validate_workspace_path(input_path)
        except PathValidationError as e:
            return f"Error: {e}"

        cmd = ["pdftotext"]
        if layout:
            cmd.append("-layout")
        if pages != "all":
            if "-" in pages:
                parts = pages.split("-", 1)
                cmd.extend(["-f", parts[0].strip(), "-l", parts[1].strip()])
            else:
                cmd.extend(["-f", pages, "-l", pages])
        cmd.extend([str(validated), "-"])

        result = await run_command(cmd)
        if not result.success:
            return f"Error: {result.stderr}"
        return result.stdout

    @mcp.tool()
    async def pandoc_convert(
        input_path: str,
        output_path: str,
        from_format: str = "markdown",
        to_format: str = "html",
    ) -> str:
        """Convert documents between formats using pandoc.

        Supported formats: markdown, html, docx, pdf, rst, latex, etc.

        Args:
            input_path: Source file path within workspace
            output_path: Destination file path within workspace
            from_format: Input format (markdown, html, docx, pdf, etc.)
            to_format: Output format

        Returns:
            Success message or error
        """
        try:
            in_path = validate_workspace_path(input_path)
            out_path = validate_output_path(output_path)
        except PathValidationError as e:
            return f"Error: {e}"

        cmd = [
            "pandoc",
            str(in_path),
            "-f",
            from_format,
            "-t",
            to_format,
            "-o",
            str(out_path),
        ]

        result = await run_command(cmd)
        if not result.success:
            return f"Error: {result.stderr}"
        return f"Successfully converted {input_path} to {output_path}"
