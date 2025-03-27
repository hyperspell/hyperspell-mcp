# syntax=docker/dockerfile:1
# check=skip=SecretsUsedInArgOrEnv

# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Install uv
RUN pip install uv

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

# Copy dependencies and install dependencies **as non-root**
COPY pyproject.toml /app
COPY README.md /app
COPY uv.lock /app
COPY src /app/src

RUN uv pip install --system -e .

RUN useradd -m -s /bin/bash appuser
USER appuser

ENV HYPERSPELL_TOKEN="<user-or-app-token>"

# Run the MCP server
ENTRYPOINT ["python", "-m", "hyperspell_mcp"]
