"""HTML parsing utilities for Tennis Warehouse responses"""

import sys
import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup

from ..utils.constants import (
    DEFAULT_UNKNOWN_PRODUCT,
    DEFAULT_UNKNOWN_BRAND,
    DEFAULT_PRICE_NOT_AVAILABLE,
    DEFAULT_AVAILABILITY_UNKNOWN,
    HTML_PARSER,
)


def extract_search_insights(website_response: Dict[str, Any]) -> Dict[str, Any]:
    """Extract filtering options and search insights from Tennis Warehouse website HTML"""

    if "error" in website_response:
        return {"error": website_response["error"]}

    html_content = website_response.get("html_content", "")
    if not html_content:
        return {"error": "No HTML content received"}

    try:
        soup = BeautifulSoup(html_content, HTML_PARSER)
        insights = {
            "brands": [],
            "types": [],
            "categories": [],
            "total_products": 0,
            "has_filter_options": False,
        }

        # Extract "Shop by Brand" options
        brand_links = soup.find_all(attrs={"data-gtm_promo_creative": "Shop By Brand"})
        for link in brand_links:
            brand_name = link.get("data-gtm_promo_name", "")
            brand_url = link.get("href", "")
            if brand_name and brand_url:
                clean_name = (
                    brand_name.replace(" Tennis Racquets", "")
                    .replace(" Tennis", "")
                    .strip()
                )
                insights["brands"].append(
                    {"name": clean_name, "url": brand_url, "display_name": clean_name}
                )

        # Extract "Shop by Type" options
        type_links = soup.find_all(attrs={"data-gtm_promo_creative": "Profile Block"})
        for link in type_links:
            type_name = link.get("data-gtm_promo_name", "")
            type_url = link.get("href", "")
            if type_name and type_url:
                clean_type = (
                    type_name.replace(" Tennis Racquets", "")
                    .replace(" Racquets", "")
                    .strip()
                )
                insights["types"].append(
                    {"name": clean_type, "url": type_url, "display_name": clean_type}
                )

        # Count products
        product_elements = soup.find_all(attrs={"data-gtm_impression_code": True})
        insights["total_products"] = len(product_elements)

        # Determine if we have filtering options
        insights["has_filter_options"] = (
            len(insights["brands"]) > 0 or len(insights["types"]) > 0
        )

        print(
            f"Success: Extracted insights: {len(insights['brands'])} brands, {len(insights['types'])} types, {insights['total_products']} products",
            file=sys.stderr,
        )
        return insights

    except Exception as e:
        error_msg = f"Failed to extract insights: {str(e)}"
        print(f"Error: {error_msg}", file=sys.stderr)
        return {"error": error_msg}


def extract_products(website_response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract product list from Tennis Warehouse website HTML"""

    if "error" in website_response:
        return [{"error": website_response["error"]}]

    html_content = website_response.get("html_content", "")
    if not html_content:
        return [{"error": "No HTML content received"}]

    try:
        soup = BeautifulSoup(html_content, HTML_PARSER)
        products = []

        # Find product containers using GTM data attributes
        product_elements = soup.find_all(attrs={"data-gtm_impression_code": True})

        for element in product_elements:
            product = _extract_single_product(element)
            if product:
                products.append(product)

        print(f"Success: Extracted {len(products)} products from HTML", file=sys.stderr)
        return products

    except Exception as e:
        error_msg = f"Failed to parse HTML: {str(e)}"
        print(f"Error: {error_msg}", file=sys.stderr)
        return [{"error": error_msg}]


def _extract_single_product(element) -> Dict[str, Any]:
    """Extract product data from a single product element"""
    # Extract product data from GTM attributes
    product_code = element.get("data-gtm_impression_code", "")
    product_name = element.get("data-gtm_impression_name", DEFAULT_UNKNOWN_PRODUCT)
    product_price = element.get("data-gtm_impression_price", "")
    product_brand = element.get("data-gtm_impression_brand", "")

    # Find product URL
    product_url = None
    link_element = element.find("a", href=True)
    if link_element:
        href = link_element["href"]
        if href.startswith("/"):
            product_url = f"https://www.tennis-warehouse.com{href}"
        else:
            product_url = href

    # Extract price information
    price_display = DEFAULT_PRICE_NOT_AVAILABLE
    if product_price:
        try:
            price_num = float(product_price)
            price_display = f"${price_num:.2f}"
        except (ValueError, TypeError):
            price_display = str(product_price)

    # Look for availability/stock information
    availability = DEFAULT_AVAILABILITY_UNKNOWN
    in_stock = None

    price_elements = element.find_all(
        class_=re.compile(r"price|availability|stock", re.I)
    )
    for price_elem in price_elements:
        text = price_elem.get_text(strip=True).lower()
        if "out of stock" in text or "unavailable" in text:
            availability = "Out of Stock"
            in_stock = False
        elif "in stock" in text or "available" in text:
            availability = "Available"
            in_stock = True

    # If we have price data, assume it's available
    if in_stock is None and product_price:
        availability = "Available"
        in_stock = True
    elif in_stock is None:
        availability = DEFAULT_AVAILABILITY_UNKNOWN
        in_stock = False

    # Create source citation
    source_citation = None
    source_display = None
    if product_url:
        source_citation = f"[Tennis Warehouse]({product_url})"
        source_display = f"🔗 **Tennis Warehouse** - {product_url}"

    return {
        "name": product_name,
        "brand": product_brand or DEFAULT_UNKNOWN_BRAND,
        "price": price_display,
        "code": product_code,
        "in_stock": in_stock,
        "availability": availability,
        "product_url": product_url,
        "source_citation": source_citation,
        "source_display": source_display,
    }


def extract_categories(solr_response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract category list from Solr facet response"""

    if "error" in solr_response:
        return [{"error": solr_response["error"]}]

    categories = []
    facets = solr_response.get("facet_counts", {}).get("facet_fields", {})

    for facet_key, facet_data in facets.items():
        if isinstance(facet_data, list) and len(facet_data) >= 2:
            # Solr returns facets as [value1, count1, value2, count2, ...]
            for i in range(0, len(facet_data), 2):
                if i + 1 < len(facet_data):
                    category_name = facet_data[i]
                    product_count = facet_data[i + 1]

                    categories.append(
                        {
                            "name": category_name,
                            "code": category_name.upper()
                            .replace(" ", "")
                            .replace("-", ""),
                            "product_count": product_count,
                        }
                    )

    return categories


def extract_price_ranges(solr_response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract price range information from Solr facet response"""

    if "error" in solr_response:
        return [{"error": solr_response["error"]}]

    price_ranges = []
    facets = solr_response.get("facet_counts", {}).get("facet_fields", {})

    for facet_key, facet_data in facets.items():
        if "price" in facet_key.lower() and isinstance(facet_data, list):
            for i in range(0, len(facet_data), 2):
                if i + 1 < len(facet_data):
                    price_range = facet_data[i]
                    count = facet_data[i + 1]
                    price_ranges.append({"range": price_range, "product_count": count})

    return price_ranges
