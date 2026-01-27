"""输入验证工具函数

本模块提供各种输入验证函数，用于验证搜索查询、URL 和数值范围等。
所有验证函数返回 (is_valid, error_message) 元组。
"""

from typing import Optional, Tuple


def validate_search_query(
    query: str, min_length: int = 2
) -> Tuple[bool, Optional[str]]:
    """验证搜索查询字符串

    Args:
        query: 要验证的搜索查询字符串
        min_length: 最小长度要求，默认为 2

    Returns:
        元组 (is_valid, error_message)
        - is_valid: 布尔值，表示查询是否有效
        - error_message: 如果无效，返回错误消息；否则返回 None
    """
    if not query or not isinstance(query, str):
        return False, "Search query must be a non-empty string"

    if len(query.strip()) < min_length:
        return False, f"Search query must be at least {min_length} characters"

    return True, None


def validate_url(
    url: str, required_domain: str = "tennis-warehouse.com"
) -> Tuple[bool, Optional[str]]:
    """验证 URL 格式和域名

    Args:
        url: 要验证的 URL 字符串
        required_domain: 必需的域名，默认为 "tennis-warehouse.com"

    Returns:
        元组 (is_valid, error_message)
        - is_valid: 布尔值，表示 URL 是否有效
        - error_message: 如果无效，返回错误消息；否则返回 None
    """
    if not url or not isinstance(url, str):
        return False, "Invalid URL provided"

    if required_domain and required_domain not in url:
        return False, f"URL must be from {required_domain}"

    return True, None


def validate_limit(limit: int, min_val: int = 1, max_val: int = 50) -> int:
    """验证并限制数值范围

    将输入值限制在指定的最小值和最大值之间。
    如果值小于最小值，返回默认值 10。
    如果值大于最大值，返回最大值。

    Args:
        limit: 要验证的数值
        min_val: 最小允许值，默认为 1
        max_val: 最大允许值，默认为 50

    Returns:
        限制后的数值
    """
    if limit > max_val:
        return max_val
    elif limit < min_val:
        return 10  # 返回默认值
    return limit
