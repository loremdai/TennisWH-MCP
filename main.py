#!/usr/bin/env python3
"""Tennis Warehouse MCP 服务器入口点

此文件提供向后兼容性，通过导入新的模块化结构来运行 MCP 服务器。
"""

# 导入并运行新的模块化主程序
from src.main import mcp

if __name__ == "__main__":
    mcp.run()
