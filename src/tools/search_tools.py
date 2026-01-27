"""Search-related tool functions"""

import sys
from typing import List, Dict, Any, Optional

from ..api import TennisWarehouseAPI, extract_products, extract_search_insights
from ..utils.constants import CATEGORY_ALIASES
from ..utils.validators import validate_search_query, validate_limit


def search_tennis_products(
    tw_api: TennisWarehouseAPI,
    query: str,
    category: Optional[str] = None,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """Search Tennis Warehouse products with intelligent filtering"""

    print(
        f"Search: Searching products: query='{query}', category={category}",
        file=sys.stderr,
    )

    # Validate query
    is_valid, error = validate_search_query(query)
    if not is_valid:
        return [{"error": error}]

    # Validate and clamp max_results
    max_results = validate_limit(max_results, max_val=20)

    # Map category aliases
    if category:
        category = CATEGORY_ALIASES.get(category.upper(), category.upper())

    # Call API
    raw_response = tw_api.search_products(
        search_term=query, category=category, limit=max_results
    )

    # Transform for LLM consumption
    products = extract_products(raw_response)

    # Check if we should provide smart search suggestions
    insights = extract_search_insights(raw_response)

    # Return products with insights
    if products and "error" not in products[0]:
        print(f"Success: Found {len(products)} products", file=sys.stderr)

    return products


def search_tennis_bags(
    tw_api: TennisWarehouseAPI,
    style: Optional[str] = None,
    brand: Optional[str] = None,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """Search specifically for tennis bags with advanced filtering"""

    print(f"Searching bags: style={style}, brand={brand}", file=sys.stderr)

    max_results = validate_limit(max_results, max_val=20)

    # Get all bags first
    raw_response = tw_api.search_bags(limit=max_results * 2)
    products = extract_products(raw_response)

    if products and "error" in products[0]:
        return products

    # Apply additional filtering
    filtered_bags = []
    for product in products:
        # Style filtering
        if style:
            product_name = product.get("name", "").lower()
            style_lower = style.lower()

            # Handle common style aliases
            style_matches = {
                "backpack": ["backpack", "back pack"],
                "tote": ["tote"],
                "duffel": ["duffel", "duffle"],
                "6 pack": ["6 pack", "6-pack", "six pack"],
                "12 pack": ["12 pack", "12-pack", "twelve pack"],
                "wheeled": ["wheel", "rolling", "roll"],
            }

            matches = style_matches.get(style_lower, [style_lower])
            if not any(match in product_name for match in matches):
                continue

        # Brand filtering
        if brand:
            product_brand = product.get("brand", "").lower()
            if brand.lower() not in product_brand:
                continue

        filtered_bags.append(product)

        if len(filtered_bags) >= max_results:
            break

    print(f"Success: Found {len(filtered_bags)} matching bags", file=sys.stderr)
    return filtered_bags


def search_tennis_racquets(
    tw_api: TennisWarehouseAPI,
    brand: Optional[str] = None,
    weight_range: Optional[str] = None,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """Search for tennis racquets with brand and weight filtering"""

    print(f"Searching racquets: brand={brand}, weight={weight_range}", file=sys.stderr)

    max_results = validate_limit(max_results, max_val=20)

    # Build search term
    search_term = "racquet"
    if brand:
        search_term = f"{brand} racquet"

    raw_response = tw_api.search_products(
        search_term=search_term, category="RACQUETS", limit=max_results
    )

    products = extract_products(raw_response)

    # TODO: Add weight filtering when we understand the data structure better
    if weight_range:
        print(
            f"ℹ️  Weight filtering ({weight_range}) not yet implemented", file=sys.stderr
        )

    print(f"Success: Found {len(products)} racquets", file=sys.stderr)
    return products


def search_tennis_shoes(
    tw_api: TennisWarehouseAPI,
    gender: Optional[str] = None,
    brand: Optional[str] = None,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """Search for tennis shoes with gender and brand filtering"""

    print(f"Searching shoes: gender={gender}, brand={brand}", file=sys.stderr)

    max_results = validate_limit(max_results, max_val=20)

    # Build search term
    search_term = "tennis shoes"
    if brand:
        search_term = f"{brand} tennis shoes"

    # Determine category
    category = None
    if gender:
        if gender.lower() in ["men", "mens", "male"]:
            category = "MENSSHOES"
        elif gender.lower() in ["women", "womens", "female"]:
            category = "WOMENSSHOES"

    raw_response = tw_api.search_products(
        search_term=search_term, category=category, limit=max_results
    )

    products = extract_products(raw_response)

    print(f"Success: Found {len(products)} shoes", file=sys.stderr)
    return products


def smart_search_tennis(
    tw_api: TennisWarehouseAPI, query: str, max_results: int = 20
) -> List[Dict[str, Any]]:
    """Intelligent tennis product search with conversational filtering options"""

    print(f"Smart search: '{query}'", file=sys.stderr)

    # Validate query
    is_valid, error = validate_search_query(query)
    if not is_valid:
        return [{"error": error}]

    max_results = validate_limit(max_results, max_val=50)

    # Call website search
    raw_response = tw_api.search_products(search_term=query, limit=max_results)

    # Extract insights and products
    insights = extract_search_insights(raw_response)
    products = extract_products(raw_response)

    # Add sample products with citations to the main result
    sample_products = []
    if products and not any("error" in p for p in products):
        for product in products[:3]:
            name_with_source = product.get("name", "Unknown Product")
            if product.get("source_citation"):
                name_with_source += f" {product['source_citation']}"

            sample_product = {
                "name": name_with_source,
                "brand": product.get("brand", "Unknown Brand"),
                "price": product.get("price", "Price not available"),
                "availability": product.get("availability", "Unknown"),
                "product_url": product.get("product_url", ""),
                "source_citation": product.get("source_citation", ""),
            }
            sample_products.append(sample_product)

    # Return consolidated result
    result = [
        {
            "insights": insights,
            "sample_products": sample_products,
            "source_info": "All product information and pricing from Tennis Warehouse. Click source links to view full details and purchase."
            if sample_products
            else "",
        }
    ]

    print(
        f"Success: Smart search complete: {insights.get('total_products', 0)} products found",
        file=sys.stderr,
    )
    return result


def get_tennis_deals(
    tw_api: TennisWarehouseAPI, category: Optional[str] = None, max_results: int = 10
) -> List[Dict[str, Any]]:
    """Find current deals and discounted tennis products"""

    print(f"Looking for deals in category: {category}", file=sys.stderr)

    max_results = validate_limit(max_results, max_val=20)

    # Search for terms that typically indicate sales/deals
    deal_terms = ["sale", "clearance", "discount", "special"]

    all_deals = []
    for term in deal_terms:
        raw_response = tw_api.search_products(
            search_term=term, category=category, limit=max_results
        )

        products = extract_products(raw_response)
        if products and "error" not in products[0]:
            all_deals.extend(products)

        if len(all_deals) >= max_results:
            break

    # Remove duplicates and limit results
    seen_names = set()
    unique_deals = []
    for deal in all_deals:
        name = deal.get("name", "")
        if name not in seen_names:
            seen_names.add(name)
            unique_deals.append(deal)

        if len(unique_deals) >= max_results:
            break

    print(f"Success: Found {len(unique_deals)} deals", file=sys.stderr)
    return unique_deals
