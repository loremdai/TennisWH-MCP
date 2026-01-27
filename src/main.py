#!/usr/bin/env python3
"""
Tennis Warehouse MCP Server - Modular Version
"""

import sys
from typing import List, Dict, Any, Optional

try:
    from mcp.server.fastmcp import FastMCP

    print("Success: MCP imported successfully", file=sys.stderr)
except Exception as e:
    print(f"Error: Failed to import MCP: {e}", file=sys.stderr)
    sys.exit(1)

from src.api import TennisWarehouseAPI
from src.tools import (
    search_tennis_products,
    search_tennis_bags,
    search_tennis_racquets,
    search_tennis_shoes,
    smart_search_tennis,
    get_tennis_deals,
    search_review_page,
    get_product_specs,
    get_product_review,
    get_product_categories,
    check_product_availability,
    handle_search_option,
)

# Initialize MCP server
mcp = FastMCP("tennis-warehouse")

# Initialize API client
try:
    tw_api = TennisWarehouseAPI()
    print("Success: Tennis Warehouse MCP server starting up...", file=sys.stderr)
except Exception as e:
    print(f"Error: Failed to initialize Tennis Warehouse API: {e}", file=sys.stderr)
    sys.exit(1)


# Register all tools
@mcp.tool()
def search_products(
    query: str, category: Optional[str] = None, max_results: int = 10
) -> List[Dict[str, Any]]:
    """Search Tennis Warehouse products with intelligent filtering.

    Returns basic product information (name, brand, price, availability, URL).

    For more detailed information, use these follow-up tools:
    - get_product_specs(product_url) - Get technical specifications (Swingweight, Stiffness, etc.)
    - search_review(product_name, brand, category) - Find review pages
    - get_product_review(review_url) - Get performance ratings and playtester feedback

    Workflow example:
    1. Use this tool to find products
    2. Extract product_url from results
    3. Call get_product_specs(product_url) for detailed specs
       OR search_review for reviews

    Args:
        query: Search term (e.g., "wilson racquet", "nike shoes", "head bag")
        category: Product category filter (e.g., "RACQUETS", "SHOES", "BAGS")
        max_results: Maximum number of results (1-20, default: 10)

    Returns:
        List of products with name, brand, price, availability, and URL
    """
    return search_tennis_products(tw_api, query, category, max_results)


@mcp.tool()
def get_specs(product_url: str) -> Dict[str, Any]:
    """Get detailed technical specifications for a tennis product.

    IMPORTANT: Use this tool when users ask about specific technical parameters.
    This tool extracts detailed specs that are NOT available in search results.

    Common use cases:
    - User asks: "What's the Swingweight of Wilson Blade 98?"
      → First search for the product, then use this tool with the product URL

    - User asks: "Compare the Stiffness of these two racquets"
      → Search for each racquet, then use this tool for each URL

    - User asks: "Show me the full specs of this racquet"
      → Use this tool with the product URL

    Technical parameters this tool extracts (not in search results):
    - Racquets: Head Size, Weight, Balance, Swingweight, Stiffness, String Pattern,
      Beam Width, Power Level, Stroke Style, Swing Speed
    - Shoes: Weight, Cushioning, Outsole, Support features

    This tool extracts specifications from product detail pages.
    It does NOT provide review scores or performance ratings.
    For reviews, use search_review and get_review instead.

    Workflow:
    1. User asks about product specifications
    2. Use search_products to find the product and get its URL
    3. Call this tool with the product URL to extract detailed specs

    Args:
        product_url: Full URL to the product detail page on Tennis Warehouse

    Returns:
        Dictionary containing all available specifications from the product page
    """
    return get_product_specs(tw_api, product_url)


