#!/usr/bin/env python3
"""测试 search_review_page 功能"""

from src.api import TennisWarehouseAPI


def test_search_review():
    """测试搜索评测页面功能"""

    api = TennisWarehouseAPI()

    # 测试用例：Babolat Pure Strike 100 16x20
    print("\n" + "=" * 60)
    print("测试搜索评测页面: Babolat Pure Strike 100 16x20")
    print("=" * 60 + "\n")

    from src.tools.product_tools import search_review_page

    result = search_review_page(
        api, product_name="Pure Strike 100 16x20", brand="Babolat"
    )

    if "error" in result:
        print(f"错误: {result['error']}")
        if "suggestion" in result:
            print(f"建议: {result['suggestion']}")
        return False

    print(f"找到 {result['count']} 个评测页面:\n")

    for i, page in enumerate(result.get("review_pages", []), 1):
        print(f"{i}. {page['title']}")
        print(f"   URL: {page['url']}\n")

    if result.get("suggestion"):
        print(f"建议: {result['suggestion']}")

    return True


if __name__ == "__main__":
    test_search_review()
