"""产品相关工具函数

包含产品规格、评测、分类和库存检查等功能。
"""

import sys
from typing import Dict, Any, List, Optional

from ..api import TennisWarehouseAPI
from ..utils.validators import validate_url


def search_review_page(
    tw_api: TennisWarehouseAPI, product_name: str, brand: Optional[str] = None
) -> Dict[str, Any]:
    """搜索产品评测页面

    由于评测页面的 URL 命名规则不固定，此函数通过搜索来找到实际的评测页面。

    Args:
        tw_api: Tennis Warehouse API 客户端
        product_name: 产品名称（如 "Pure Strike 100"）
        brand: 品牌名称（如 "Babolat"），可选

    Returns:
        包含评测页面 URL 或错误信息的字典
    """
    # 构造搜索查询
    search_query = (
        f"{brand} {product_name} review" if brand else f"{product_name} review"
    )

    print(f"Info: Searching for review page: {search_query}", file=sys.stderr)

    # 搜索评测相关内容
    raw_response = tw_api.search_products(search_term=search_query, limit=20)

    if "error" in raw_response:
        return {
            "error": raw_response["error"],
            "suggestion": "Try searching with a different product name or check if the review exists",
        }

    # 解析 HTML 查找评测页面链接
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(raw_response.get("html_content", ""), "html.parser")

    # 查找所有链接
    review_links = []
    for link in soup.find_all("a", href=True):
        href = link["href"]
        # 查找评测页面链接（通常在 learning_center/racquet_reviews/ 目录下）
        if "learning_center" in href and "review" in href.lower():
            full_url = (
                href
                if href.startswith("http")
                else f"https://www.tennis-warehouse.com{href}"
            )
            link_text = link.get_text(strip=True)

            review_links.append({"url": full_url, "title": link_text})

    if not review_links:
        return {
            "error": "No review page found for this product",
            "suggestion": f"Searched for '{search_query}' but found no review links. The product may not have a published review yet.",
            "search_query": search_query,
        }

    # 返回找到的评测链接
    print(f"Success: Found {len(review_links)} review page(s)", file=sys.stderr)

    return {
        "review_pages": review_links,
        "count": len(review_links),
        "search_query": search_query,
        "suggestion": "Use the first URL with get_product_review tool to fetch the review data",
    }


def get_product_specs(tw_api: TennisWarehouseAPI, product_url: str) -> Dict[str, Any]:
    """获取产品规格参数

    从产品详情页面提取技术规格。

    Args:
        tw_api: Tennis Warehouse API 客户端
        product_url: 产品页面 URL

    Returns:
        包含产品规格或错误信息的字典
    """
    is_valid, error = validate_url(product_url, "tennis-warehouse.com")
    if not is_valid:
        return {"error": error}

    print(f"Info: Fetching product specs from: {product_url}", file=sys.stderr)
    result = tw_api.get_product_specs(product_url)

    if "error" not in result:
        print(
            f"Success: Extracted {result.get('spec_count', 0)} specifications",
            file=sys.stderr,
        )

    return result


def get_product_review(tw_api: TennisWarehouseAPI, review_url: str) -> Dict[str, Any]:
    """获取产品评测数据

    从评测页面提取性能评分、实验室数据和测试员反馈。

    Args:
        tw_api: Tennis Warehouse API 客户端
        review_url: 评测页面 URL

    Returns:
        包含评测数据或错误信息的字典
    """
    is_valid, error = validate_url(review_url, "tennis-warehouse.com")
    if not is_valid:
        return {"error": error}

    print(f"Info: Fetching review from: {review_url}", file=sys.stderr)
    result = tw_api.get_product_review(review_url)

    if "error" not in result:
        scores_count = len(result.get("scores", {}))
        lab_count = len(result.get("lab_data", {}))
        print(
            f"Success: Extracted {scores_count} scores, {lab_count} lab metrics",
            file=sys.stderr,
        )

    return result


def get_product_categories(tw_api: TennisWarehouseAPI) -> List[Dict[str, str]]:
    """获取所有产品分类

    返回 Tennis Warehouse 的所有产品分类列表。

    Args:
        tw_api: Tennis Warehouse API 客户端

    Returns:
        产品分类列表
    """
    result = tw_api.get_categories()
    categories = result.get("categories", [])

    print(f"Info: Retrieved {len(categories)} product categories", file=sys.stderr)
    return categories


def check_product_availability(
    tw_api: TennisWarehouseAPI, product_name: str
) -> List[Dict[str, Any]]:
    """检查产品库存状态

    搜索产品并返回库存信息。

    Args:
        tw_api: Tennis Warehouse API 客户端
        product_name: 产品名称

    Returns:
        产品列表，包含库存状态
    """
    from ..api import extract_products

    print(f"Info: Checking availability for: {product_name}", file=sys.stderr)

    raw_response = tw_api.check_availability(product_name)
    products = extract_products(raw_response)

    if products and "error" not in products[0]:
        available_count = sum(
            1 for p in products if p.get("availability") == "Available"
        )
        print(
            f"Success: Found {len(products)} products, {available_count} available",
            file=sys.stderr,
        )

    return products
