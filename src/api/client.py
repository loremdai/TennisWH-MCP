"""Tennis Warehouse API Client"""

import requests
import sys
import os
from typing import Dict, Any
from bs4 import BeautifulSoup
import re

from ..utils.constants import (
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RESULTS,
    ERROR_INVALID_URL,
    ERROR_URL_MUST_BE_TW,
    ERROR_TIMEOUT,
    ERROR_NO_SPECS,
    ERROR_NO_REVIEW_DATA,
    HTML_PARSER,
    REVIEW_CATEGORY_IDS,
)
from ..utils.validators import validate_url, validate_limit


class TennisWarehouseAPI:
    """Client for Tennis Warehouse's public website search"""

    def __init__(self):
        self.base_url = "https://www.tennis-warehouse.com"
        self.search_endpoint = f"{self.base_url}/search-tennis.html"
        self.timeout = int(os.getenv("TW_API_TIMEOUT", str(DEFAULT_TIMEOUT)))
        self.max_results = int(os.getenv("TW_MAX_RESULTS", str(DEFAULT_MAX_RESULTS)))

        print("Tennis Warehouse API initialized", file=sys.stderr)
        print(f"   Base URL: {self.base_url}", file=sys.stderr)
        print(f"   Timeout: {self.timeout}s", file=sys.stderr)

    def search_products(
        self, search_term: str = None, category: str = None, limit: int = 20
    ) -> Dict[str, Any]:
        """Search Tennis Warehouse website using public search endpoint

        Args:
            search_term: Search query string
            category: Product category filter (not implemented for website search)
            limit: Maximum number of results per page

        Returns:
            Dictionary containing HTML content and metadata for parsing
        """
        limit = validate_limit(limit, max_val=self.max_results)

        params = {
            "searchtext": search_term or "",
            "opt_perpage": limit,
            "opt_sort": "relevance",
            "opt_page": 1,
        }

        print(f"Search: Calling website search with params: {params}", file=sys.stderr)

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
            print("Success: Website search successful", file=sys.stderr)
            return result

        except requests.exceptions.Timeout:
            error_msg = f"{ERROR_TIMEOUT} after {self.timeout}s"
            print(f"Error: {error_msg}", file=sys.stderr)
            return {"error": error_msg}

        except requests.exceptions.RequestException as e:
            error_msg = f"API call failed: {str(e)}"
            print(f"Error: {error_msg}", file=sys.stderr)
            return {"error": error_msg}

    def get_categories(self) -> Dict[str, Any]:
        """Get available product categories"""
        from ..utils.constants import PRODUCT_CATEGORIES

        return {"categories": PRODUCT_CATEGORIES}

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
                return {"error": ERROR_INVALID_URL}

        is_valid, error = validate_url(product_url, "tennis-warehouse.com")
        if not is_valid:
            return {"error": error}

        print(f"Info: Fetching specs from: {product_url}", file=sys.stderr)

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

            soup = BeautifulSoup(response.text, HTML_PARSER)
            specs = self._extract_specs_from_page(soup)

            if not specs:
                return {
                    "error": ERROR_NO_SPECS,
                    "url": product_url,
                    "suggestion": "This product may not have detailed specs, or the page structure is different",
                }

            print(f"Success: Extracted {len(specs)} specifications", file=sys.stderr)
            return {"url": product_url, "specs": specs, "spec_count": len(specs)}

        except requests.exceptions.Timeout:
            error_msg = f"{ERROR_TIMEOUT} after {self.timeout}s"
            print(f"Error: {error_msg}", file=sys.stderr)
            return {"error": error_msg, "url": product_url}

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch product page: {str(e)}"
            print(f"Error: {error_msg}", file=sys.stderr)
            return {"error": error_msg, "url": product_url}

        except Exception as e:
            error_msg = f"Unexpected error parsing product specs: {str(e)}"
            print(f"Error: {error_msg}", file=sys.stderr)
            return {"error": error_msg, "url": product_url}

    def _extract_specs_from_page(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract specifications from product page HTML"""
        specs = {}
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
            rows = specs_table.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])

                # Two-column table
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        key = key.rstrip(":").strip()
                        specs[key] = value

                # Single-column table with <strong> tag
                elif len(cells) == 1:
                    cell = cells[0]
                    strong_tag = cell.find("strong")
                    if strong_tag:
                        key = strong_tag.get_text(strip=True).rstrip(":").strip()
                        full_text = cell.get_text(strip=True)
                        key_text = strong_tag.get_text(strip=True)
                        value = full_text.replace(key_text, "", 1).strip()
                        if key and value:
                            specs[key] = value

        # Try definition list if no table found
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

        return specs

    def get_product_review(self, review_url: str) -> Dict[str, Any]:
        """Extract review data from Tennis Warehouse review pages

        Extracts:
        - Performance scores (Power, Control, Maneuverability, etc.)
        - TWU Lab Data (Flex Rating, Swingweight, etc.)
        - Qualitative feedback (Positives, Negatives, Playtester Thoughts)

        Args:
            review_url: Full URL to the review page

        Returns:
            Dictionary containing review data or error message
        """
        is_valid, error = validate_url(review_url, "tennis-warehouse.com")
        if not is_valid:
            return {"error": error}

        print(f"Info: Fetching review from: {review_url}", file=sys.stderr)

        try:
            response = requests.get(
                review_url,
                timeout=self.timeout,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Tennis-Warehouse-MCP/1.0",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, HTML_PARSER)
            review_data = {
                "url": review_url,
                "scores": {},
                "lab_data": {},
                "feedback": {
                    "positives": [],
                    "negatives": [],
                    "playtester_thoughts": [],
                },
            }

            # Extract performance scores
            review_data["scores"] = self._extract_breakdown_scores(soup)

            # Extract lab data
            review_data["lab_data"] = self._extract_lab_data(soup)

            # Extract positives and negatives
            positives, negatives = self._extract_positives_negatives(soup)
            review_data["feedback"]["positives"] = positives
            review_data["feedback"]["negatives"] = negatives

            # Extract playtester thoughts
            review_data["feedback"]["playtester_thoughts"] = (
                self._extract_playtester_thoughts(soup)
            )

            if not review_data["scores"] and not review_data["lab_data"]:
                return {
                    "error": ERROR_NO_REVIEW_DATA,
                    "url": review_url,
                    "suggestion": "This may not be a valid review page, or the structure is different",
                }

            print(
                f"Success: Extracted {len(review_data['scores'])} scores, {len(review_data['lab_data'])} lab metrics",
                file=sys.stderr,
            )
            return review_data

        except requests.exceptions.Timeout:
            error_msg = f"{ERROR_TIMEOUT} after {self.timeout}s"
            print(f"Error: {error_msg}", file=sys.stderr)
            return {"error": error_msg, "url": review_url}

        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to fetch review page: {str(e)}"
            print(f"Error: {error_msg}", file=sys.stderr)
            return {"error": error_msg, "url": review_url}

        except Exception as e:
            error_msg = f"Failed to parse review data: {str(e)}"
            print(f"Error: {error_msg}", file=sys.stderr)
            return {"error": error_msg, "url": review_url}

    def _extract_breakdown_scores(self, soup: BeautifulSoup) -> Dict[str, float]:
        """Extract performance scores from Breakdown Summary table"""
        scores = {}
        breakdown_div = soup.find("div", id="breakdown_summary")
        if breakdown_div:
            table_div = breakdown_div.find_next_sibling(
                "div", class_="table-responsive"
            )
            if table_div:
                table = table_div.find("table")
                if table:
                    rows = table.find_all("tr")
                    for row in rows:
                        cells = row.find_all("td")
                        if len(cells) >= 2:
                            category = cells[0].get_text(strip=True)
                            score_cell = cells[1]

                            # Handle final_verdict specially
                            if category.lower() == "final verdict":
                                score_text = score_cell.get_text(strip=True)
                                score_match = re.search(
                                    r"(\d+(?:\.\d+)?)\s*/\s*10", score_text
                                )
                                if score_match:
                                    try:
                                        scores[category] = float(score_match.group(1))
                                    except ValueError:
                                        pass
                            else:
                                score_text = score_cell.get_text(strip=True)
                                try:
                                    scores[category] = float(score_text)
                                except ValueError:
                                    pass
        return scores

    def _extract_lab_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract TWU Lab Data from table"""
        lab_data = {}
        table_data_div = soup.find("div", id="table_data")
        if table_data_div:
            table_div = table_data_div.find_next_sibling(
                "div", class_="table-responsive"
            )
            if table_div:
                table = table_div.find("table")
                if table:
                    rows = table.find_all("tr")
                    header_row = rows[0] if rows else None
                    headers = []
                    if header_row:
                        headers = [
                            th.get_text(strip=True) for th in header_row.find_all("th")
                        ]

                    for row in rows[1:]:
                        cells = row.find_all("td")
                        if cells and headers:
                            metric = cells[0].get_text(strip=True)
                            for i, cell in enumerate(cells[1:], 1):
                                if i < len(headers):
                                    value = cell.get_text(strip=True)
                                    key = f"{metric} - {headers[i]}"
                                    lab_data[key] = value
        return lab_data

    def _extract_positives_negatives(self, soup: BeautifulSoup) -> tuple:
        """Extract positives and negatives from review"""
        positives = []
        negatives = []

        pos_neg_div = soup.find("div", id="positivesnegatives")
        if pos_neg_div:
            summary_lists = pos_neg_div.find_all("div", class_="review-summary_list")
            for summary_list in summary_lists:
                heading_div = summary_list.find(
                    "div", class_="review-summary_list_heading"
                )
                if heading_div:
                    heading_text = heading_div.get_text(strip=True).lower()

                    # Find all <p> tags in this summary list
                    paragraphs = summary_list.find_all("p")
                    items = []
                    for p in paragraphs:
                        # Split by <br> tags
                        text_parts = []
                        for content in p.contents:
                            if content.name == "br":
                                continue
                            text = str(content).strip()
                            if text:
                                text_parts.append(text)

                        # Join and split again to handle multiple items
                        full_text = " ".join(text_parts)
                        for item in full_text.split("\n"):
                            item = item.strip()
                            if item:
                                items.append(item)

                    if "positive" in heading_text:
                        positives = items
                    elif "negative" in heading_text:
                        negatives = items

        return positives, negatives

    def _extract_playtester_thoughts(self, soup: BeautifulSoup) -> list:
        """Extract playtester thoughts from review"""
        thoughts = []

        for cat_id in REVIEW_CATEGORY_IDS:
            cat_div = soup.find("div", id=cat_id)
            if cat_div:
                next_elem = cat_div.find_next_sibling()
                count = 0
                while next_elem and count < 5:
                    if next_elem.name == "div":
                        paragraphs = next_elem.find_all("p")
                        for p in paragraphs:
                            text = p.get_text(strip=True)
                            if text and len(text) > 50:
                                thoughts.append(text)
                    next_elem = next_elem.find_next_sibling()
                    count += 1

                    if next_elem and next_elem.get("id") in REVIEW_CATEGORY_IDS:
                        break

        return thoughts[:10]  # Limit to 10
