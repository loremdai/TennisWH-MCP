"""产品相关工具函数

包含产品规格、评测、分类和库存检查等功能。
"""

import sys
from typing import Dict, Any, List, Optional

from ..api import TennisWarehouseAPI
from ..utils.validators import validate_url


# 评测索引页面 URL
REVIEW_INDEX_URLS = {
    "racquets": "https://www.tennis-warehouse.com/reviewedracquets.html",
    "shoes": "https://www.tennis-warehouse.com/reviewedshoes.html",
    "strings": "https://www.tennis-warehouse.com/reviewedstrings.html",
}


def search_review_page(
    tw_api: TennisWarehouseAPI,
    product_name: str,
    brand: Optional[str] = None,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """搜索产品评测页面

    从 Tennis Warehouse 的评测索引页面中搜索匹配的评测。
    这比通过搜索 API 更准确，因为索引页面包含所有已发布的评测。

    Args:
        tw_api: Tennis Warehouse API 客户端
        product_name: 产品名称（如 "Pure Strike 100"）
        brand: 品牌名称（如 "Babolat"），可选
        category: 产品类别（"racquets", "shoes", "strings"），可选

    Returns:
        包含评测页面 URL 或错误信息的字典
    """
    import requests
    from bs4 import BeautifulSoup

    # 确定要搜索的索引页面
    index_urls = []
    if category and category.lower() in REVIEW_INDEX_URLS:
        index_urls.append(REVIEW_INDEX_URLS[category.lower()])
    else:
        # 如果没有指定类别，搜索所有索引页面
        index_urls = list(REVIEW_INDEX_URLS.values())

    print(
        f"Info: Searching review index pages for: {brand} {product_name}"
        if brand
        else f"Info: Searching review index pages for: {product_name}",
        file=sys.stderr,
    )

    all_review_links = []

    for index_url in index_urls:
        try:
            response = requests.get(index_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # 查找所有评测链接
            for link in soup.find_all("a", href=True):
                href = link["href"]
                link_text = link.get_text(strip=True)

                # 过滤评测页面链接
                if "review" in href.lower() and "learning_center" in href:
                    # 构造完整 URL
                    full_url = (
                        href
                        if href.startswith("http")
                        else f"https://www.tennis-warehouse.com{href}"
                    )

                    # 检查是否匹配产品名称和品牌
                    text_lower = link_text.lower()
                    product_lower = product_name.lower()

                    # 基本匹配：链接文本包含产品名称的关键词
                    product_keywords = product_lower.split()
                    matches = sum(
                        1 for keyword in product_keywords if keyword in text_lower
                    )

                    # 如果指定了品牌，也要匹配品牌
                    brand_match = True
                    if brand:
                        brand_match = brand.lower() in text_lower

                    # 只添加匹配的评测
                    if matches > 0 and brand_match:
                        all_review_links.append(
                            {
                                "url": full_url,
                                "title": link_text,
                                "match_score": matches,
                            }
                        )

        except Exception as e:
            print(f"Warning: Failed to fetch {index_url}: {e}", file=sys.stderr)
            continue

    if not all_review_links:
        return {
            "error": "No review page found for this product",
            "suggestion": (
                f"Searched for '{brand} {product_name}' in review index pages but found no matches. "
                "The product may not have a published review yet."
            )
            if brand
            else (
                f"Searched for '{product_name}' in review index pages but found no matches. "
                "The product may not have a published review yet."
            ),
            "search_query": f"{brand} {product_name}" if brand else product_name,
        }

    # 按匹配分数排序
    all_review_links.sort(key=lambda x: x["match_score"], reverse=True)

    # 移除重复的 URL
    seen_urls = set()
    unique_links = []
    for link in all_review_links:
        if link["url"] not in seen_urls:
            seen_urls.add(link["url"])
            unique_links.append({"url": link["url"], "title": link["title"]})

    print(f"Success: Found {len(unique_links)} review page(s)", file=sys.stderr)

    return {
        "review_pages": unique_links,
        "count": len(unique_links),
        "search_query": f"{brand} {product_name}" if brand else product_name,
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
