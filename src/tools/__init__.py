"""工具模块

导出所有 MCP 工具函数，包括搜索工具、产品工具和辅助函数。
"""

from .search_tools import (
    search_tennis_products,
    search_tennis_bags,
    search_tennis_racquets,
    search_tennis_shoes,
    smart_search_tennis,
    get_tennis_deals,
)

from .product_tools import (
    get_product_specs,
    get_product_review,
    get_product_categories,
    check_product_availability,
)

from .helpers import (
    generate_search_suggestions,
    handle_search_option,
)

__all__ = [
    # 搜索工具
    "search_tennis_products",
    "search_tennis_bags",
    "search_tennis_racquets",
    "search_tennis_shoes",
    "smart_search_tennis",
    "get_tennis_deals",
    # 产品工具
    "get_product_specs",
    "get_product_review",
    "get_product_categories",
    "check_product_availability",
    # 辅助函数
    "generate_search_suggestions",
    "handle_search_option",
]