@mcp.tool()
def search_bags(
    style: Optional[str] = None, brand: Optional[str] = None, max_results: int = 10
) -> List[Dict[str, Any]]:
    """Search specifically for tennis bags with advanced filtering.

    Returns basic bag information. For detailed specifications:
    1. Use this tool to find bags
    2. Extract product_url from results
    3. Call get_specs(product_url) for technical details

    Args:
        style: Bag style (e.g., "backpack", "tote", "duffel", "6 pack", "12 pack")
        brand: Brand filter (e.g., "Wilson", "Head", "Babolat", "Nike")
        max_results: Maximum number of results (1-20, default: 10)

    Returns:
        List of tennis bags with specifications and features
    """
    return search_tennis_bags(tw_api, style, brand, max_results)


@mcp.tool()
def search_racquets(
    brand: Optional[str] = None,
    weight_range: Optional[str] = None,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """Search for tennis racquets with brand and weight filtering.

    Returns basic racquet information. For detailed specifications or reviews:
    1. Use this tool to find racquets
    2. Extract product_url from results
    3. Call get_specs(product_url) for technical specs
       OR search_review(product_name, brand, "racquets") for reviews

    Args:
        brand: Racquet brand (e.g., "Wilson", "Head", "Babolat", "Yonex")
        weight_range: Weight preference (e.g., "light", "medium", "heavy")
        max_results: Maximum number of results (1-20, default: 10)

    Returns:
        List of tennis racquets with specifications
    """
    return search_tennis_racquets(tw_api, brand, weight_range, max_results)


@mcp.tool()
def search_shoes(
    gender: Optional[str] = None,
    brand: Optional[str] = None,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """Search for tennis shoes with gender and brand filtering.

    Args:
        gender: Gender filter (e.g., "men", "women")
        brand: Brand filter (e.g., "Nike", "Adidas", "Asics")
        max_results: Maximum number of results (1-20, default: 10)

    Returns:
        List of tennis shoes with specifications
    """
    return search_tennis_shoes(tw_api, gender, brand, max_results)


@mcp.tool()
def get_categories() -> list:
    """Get all available product categories with product counts.

    Use this to discover available categories, then use search_products
    or smart_search with the category code to find products.

    Example workflow:
    1. Call this tool to see all categories
    2. Choose a category (e.g., "RACQUETS", "SHOES")
    3. Use search_products(query="...", category="RACQUETS")

    Returns:
        List of categories with names, codes, and product counts
    """
    return get_product_categories()


@mcp.tool()
def check_availability(product_name: str) -> Dict[str, Any]:
    """Check if a specific product is in stock.

    Returns availability status with product_url. Use the URL for more details:
    - get_specs(product_url) - Get detailed specifications
    - search_review(product_name, brand, category) - Find review pages

    Example workflow:
    1. Call this tool to check availability
    2. If found, extract product_url from result
    3. Call get_specs(product_url) for full specifications

    Args:
        product_name: Exact or partial product name to check

    Returns:
        Availability status with product details and URL
    """
    return check_product_availability(tw_api, product_name)


@mcp.tool()
def search_review(
    product_name: str, brand: Optional[str] = None, category: Optional[str] = None
) -> Dict[str, Any]:
    """Search for product review pages on Tennis Warehouse.

    IMPORTANT: Use this tool BEFORE calling get_review to find the correct review URL.

    This tool searches Tennis Warehouse's official review index pages for accurate results:
    - Racquets: https://www.tennis-warehouse.com/reviewedracquets.html
    - Shoes: https://www.tennis-warehouse.com/reviewedshoes.html
    - Strings: https://www.tennis-warehouse.com/reviewedstrings.html

    Common workflow:
    1. User asks: "What's the review for Babolat Pure Strike 100?"
    2. Call this tool: search_review("Pure Strike 100", "Babolat", "racquets")
    3. Extract the review URL from results (sorted by relevance)
    4. Call get_review with the correct URL

    Why use this tool:
    - Review URLs don't follow predictable patterns
    - Example: "Pure Strike 100 16x20" → "PS1620review.html" (not "BPS1001620review.html")
    - This tool searches official review index pages for accurate matches

    Args:
        product_name: Product name (e.g., "Pure Strike 100", "FX 500")
        brand: Brand name (e.g., "Babolat", "Dunlop") - helps narrow search
        category: Product category ("racquets", "shoes", "strings") - searches specific index

    Returns:
        Dictionary containing:
        - review_pages: List of found review URLs with titles (sorted by relevance)
        - count: Number of review pages found
        - suggestion: Next steps to take
    """
    return search_review_page(tw_api, product_name, brand, category)


@mcp.tool()
def get_review(review_url: str) -> Dict[str, Any]:
    """Extract comprehensive review data from Tennis Warehouse review pages.

    This tool extracts multi-dimensional review data including:
    - Performance scores (Power, Control, Maneuverability, Stability, Comfort, etc.) on 1-10 scale
    - TWU Lab Data (Flex Rating, Swingweight, measured specifications)
    - Qualitative feedback (Positives, Negatives, Playtester Thoughts)

    Use this tool when users ask about:
    - Product reviews or ratings
    - Performance characteristics or how a product plays
    - Lab-tested specifications
    - Playtester feedback or opinions

    Args:
        review_url: Full URL to Tennis Warehouse review page
                   (e.g., https://www.tennis-warehouse.com/learning_center/racquet_reviews/DF500review.html)

    Returns:
        Dictionary containing:
        - scores: Performance metrics (Power, Control, etc.)
        - lab_data: Laboratory measurements
        - feedback: Positives, negatives, and playtester thoughts

    Example workflow:
        1. User asks: "What's the review for Dunlop FX 500?"
        2. Use search_review to find the review URL
        3. Call get_review with the review URL
    """
    return get_product_review(tw_api, review_url)


@mcp.tool()
def get_deals(
    category: Optional[str] = None, max_results: int = 10
) -> List[Dict[str, Any]]:
    """Find current deals and discounted tennis products.

    Returns deals with product_url. For detailed information:
    - get_specs(product_url) - Get technical specifications
    - search_review(product_name, brand, category) - Find review pages

    Example workflow:
    1. Call this tool to find deals
    2. Extract product_url from results
    3. Use get_specs or search_review for more details

    Args:
        category: Product category to search for deals (e.g., "RACQUETS", "SHOES")
        max_results: Maximum number of deals to return (1-20, default: 10)

    Returns:
        List of discounted products with deal information and URLs
    """
    return get_tennis_deals(tw_api, category, max_results)


@mcp.tool()
def smart_search(query: str, max_results: int = 20) -> List[Dict[str, Any]]:
    """Intelligent tennis product search with conversational filtering options.

    This tool searches for tennis products and returns basic information:
    - Product name, brand, price, availability, and URL

    NOTE: This tool does NOT return:
    - Detailed technical specifications (Swingweight, Stiffness, Balance, etc.)
    - Review scores or performance ratings
    - Lab-tested data or playtester feedback

    If user asks about technical parameters:
    1. Use this tool to find the product and get its URL
    2. Then call get_specs with the product URL

    If user asks about reviews, ratings, or performance:
    1. Use this tool to find the product
    2. Then call search_review to find review pages
    3. Then call get_review with the review URL

    Example workflows:
    - Technical specs: "What's the Swingweight of Wilson Blade 98?"
      → smart_search → get_specs
    - Reviews: "How does the Dunlop FX 500 play?"
      → smart_search → search_review → get_review

    Args:
        query: Search term (e.g., "tennis balls", "wilson racquet", "nike shoes")
        max_results: Maximum number of results to analyze (1-50, default: 20)

    Returns:
        Search results with product names, prices, URLs, and filtering suggestions
    """
    return smart_search_tennis(tw_api, query, max_results)


@mcp.tool()
def handle_option(option: str, insights: Dict[str, Any], query: str) -> Dict[str, Any]:
    """Handle user's search option selection from smart search suggestions.

    Args:
        option: Option number selected by user
        insights: Search insights from previous smart_search call
        query: Original search query

    Returns:
        Action to take based on selected option
    """
    return handle_search_option(option, insights, query)


if __name__ == "__main__":
    mcp.run()
