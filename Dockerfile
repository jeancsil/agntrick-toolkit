# agntrick-toolbox Dockerfile
# Docker-based MCP server providing curated CLI tools for LLM agents

FROM python:3.12-slim-bookworm

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for Phase A tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Document tools
    pandoc \
    poppler-utils \
    # Media tools
    ffmpeg \
    imagemagick \
    # Data tools
    jq \
    yq \
    # Search tools
    ripgrep \
    fd-find \
    # Utils
    curl \
    wget \
    git \
    # Build tools
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for fd (installed as fdfind on Debian)
RUN ln -sf /usr/bin/fdfind /usr/local/bin/fd

# Install Python package
WORKDIR /app
COPY pyproject.toml .
COPY src/ ./src/
RUN pip install --no-cache-dir -e .

# Create non-root user and workspace
RUN useradd -m -u 1000 toolbox && \
    mkdir -p /workspace && \
    chown toolbox:toolbox /workspace

# Configure ImageMagick policy (allow all operations)
RUN sed -i 's/rights="none" pattern="PDF"/rights="read|write" pattern="PDF"/' /etc/ImageMagick-6/policy.xml || true

USER toolbox
WORKDIR /workspace

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["toolbox-server"]
