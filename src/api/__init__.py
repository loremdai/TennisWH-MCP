"""API 模块

导出 Tennis Warehouse API 客户端和 HTML 解析器函数。
"""

from .client import TennisWarehouseAPI
from .parsers import (
    extract_products,
    extract_categories,
    extract_price_ranges,
    extract_search_insights,
)

__all__ = [
    "TennisWarehouseAPI",
    "extract_products",
    "extract_categories",
    "extract_price_ranges",
    "extract_search_insights",
]
