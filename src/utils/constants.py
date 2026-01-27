"""Tennis Warehouse MCP 服务器使用的常量定义

本模块包含整个项目中使用的所有常量，包括错误消息、默认值、
API 配置和产品分类等。
"""

# 错误消息常量
ERROR_INVALID_URL = "Invalid URL provided"
ERROR_URL_MUST_BE_TW = "URL must be from tennis-warehouse.com"
ERROR_TIMEOUT = "Request timed out"
ERROR_NO_SPECS = "No specifications found on this page"
ERROR_NO_REVIEW_DATA = "No review data found on this page"
ERROR_QUERY_TOO_SHORT = "Search query must be at least 2 characters"
ERROR_PRODUCT_NOT_FOUND = "Product not found"

# 默认值常量
DEFAULT_UNKNOWN_PRODUCT = "Unknown Product"
DEFAULT_UNKNOWN_BRAND = "Unknown Brand"
DEFAULT_PRICE_NOT_AVAILABLE = "Price not available"
DEFAULT_AVAILABILITY_UNKNOWN = "Unknown"

# HTML 解析配置
HTML_PARSER = "html.parser"

# API 配置常量
DEFAULT_TIMEOUT = 10  # 默认超时时间（秒）
DEFAULT_MAX_RESULTS = 20  # 默认最大结果数
MAX_SEARCH_RESULTS = 50  # 搜索结果上限

# 产品分类别名映射
# 用于将用户输入的分类名称映射到 Tennis Warehouse 的内部分类代码
CATEGORY_ALIASES = {
    "BAGS": "SHOULDBAGS",
    "BAG": "SHOULDBAGS",
    "MENS_SHOES": "MENSSHOES",
    "WOMENS_SHOES": "WOMENSSHOES",
    "MEN_SHOES": "MENSSHOES",
    "WOMEN_SHOES": "WOMENSSHOES",
}

# 产品分类静态列表
# 包含所有可用的产品分类及其代码和大致产品数量
PRODUCT_CATEGORIES = [
    {"name": "Racquets", "code": "RACQUETS", "count": "500+"},
    {"name": "Shoes", "code": "SHOES", "count": "300+"},
    {"name": "Bags", "code": "SHOULDBAGS", "count": "200+"},
    {"name": "Strings", "code": "STRINGS", "count": "400+"},
    {"name": "Balls", "code": "BALLS", "count": "100+"},
    {"name": "Grips", "code": "GRIPS", "count": "150+"},
    {"name": "Apparel", "code": "APPAREL", "count": "400+"},
    {"name": "Accessories", "code": "ACCESSORIES", "count": "250+"},
]

# 评测页面分类 ID 列表
# 用于从评测页面提取测试员反馈时定位相关内容区域
REVIEW_CATEGORY_IDS = [
    "Groundstrokes",
    "Volleys",
    "Serves",
    "Returns",
    "Power",
    "Control",
]
