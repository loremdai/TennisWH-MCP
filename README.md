# Tennis Warehouse MCP Server

[English](#english) | [中文](#chinese)

---

## English

### Overview

Tennis Warehouse MCP Server is a Model Context Protocol (MCP) server that provides LLMs with access to Tennis Warehouse product data, including product search, specifications, and reviews.

### Features

- **Product Search**: Search for tennis products by keyword, category, or brand
- **Detailed Specifications**: Extract technical specifications from product pages
- **Review Data**: Get performance ratings and playtester feedback
- **Specialized Search**: Dedicated search for racquets, bags, and shoes
- **Deal Finder**: Discover discounted products
- **Smart Search**: Intelligent search with filtering suggestions

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd tennis-warehouse-mcp

# Install dependencies
uv sync
```

### Usage

#### Start the MCP Server

```bash
# Method 1: Using the launch script
./run_mcp.sh

# Method 2: Direct execution
uv run python main.py
```

#### Available Tools

The server provides 11 MCP tools:

1. `search_products` - Search tennis products
2. `get_specs` - Get product specifications
3. `get_review` - Get product reviews
4. `search_bags` - Search tennis bags
5. `search_racquets` - Search tennis racquets
6. `search_shoes` - Search tennis shoes
7. `get_categories` - Get product categories
8. `check_availability` - Check product stock
9. `get_deals` - Find discounted products
10. `smart_search` - Intelligent search
11. `handle_option` - Handle search options

### Project Structure

```
tennis-warehouse-mcp/
├── src/           # Source code
│   ├── api/       # API client and parsers
│   ├── tools/     # MCP tool functions
│   └── utils/     # Utilities and constants
├── tests/         # Test scripts
├── docs/          # Documentation
└── main.py        # Entry point
```

### Documentation

- [Usage Guide](docs/usage.md) - Detailed usage instructions
- [API Documentation](docs/api.md) - API module reference
- [Tools Documentation](docs/tools.md) - MCP tools reference
- [Development Guide](docs/development.md) - Development and contribution guide

### Testing

```bash
# Run tests
uv run python tests/test_product_review.py
```

### Configuration

Environment variables:

- `TW_API_TIMEOUT` - API timeout in seconds (default: 10)
- `TW_MAX_RESULTS` - Maximum results (default: 20)

### Requirements

- Python 3.10+
- uv (recommended) or pip

### License

MIT License - see [LICENSE](LICENSE) file for details.

This project is based on and extends the original Tennis Warehouse MCP implementation.

---

## Chinese

### 概述

Tennis Warehouse MCP 服务器是一个模型上下文协议（MCP）服务器，为大语言模型提供访问 Tennis Warehouse 产品数据的能力，包括产品搜索、规格查询和评测数据。

### 功能特性

- **产品搜索**：通过关键词、分类或品牌搜索网球产品
- **详细规格**：从产品页面提取技术规格参数
- **评测数据**：获取性能评分和测试员反馈
- **专业搜索**：针对球拍、球包和球鞋的专用搜索
- **优惠查找**：发现促销产品
- **智能搜索**：带过滤建议的智能搜索

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd tennis-warehouse-mcp

# 安装依赖
uv sync
```

### 使用方法

#### 启动 MCP 服务器

```bash
# 方式 1：使用启动脚本
./run_mcp.sh

# 方式 2：直接运行
uv run python main.py
```

#### 可用工具

服务器提供 11 个 MCP 工具：

1. `search_products` - 搜索网球产品
2. `get_specs` - 获取产品规格
3. `get_review` - 获取产品评测
4. `search_bags` - 搜索网球包
5. `search_racquets` - 搜索网球拍
6. `search_shoes` - 搜索网球鞋
7. `get_categories` - 获取产品分类
8. `check_availability` - 检查产品库存
9. `get_deals` - 查找优惠产品
10. `smart_search` - 智能搜索
11. `handle_option` - 处理搜索选项

### 项目结构

```
tennis-warehouse-mcp/
├── src/           # 源代码
│   ├── api/       # API 客户端和解析器
│   ├── tools/     # MCP 工具函数
│   └── utils/     # 工具和常量
├── tests/         # 测试脚本
├── docs/          # 文档
└── main.py        # 入口文件
```

### 文档

- [使用指南](docs/usage.md) - 详细使用说明
- [API 文档](docs/api.md) - API 模块参考
- [工具文档](docs/tools.md) - MCP 工具参考
- [开发指南](docs/development.md) - 开发和贡献指南

### 测试

```bash
# 运行测试
uv run python tests/test_product_review.py
```

### 配置

环境变量：

- `TW_API_TIMEOUT` - API 超时时间（秒），默认值：10
- `TW_MAX_RESULTS` - 最大结果数，默认值：20

### 系统要求

- Python 3.10+
- uv（推荐）或 pip

### 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

本项目基于原始的 Tennis Warehouse MCP 实现进行扩展和改进。