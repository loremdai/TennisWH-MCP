#!/usr/bin/env python3
"""
Tennis Warehouse API Client - Internal API wrapper
"""

import requests
import sys
import os
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode
from bs4 import BeautifulSoup


class TennisWarehouseAPI:
    """Client for Tennis Warehouse's public website search"""

    def __init__(self):
        self.base_url = "https://www.tennis-warehouse.com"
        self.search_endpoint = f"{self.base_url}/search-tennis.html"
        self.timeout = int(os.getenv("TW_API_TIMEOUT", "10"))
        self.max_results = int(os.getenv("TW_MAX_RESULTS", "20"))

        print(f"🎾 Tennis Warehouse API initialized", file=sys.stderr)
        print(f"   Base URL: {self.base_url}", file=sys.stderr)
        print(f"   Timeout: {self.timeout}s", file=sys.stderr)

    def search_products(
        self, search_term: str = None, category: str = None, limit: int = 20
    ) -> Dict[str, Any]:
        """Search Tennis Warehouse website using public search endpoint

        Args:
            search_term: Search query string (e.g., "wilson racquet", "nike shoes")
            category: Product category filter (currently not implemented for website search)
            limit: Maximum number of results per page (max 100)

        Returns:
            Dictionary containing HTML content and metadata for parsing
        """

        # Validate limit
        if limit > self.max_results:
            limit = self.max_results
        elif limit < 1:
            limit = 20

        # Build parameters for website search
        params = {
            "searchtext": search_term or "",
            "opt_perpage": limit,
            "opt_sort": "relevance",
            "opt_page": 1,
        }

        # Note: Category filtering will be implemented in HTML parsing
        # as the website search doesn't use simple category parameters

        print(f"🔍 Calling website search with params: {params}", file=sys.stderr)

        try:
            response = requests.get(
                self.search_endpoint,
                params=params,
                timeout=self.timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Tennis-Warehouse-MCP/1.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            )
            response.raise_for_status()

            result = {
                "html_content": response.text,
                "status_code": response.status_code,
                "url": str(response.url),
            }
            print(f"✅ Website search successful", file=sys.stderr)

            return result

        except requests.exceptions.Timeout:
            error_msg = f"API call timed out after {self.timeout}s"
            print(f"❌ {error_msg}", file=sys.stderr)
            return {"error": error_msg}

        except requests.exceptions.RequestException as e:
            error_msg = f"API call failed: {str(e)}"
            print(f"❌ {error_msg}", file=sys.stderr)
            return {"error": error_msg}

        except ValueError as e:
            error_msg = f"Invalid JSON response: {str(e)}"
            print(f"❌ {error_msg}", file=sys.stderr)
            return {"error": error_msg}

    def get_categories(self) -> Dict[str, Any]:
        """Get available product categories"""
        # Return a simple category list since website search doesn't support facets
        return {
            "categories": [
                {"name": "Racquets", "code": "RACQUETS"},
                {"name": "Shoes - Men's", "code": "MENSSHOES"},
                {"name": "Shoes - Women's", "code": "WOMENSSHOES"},
                {"name": "Bags", "code": "SHOULDBAGS"},
                {"name": "Strings", "code": "STRINGS"},
                {"name": "Apparel", "code": "APPAREL"},
            ]
        }

    def search_bags(self, limit: int = 20) -> Dict[str, Any]:
        """Search specifically for tennis bags"""
        return self.search_products(search_term="tennis bags", limit=limit)

    def search_racquets(self, brand: str = None, limit: int = 20) -> Dict[str, Any]:
        """Search for tennis racquets"""
        search_term = f"{brand} racquet" if brand else "racquet"
        return self.search_products(
            search_term=search_term, category="RACQUETS", limit=limit
        )

    def search_shoes(self, gender: str = None, limit: int = 20) -> Dict[str, Any]:
        """Search for tennis shoes"""
        category = None
        if gender:
            category = "MENSSHOES" if gender.lower() == "men" else "WOMENSSHOES"
        return self.search_products(search_term="shoes", category=category, limit=limit)

    def check_availability(self, product_name: str) -> Dict[str, Any]:
        """Check if a specific product is available"""
        return self.search_products(search_term=product_name, limit=5)

    def get_product_specs(self, product_url: str) -> Dict[str, Any]:
        """Get product specifications from product detail page

        Args:
            product_url: Full URL to the product detail page

        Returns:
            Dictionary containing product specifications or error message
        """
        if not product_url:
            return {"error": "Product URL is required"}

        if not product_url.startswith("http"):
            if product_url.startswith("/"):
                product_url = f"{self.base_url}{product_url}"
            else:
                return {"error": "Invalid product URL format"}

        print(f"📊 Fetching specs from: {product_url}", file=sys.stderr)

        try:
            response = requests.get(
                product_url,
                timeout=self.timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Tennis-Warehouse-MCP/1.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            specs = {}

            # Try multiple common table patterns for specs
            specs_table = None

            # Pattern 1: Look for table with "Specs" in heading
            for heading in soup.find_all(["h2", "h3", "h4"]):
                if "spec" in heading.get_text().lower():
                    specs_table = heading.find_next("table")
                    if specs_table:
                        break

            # Pattern 2: Look for table with class containing "spec"
            if not specs_table:
                specs_table = soup.find("table", class_=re.compile(r"spec", re.I))

            # Pattern 3: Look for div with id/class containing "spec"
            if not specs_table:
                specs_div = soup.find(
                    ["div", "section"], attrs={"id": re.compile(r"spec", re.I)}
                )
                if not specs_div:
                    specs_div = soup.find(
                        ["div", "section"], class_=re.compile(r"spec", re.I)
                    )
                if specs_div:
                    specs_table = specs_div.find("table")

            if specs_table:
                # Extract table data
                rows = specs_table.find_all("tr")
                for row in rows:
                    cells = row.find_all(["td", "th"])

                    # Pattern A: Two-column table (key in first cell, value in second)
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            key = key.rstrip(":").strip()
                            specs[key] = value

                    # Pattern B: Single-column table with <strong> tag for key
                    elif len(cells) == 1:
                        cell = cells[0]
                        strong_tag = cell.find("strong")
                        if strong_tag:
                            key = strong_tag.get_text(strip=True).rstrip(":").strip()
                            # Get the text after the strong tag
                            full_text = cell.get_text(strip=True)
                            key_text = strong_tag.get_text(strip=True)
                            value = full_text.replace(key_text, "", 1).strip()
                            if key and value:
                                specs[key] = value

            if not specs:
                specs_dl = soup.find("dl", class_=re.compile(r"spec", re.I))
                if specs_dl:
                    dts = specs_dl.find_all("dt")
                    dds = specs_dl.find_all("dd")
                    for dt, dd in zip(dts, dds):
                        key = dt.get_text(strip=True).rstrip(":").strip()
                        value = dd.get_text(strip=True)
                        if key and value:
                            specs[key] = value

            if not specs:
                return {
                    "error": "No specifications table found on this page",
                    "url": product_url,
                    "suggestion": "This product may not have detailed specs, or the page structure is different",
                }

            print(f"✅ Extracted {len(specs)} specifications", file=sys.stderr)
            return {"url": product_url, "specs": specs, "spec_count": len(specs)}

        except requests.exceptions.Timeout:
            error_msg = f"Request timed out after {self.timeout}s"
            print(f"❌ {error_msg}", file=sys.stderr)
            return {"error": error_msg, "url": product_url}

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch product page: {str(e)}"
            print(f"❌ {error_msg}", file=sys.stderr)
            return {"error": error_msg, "url": product_url}

        except Exception as e:
            error_msg = f"Failed to parse specifications: {str(e)}"
            print(f"❌ {error_msg}", file=sys.stderr)
            return {"error": error_msg, "url": product_url}


# Utility functions for response parsing
def extract_search_insights(website_response: Dict[str, Any]) -> Dict[str, Any]:
    """Extract filtering options and search insights from Tennis Warehouse website HTML"""

    if "error" in website_response:
        return {"error": website_response["error"]}

    html_content = website_response.get("html_content", "")
    if not html_content:
        return {"error": "No HTML content received"}

    try:
        soup = BeautifulSoup(html_content, "html.parser")
        insights = {
            "brands": [],
            "types": [],
            "categories": [],
            "total_products": 0,
            "has_filter_options": False,
        }

        # Extract "Shop by Brand" options using the correct attribute
        brand_links = soup.find_all(attrs={"data-gtm_promo_creative": "Shop By Brand"})
        for link in brand_links:
            brand_name = link.get("data-gtm_promo_name", "")
            brand_url = link.get("href", "")
            if brand_name and brand_url:
                # Clean up brand name (remove "Tennis Racquets", "Tennis", etc.)
                clean_name = (
                    brand_name.replace(" Tennis Racquets", "")
                    .replace(" Tennis", "")
                    .strip()
                )
                insights["brands"].append(
                    {"name": clean_name, "url": brand_url, "display_name": clean_name}
                )

        # Extract "Shop by Type" options using Profile Block
        type_links = soup.find_all(attrs={"data-gtm_promo_creative": "Profile Block"})
        for link in type_links:
            type_name = link.get("data-gtm_promo_name", "")
            type_url = link.get("href", "")
            if type_name and type_url:
                # Clean up type name
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
            f"✅ Extracted insights: {len(insights['brands'])} brands, {len(insights['types'])} types, {insights['total_products']} products",
            file=sys.stderr,
        )
        return insights

    except Exception as e:
        error_msg = f"Failed to extract insights: {str(e)}"
        print(f"❌ {error_msg}", file=sys.stderr)
        return {"error": error_msg}


