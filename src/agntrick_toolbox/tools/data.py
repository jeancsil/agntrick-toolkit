"""Data processing tools: jq, yq, etc."""

from mcp.server.fastmcp import FastMCP

from ..executor import run_command
from ..path_utils import PathValidationError, validate_workspace_path


def register_data_tools(mcp: FastMCP) -> None:
    """Register all data processing tools."""

    @mcp.tool()
    async def jq_query(
        query: str,
        input_path: str | None = None,
        input_data: str | None = None,
        raw_output: bool = False,
    ) -> str:
        """Query and transform JSON data using jq.

        Args:
            query: jq filter expression
            input_path: Path to JSON file within workspace (optional)
            input_data: JSON string input (used if no input_path)
            raw_output: Output raw strings without quotes

        Returns:
            Query result or error message
        """
        if input_path:
            try:
                validated = validate_workspace_path(input_path)
            except PathValidationError as e:
                return f"Error: {e}"
        elif not input_data:
            return "Error: Either input_path or input_data must be provided"

        cmd = ["jq"]
        if raw_output:
            cmd.append("-r")
        cmd.append(query)

        if input_path:
            cmd.append(str(validated))
            result = await run_command(cmd)
        else:
            result = await run_command(cmd, input_data=input_data)

        if not result.success:
            return f"Error: {result.stderr}"
        return result.stdout

    @mcp.tool()
    async def yq_query(
        query: str,
        input_path: str | None = None,
        input_data: str | None = None,
        input_format: str = "yaml",
        output_format: str = "yaml",
    ) -> str:
        """Query and transform YAML/JSON/TOML/XML data using yq.

        Args:
            query: yq filter expression
            input_path: Path to file within workspace (optional)
            input_data: Data string input (used if no input_path)
            input_format: Input format (yaml, json, toml, xml, csv)
            output_format: Output format (yaml, json, toml, xml, csv)

        Returns:
            Query result or error message
        """
        if input_path:
            try:
                validated = validate_workspace_path(input_path)
            except PathValidationError as e:
                return f"Error: {e}"
        elif not input_data:
            return "Error: Either input_path or input_data must be provided"

        cmd = ["yq"]
        cmd.extend(["-p", input_format])
        cmd.extend(["-o", output_format])
        cmd.append(query)

        if input_path:
            cmd.append(str(validated))
            result = await run_command(cmd)
        else:
            result = await run_command(cmd, input_data=input_data)

        if not result.success:
            return f"Error: {result.stderr}"
        return result.stdout
