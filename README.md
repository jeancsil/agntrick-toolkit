# agntrick-toolbox

A Docker-based MCP server providing a curated CLI tool collection for LLM agents. Single container image with **17 tools** exposed via MCP protocol, with shell fallback for additional commands.

## Features

- **Zero-friction setup**: `docker-compose up -d` and it's ready
- **High reliability**: Curated tool schemas for common use cases
- **Escape hatch**: Shell fallback for edge cases
- **Secure**: Path confinement, non-root container, read-only filesystem

## Quick Start

```bash
# Clone and start
git clone https://github.com/jeancsil/agntrick-toolbox.git
cd agntrick-toolbox
docker-compose up -d

# Verify it's running
curl http://localhost:8080/health
# Output: OK

# Or with custom config
TOOLBOX_TIMEOUT_DEFAULT=60 docker-compose up -d
```

## Available Tools (Phase A - Core)

### Document Processing
| Tool | Description |
|------|-------------|
| `pdf_extract_text` | Extract text from PDF files with page range support |
| `pandoc_convert` | Convert documents between formats (markdown, HTML, PDF, DOCX, etc.) |

### Data Processing
| Tool | Description |
|------|-------------|
| `jq_query` | Query and transform JSON data using jq |
| `yq_query` | Query and transform YAML/JSON/TOML/XML data using yq |

### Media Processing
| Tool | Description |
|------|-------------|
| `ffmpeg_convert` | Convert audio/video files with codec and bitrate options |
| `imagemagick_convert` | Convert and transform images (resize, quality, format) |

### Utilities
| Tool | Description |
|------|-------------|
| `curl_fetch` | Fetch URLs using curl with HTTP method support |
| `wget_download` | Download files using wget with resume support |

### Search
| Tool | Description |
|------|-------------|
| `ripgrep_search` | Search file contents using ripgrep (fast regex search) |
| `fd_find` | Find files and directories using fd |

### Version Control
| Tool | Description |
|------|-------------|
| `git_status` | Get git repository status |
| `git_log` | View git commit history |

### Web
| Tool | Description |
|------|-------------|
| `web_search` | Search the web using DuckDuckGo |
| `web_fetch` | Fetch and extract URL content via Jina Reader API |

### Hacker News
| Tool | Description |
|------|-------------|
| `hacker_news_top` | Get top stories from Hacker News |
| `hacker_news_item` | Get details of a specific HN item |

### Fallback
| Tool | Description |
|------|-------------|
| `run_shell` | Execute shell commands for tools not in curated set |
| `health_check` | Check if the toolbox server is healthy |

## HTTP API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check (returns `OK`) |
| `/sse` | GET | MCP SSE endpoint for tool calls |
| `/api/manifest` | GET | Tool manifest in JSON format |

## Configuration

Environment variables (set in `.env` or docker-compose):

| Variable | Default | Description |
|----------|---------|-------------|
| `TOOLBOX_PORT` | `8080` | HTTP server port |
| `TOOLBOX_TIMEOUT_DEFAULT` | `30` | Default execution timeout (seconds) |
| `TOOLBOX_SHELL_ENABLED` | `true` | Enable shell fallback tool |
| `TOOLBOX_LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `TOOLBOX_MAX_OUTPUT_SIZE` | `1048576` | Max output bytes (1MB) |
| `TOOLBOX_WEB_RESPONSE_MAX_SIZE` | `15000` | Max web fetch response chars |
| `TOOLBOX_WORKSPACE` | `./workspace` | Local workspace directory |

## Usage with agntrick

Add to your `.agntrick.yaml`:

```yaml
mcp_servers:
  - name: toolbox
    transport: sse
    url: http://localhost:8080/sse
```

## Example Tool Calls

```python
# Extract text from PDF
await mcp.call_tool("pdf_extract_text", {
    "input_path": "/workspace/document.pdf",
    "pages": "1-5"
})

# Convert markdown to HTML
await mcp.call_tool("pandoc_convert", {
    "input_path": "/workspace/readme.md",
    "output_path": "/workspace/readme.html",
    "from_format": "markdown",
    "to_format": "html"
})

# Query JSON data
await mcp.call_tool("jq_query", {
    "query": ".users[] | select(.active == true) | .name",
    "input_path": "/workspace/data.json"
})

# Search files
await mcp.call_tool("ripgrep_search", {
    "pattern": "TODO",
    "path": "/workspace/src",
    "file_pattern": "*.py"
})

# Run shell command (fallback)
await mcp.call_tool("run_shell", {
    "command": "ls -la /workspace",
    "timeout": 10
})
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/

# Run type checking
mypy src/
```

## Security

- **Path confinement**: All file operations are confined to `/workspace` directory
- **Non-root container**: Runs as user ID 1000
- **Read-only filesystem**: Root filesystem is read-only with tmpfs for /tmp
- **Shell safety**: Dangerous commands are blocked by pattern matching
- **Resource limits**: CPU and memory limits configured

## Building

```bash
# Build the image
docker build -t agntrick-toolbox:latest .

# Test locally
docker-compose up -d

# Verify health
curl http://localhost:8080/health
```

## Roadmap

Future phases will add:
- Phase B: More document tools (ghostscript, calibre, tesseract, ocrmypdf)
- Phase C: More data tools (csvkit, sqlite, duckdb, dasel)
- Phase D: Media optimization (optipng, jpegoptim, exiftool)
- Phase E: Network tools (ssh, scp, openssl, httpie)
- Sandboxed execution (Firejail/bubblewrap)
- Tool usage analytics
- Dynamic tool discovery

## License

MIT
