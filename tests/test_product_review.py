#!/usr/bin/env python3
"""产品评测功能测试脚本

测试从 Tennis Warehouse 评测页面提取评测数据的功能。
"""

import sys
from src.api import TennisWarehouseAPI


def test_product_review():
    """测试从 Tennis Warehouse 评测页面提取评测数据"""

    api = TennisWarehouseAPI()

    # 使用用户浏览器中的测试 URL
    test_url = (
        "https://www.tennis-warehouse.com/learning_center/"
        "racquet_reviews/DF500review.html"
    )

    print(f"\n{'=' * 60}")
    print("Testing get_product_review with Dunlop FX 500 review")
    print(f"URL: {test_url}")
    print(f"{'=' * 60}\n")

    result = api.get_product_review(test_url)

    if "error" in result:
        print(f"Error: {result['error']}")
        if "suggestion" in result:
            print(f"   Suggestion: {result['suggestion']}")
        return False

    print("Successfully extracted review data\n")

    # 显示评分
    if result.get("scores"):
        print(f"Performance Scores ({len(result['scores'])} metrics):")
        for metric, score in result["scores"].items():
            print(f"   {metric}: {score}")
        print()

    # 显示实验室数据
    if result.get("lab_data"):
        print(f"TWU Lab Data ({len(result['lab_data'])} measurements):")
        for metric, value in result["lab_data"].items():
            print(f"   {metric}: {value}")
        print()

    # 显示反馈
    if result.get("feedback"):
        feedback = result["feedback"]

        if feedback.get("positives"):
            print(f"Positives ({len(feedback['positives'])} items):")
            for item in feedback["positives"]:
                print(f"   - {item}")
            print()

        if feedback.get("negatives"):
            print(f"Negatives ({len(feedback['negatives'])} items):")
            for item in feedback["negatives"]:
                print(f"   - {item}")
            print()

        if feedback.get("playtester_thoughts"):
            thoughts_count = len(feedback["playtester_thoughts"])
            print(f"Playtester Thoughts ({thoughts_count} excerpts):")
            for i, thought in enumerate(feedback["playtester_thoughts"][:3], 1):
                print(f"   {i}. {thought[:100]}...")
            print()

    return True


if __name__ == "__main__":
    success = test_product_review()
    sys.exit(0 if success else 1)