def extract_products(website_response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract product list from Tennis Warehouse website HTML"""

    if "error" in website_response:
        return [{"error": website_response["error"]}]

    html_content = website_response.get("html_content", "")
    if not html_content:
        return [{"error": "No HTML content received"}]

    try:
        soup = BeautifulSoup(html_content, "html.parser")
        products = []

        # Find product containers using GTM data attributes
        product_elements = soup.find_all(attrs={"data-gtm_impression_code": True})

        for element in product_elements:
            # Extract product data from GTM attributes
            product_code = element.get("data-gtm_impression_code", "")
            product_name = element.get("data-gtm_impression_name", "Unknown Product")
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
            price_display = "Price not available"
            if product_price:
                try:
                    price_num = float(product_price)
                    price_display = f"${price_num:.2f}"
                except (ValueError, TypeError):
                    price_display = str(product_price)

            # Look for availability/stock information
            availability = "Unknown"
            in_stock = None

            # Check for price elements that might indicate availability
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
                availability = "Unknown"
                in_stock = False

            # Create web-search-style source citation
            source_display = None
            if product_url:
                source_display = f"🔗 **Tennis Warehouse** - {product_url}"

            product = {
                "name": product_name,
                "brand": product_brand or "Unknown Brand",
                "price": price_display,
                "code": product_code,
                "in_stock": in_stock,
                "availability": availability,
                "product_url": product_url,
                "source_citation": f"[Tennis Warehouse]({product_url})"
                if product_url
                else None,
                "source_display": source_display,
            }
            products.append(product)

        print(f"✅ Extracted {len(products)} products from HTML", file=sys.stderr)
        return products

    except Exception as e:
        error_msg = f"Failed to parse HTML: {str(e)}"
        print(f"❌ {error_msg}", file=sys.stderr)
        return [{"error": error_msg}]


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
