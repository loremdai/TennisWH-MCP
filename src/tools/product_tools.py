"""Product-related tool functions"""

import sys
from typing import Dict, Any

from ..api import TennisWarehouseAPI, extract_products
from ..utils.constants import PRODUCT_CATEGORIES
from ..utils.validators import validate_search_query


def get_product_specs(tw_api: TennisWarehouseAPI, product_url: str) -> Dict[str, Any]:
    """Get detailed technical specifications for a tennis product"""

    print("Info: Getting product specifications from URL", file=sys.stderr)

    if not product_url or not product_url.strip():
        return {"error": "Product URL is required"}

    result = tw_api.get_product_specs(product_url)

    if "error" in result:
        print(f"Error: Failed to get specs: {result['error']}", file=sys.stderr)
        return result

    specs = result.get("specs", {})
    print(f"Success: Retrieved {len(specs)} specifications", file=sys.stderr)

    return {
        "product_url": result.get("url"),
        "specifications": specs,
        "spec_count": result.get("spec_count", 0),
        "note": "All specifications extracted from Tennis Warehouse product page",
    }


def get_product_review(tw_api: TennisWarehouseAPI, review_url: str) -> Dict[str, Any]:
    """Extract comprehensive review data from Tennis Warehouse review pages"""

    print("Info: Getting product review from URL", file=sys.stderr)

    if not review_url or not isinstance(review_url, str):
        return {"error": "Invalid review URL provided"}

    result = tw_api.get_product_review(review_url)

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
    else:
        print("Success: Extracted review data successfully", file=sys.stderr)

    return result


def get_product_categories() -> list:
    """Get all available product categories with product counts"""

    print("📂 Getting product categories", file=sys.stderr)
    print(f"Success: Found {len(PRODUCT_CATEGORIES)} categories", file=sys.stderr)
    return PRODUCT_CATEGORIES


def check_product_availability(
    tw_api: TennisWarehouseAPI, product_name: str
) -> Dict[str, Any]:
    """Check if a specific product is in stock"""

    print(f"📦 Checking availability for: {product_name}", file=sys.stderr)

    is_valid, error = validate_search_query(product_name)
    if not is_valid:
        return {"error": error}

    raw_response = tw_api.check_availability(product_name)
    products = extract_products(raw_response)

    if not products or "error" in products[0]:
        return {
            "found": False,
            "message": "Product not found",
            "error": products[0].get("error") if products else None,
        }

    # Return the best match
    best_match = products[0]

    result = {
        "found": True,
        "name": best_match.get("name"),
        "brand": best_match.get("brand"),
        "price": best_match.get("price"),
        "in_stock": best_match.get("in_stock", False),
        "availability": best_match.get("availability", "Unknown"),
        "product_url": best_match.get("product_url"),
    }

    print(
        f"Success: Product found: {result['name']} - {result['availability']}",
        file=sys.stderr,
    )
    return result
