#!/bin/bash
if pgrep -f "uv.*tennis-warehouse-mcp.*main.py" > /dev/null; then
  echo "Tennis process is running"
else
  echo "Tennis process is NOT running"
fi
