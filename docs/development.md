# 开发指南

## 开发环境设置

### 前置要求

- Python 3.10+
- uv（推荐）或 pip

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd tennis-warehouse-mcp

# 使用 uv 安装依赖
uv sync

# 或使用 pip
pip install -e .
```

## 项目结构

```
tennis-warehouse-mcp/
├── src/                    # 源代码
│   ├── __init__.py
│   ├── main.py            # MCP 服务器入口
│   ├── api/               # API 模块
│   │   ├── __init__.py
│   │   ├── client.py      # API 客户端
│   │   └── parsers.py     # HTML 解析器
│   ├── tools/             # 工具模块
│   │   ├── __init__.py
│   │   ├── search_tools.py    # 搜索工具
│   │   ├── product_tools.py   # 产品工具
│   │   └── helpers.py         # 辅助函数
│   └── utils/             # 工具模块
│       ├── __init__.py
│       ├── constants.py   # 常量定义
│       └── validators.py  # 输入验证
├── tests/                 # 测试
│   ├── __init__.py
│   ├── README.md
│   └── test_product_review.py
├── docs/                  # 文档
│   ├── README.md
│   ├── usage.md
│   ├── api.md
│   ├── tools.md
│   └── development.md
├── main.py               # 入口文件
├── pyproject.toml        # 项目配置
└── README.md             # 项目说明
```

## 代码规范

### 导入顺序

1. 标准库
2. 第三方库
3. 本地模块

```python
import sys
import os
from typing import Dict, Any

import requests
from bs4 import BeautifulSoup

from ..utils.constants import DEFAULT_TIMEOUT
from ..utils.validators import validate_url
```

### 命名规范

- 类名：`PascalCase`
- 函数名：`snake_case`
- 常量：`UPPER_SNAKE_CASE`
- 私有方法：`_leading_underscore`

### 文档字符串

使用 Google 风格的 docstring：

```python
def search_products(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    """搜索产品
    
    Args:
        query: 搜索关键词
        max_results: 最大结果数
        
    Returns:
        产品列表
        
    Raises:
        ValueError: 如果查询为空
    """
    pass
```

## 添加新功能

### 1. 添加新的 API 方法

在 `src/api/client.py` 中添加方法：

```python
def get_product_images(self, product_url: str) -> List[str]:
    """获取产品图片"""
    # 实现逻辑
    pass
```

### 2. 添加新的工具函数

在 `src/tools/product_tools.py` 中添加函数：

```python
def get_product_images(tw_api: TennisWarehouseAPI, product_url: str) -> List[str]:
    """获取产品图片"""
    return tw_api.get_product_images(product_url)
```

### 3. 注册 MCP 工具

在 `src/main.py` 中注册：

```python
@mcp.tool()
def get_images(product_url: str) -> List[str]:
    """获取产品图片
    
    Args:
        product_url: 产品页面 URL
        
    Returns:
        图片 URL 列表
    """
    return get_product_images(tw_api, product_url)
```

### 4. 添加测试

在 `tests/` 中创建测试文件：

```python
# tests/test_product_images.py
from src.api import TennisWarehouseAPI

def test_get_product_images():
    api = TennisWarehouseAPI()
    images = api.get_product_images(test_url)
    assert len(images) > 0
```

### 5. 更新文档

在 `docs/` 中更新相关文档。

## 测试

### 运行测试

```bash
# 运行所有测试
uv run python -m pytest tests/

# 运行单个测试
uv run python tests/test_product_review.py

# 带详细输出
uv run python -m pytest tests/ -v
```

### 编写测试

```python
import pytest
from src.api import TennisWarehouseAPI

def test_search_products():
    api = TennisWarehouseAPI()
    result = api.search_products("wilson", limit=5)
    assert "html_content" in result
```

## 调试

### 启用详细日志

```python
import sys

# 在 main.py 中
print("Debug info", file=sys.stderr)
```

### 使用 Python 调试器

```python
import pdb

# 设置断点
pdb.set_trace()
```

## 发布

### 版本号

在 `pyproject.toml` 中更新版本：

```toml
[project]
version = "0.3.0"
```

### 构建

```bash
uv build
```

## 贡献指南

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 常见问题

### 导入错误

确保使用 `uv run` 或激活虚拟环境：

```bash
source .venv/bin/activate
```

### BeautifulSoup 解析失败

检查 HTML 结构是否变化，更新选择器。

### API 超时

调整超时设置：

```bash
export TW_API_TIMEOUT=30
```
