"""Tests for document processing tools."""

from unittest.mock import patch

import pytest

from agntrick_toolbox.executor import CommandResult


class TestPdfExtractText:
    """Tests for pdf_extract_text tool."""

    @pytest.mark.asyncio
    async def test_extracts_text_successfully(self, temp_workspace, monkeypatch):
        """Should extract text from a valid PDF."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        # Create a mock PDF file
        pdf_path = temp_workspace / "test.pdf"
        pdf_path.touch()

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.document import register_document_tools

        mcp = FastMCP("test")
        register_document_tools(mcp)

        # Mock run_command
        with patch("agntrick_toolbox.tools.document.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="Extracted text content",
                stderr="",
                exit_code=0,
            )

            # Get the tool function and call it
            tools = mcp._tool_manager._tools
            pdf_tool = tools.get("pdf_extract_text")
            if pdf_tool:
                result = await pdf_tool.fn(input_path="test.pdf")
                assert "Extracted text content" in result

    @pytest.mark.asyncio
    async def test_rejects_path_outside_workspace(self, temp_workspace, monkeypatch):
        """Should reject paths outside workspace."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.document import register_document_tools

        mcp = FastMCP("test")
        register_document_tools(mcp)

        tools = mcp._tool_manager._tools
        pdf_tool = tools.get("pdf_extract_text")
        if pdf_tool:
            result = await pdf_tool.fn(input_path="/etc/passwd")
            assert "Error" in result
            assert "outside workspace" in result


class TestPandocConvert:
    """Tests for pandoc_convert tool."""

    @pytest.mark.asyncio
    async def test_converts_markdown_to_html(self, temp_workspace, monkeypatch):
        """Should convert markdown to HTML."""
        import agntrick_toolbox.path_utils as path_utils

        monkeypatch.setattr(path_utils.settings, "toolbox_workspace", str(temp_workspace))

        # Create input file
        input_file = temp_workspace / "test.md"
        input_file.write_text("# Hello")

        from mcp.server.fastmcp import FastMCP

        from agntrick_toolbox.tools.document import register_document_tools

        mcp = FastMCP("test")
        register_document_tools(mcp)

        with patch("agntrick_toolbox.tools.document.run_command") as mock_run:
            mock_run.return_value = CommandResult(
                success=True,
                stdout="",
                stderr="",
                exit_code=0,
            )

            tools = mcp._tool_manager._tools
            pandoc_tool = tools.get("pandoc_convert")
            if pandoc_tool:
                result = await pandoc_tool.fn(
                    input_path="test.md",
                    output_path="output.html",
                    from_format="markdown",
                    to_format="html",
                )
                assert "Successfully converted" in result
