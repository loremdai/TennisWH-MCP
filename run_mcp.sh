#!/bin/bash
# Tennis Warehouse MCP Server Launcher
cd "$(dirname "$0")"
uv run python main.py "$@"