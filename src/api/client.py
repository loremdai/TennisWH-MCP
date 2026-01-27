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
        """Extract performance scores from review tables

        Supports multiple table structures:
        1. Tables with id="breakdown_summary"
        2. Tables with class="racquet_rate_table"
        3. Tables containing "Overall" score (fallback)
        """
        scores = {}

        # Method 1: Try breakdown_summary div (original structure)
        breakdown_div = soup.find("div", id="breakdown_summary")
        if breakdown_div:
            table_div = breakdown_div.find_next_sibling(
                "div", class_="table-responsive"
            )
            if table_div:
                table = table_div.find("table")
                if table:
                    scores = self._parse_score_table(table)
                    if scores:
                        return scores

        # Method 2: Try racquet_rate_table class
        rate_table = soup.find("table", class_="racquet_rate_table")
        if rate_table:
            scores = self._parse_score_table(rate_table)
            if scores:
                return scores

        # Method 3: Fallback - find table containing "Overall" score
        all_tables = soup.find_all("table")
        for table in all_tables:
            # Check if this table contains "Overall" text
            overall_cell = table.find(
                lambda tag: tag.name in ["th", "td"]
                and "overall" in tag.get_text(strip=True).lower()
            )
            if overall_cell:
                scores = self._parse_score_table(table)
                if scores:
                    return scores

        return scores

    def _parse_score_table(self, table) -> Dict[str, float]:
        """Parse scores from a table element"""
        scores = {}
        rows = table.find_all("tr")

        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) >= 2:
                category = cells[0].get_text(strip=True)
                score_cell = cells[1]

                # Skip header rows
                if category.lower() in ["category", "metric", ""]:
                    continue

                # Handle final_verdict specially
                if category.lower() == "final verdict":
                    score_text = score_cell.get_text(strip=True)
                    score_match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", score_text)
                    if score_match:
                        try:
                            scores[category] = float(score_match.group(1))
                        except ValueError:
                            pass
                else:
                    score_text = score_cell.get_text(strip=True)
                    # Try to extract number from text like "87" or "8.5"
                    score_match = re.search(r"(\d+(?:\.\d+)?)", score_text)
                    if score_match:
                        try:
                            scores[category] = float(score_match.group(1))
                        except ValueError:
                            pass

        return scores

    def _extract_lab_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract TWU Lab Data and Tech Specs from tables
        
        Supports multiple table structures:
        1. header/div with id="table_data" or "tech_specs" followed by table
        2. Tables with class="racquet_specs_table"
        """
        lab_data = {}
        
        # Method 1: Try finding header or div with specific IDs
        for section_id in ["table_data", "tech_specs"]:
            # Try header first (newer structure)
            section = soup.find("header", id=section_id)
            if not section:
                # Fallback to div (older structure)
                section = soup.find("div", id=section_id)
            
            if section:
                # Look for table in next sibling or within a div wrapper
                next_elem = section.find_next_sibling()
                if next_elem:
                    # Check if next sibling is a div containing a table
                    if next_elem.name == "div":
                        table = next_elem.find("table")
                        if table:
                            data = self._parse_lab_table(table)
                            lab_data.update(data)
                    # Or if next sibling is directly a table
                    elif next_elem.name == "table":
                        data = self._parse_lab_table(next_elem)
                        lab_data.update(data)
        
        if lab_data:
            return lab_data
        
        # Method 2: Try racquet_specs_table class
        specs_table = soup.find("table", class_="racquet_specs_table")
        if specs_table:
            lab_data = self._parse_lab_table(specs_table)
        
        return lab_data

    def _parse_lab_table(self, table) -> Dict[str, str]:
        """Parse lab data from a table element"""
        lab_data = {}
        rows = table.find_all("tr")

        # Try to find header row
        header_row = rows[0] if rows else None
        headers = []
        if header_row:
            headers = [
                th.get_text(strip=True) for th in header_row.find_all(["th", "td"])
            ]

        # Parse data rows
        for row in rows[1:] if len(rows) > 1 else rows:
            cells = row.find_all(["td", "th"])
            if cells:
                metric = cells[0].get_text(strip=True)

                # Skip empty or header-like rows
                if not metric or metric.lower() in ["metric", "specification", ""]:
                    continue

                # If we have headers, use them
                if headers and len(headers) > 1:
                    for i, cell in enumerate(cells[1:], 1):
                        if i < len(headers):
                            value = cell.get_text(strip=True)
                            if value:
                                key = f"{metric} - {headers[i]}"
                                lab_data[key] = value
                else:
                    # No headers, just use metric: value
                    if len(cells) >= 2:
                        value = cells[1].get_text(strip=True)
                        if value:
                            lab_data[metric] = value

        return lab_data

    def _extract_positives_negatives(self, soup: BeautifulSoup) -> tuple:
        """Extract positives and negatives from review

        Supports multiple structures:
        1. .review-summary_list containers with icon-based headers
        2. div#positivesnegatives with text-based headers
        """
        positives = []
        negatives = []

        # Method 1: Try .review-summary_list containers (newer structure)
        summary_lists = soup.find_all("div", class_="review-summary_list")
        for summary_list in summary_lists:
            header = summary_list.find("div", class_="review-summary_list_header")
            body = summary_list.find("div", class_="review-summary_list_body")

            if header and body:
                # Check for icon in header (green check = positive, red x = negative)
                header_html = str(header)
                is_positive = (
                    "check" in header_html.lower() or "positive" in header_html.lower()
                )
                is_negative = (
                    "times" in header_html.lower()
                    or "negative" in header_html.lower()
                    or "close" in header_html.lower()
                )

                # Extract items from body
                items = []
                # Try to find paragraphs or direct text
                paragraphs = body.find_all("p")
                if paragraphs:
                    for p in paragraphs:
                        text = p.get_text("\n", strip=True)
                        for line in text.split("\n"):
                            line = line.strip()
                            if line and len(line) > 1:
                                items.append(line)
                else:
                    # Try direct text content
                    text = body.get_text("\n", strip=True)
                    for line in text.split("\n"):
                        line = line.strip()
                        if line and len(line) > 1:
                            items.append(line)

                if is_positive and items:
                    positives = items
                elif is_negative and items:
                    negatives = items

        # Method 2: Fallback to old structure
        if not positives and not negatives:
            pos_neg_div = soup.find("div", id="positivesnegatives")
            if pos_neg_div:
                summary_lists = pos_neg_div.find_all(
                    "div", class_="review-summary_list"
                )
                for summary_list in summary_lists:
                    heading_div = summary_list.find(
                        "div", class_="review-summary_list_heading"
                    )
                    if heading_div:
                        heading_text = heading_div.get_text(strip=True).lower()
                        paragraphs = summary_list.find_all("p")
                        items = []
                        for p in paragraphs:
                            text = p.get_text("\n", strip=True)
                            for line in text.split("\n"):
                                line = line.strip()
                                if line:
                                    items.append(line)

                        if "positive" in heading_text:
                            positives = items
                        elif "negative" in heading_text:
                            negatives = items

        # Method 3: Handle duplicate IDs with simple p/br structure
        if not positives and not negatives:
            all_pos_neg = soup.find_all("div", id="positivesnegatives")
            if len(all_pos_neg) >= 2:
                # First occurrence = positives, second = negatives
                for i, div in enumerate(all_pos_neg[:2]):
                    items = []
                    paragraphs = div.find_all("p")
                    for p in paragraphs:
                        for text in p.stripped_strings:
                            text = text.strip()
                            if text and len(text) > 1:
                                items.append(text)

                    if i == 0:
                        positives = items
                    else:
                        negatives = items
            elif len(all_pos_neg) == 1:
                # Only one div, extract all items as positives
                div = all_pos_neg[0]
                paragraphs = div.find_all("p")
                for p in paragraphs:
                    for text in p.stripped_strings:
                        text = text.strip()
                        if text and len(text) > 1:
                            positives.append(text)

        return positives, negatives

    def _extract_playtester_thoughts(self, soup: BeautifulSoup) -> list:
        """Extract playtester thoughts from review

        Supports multiple structures:
        1. .review-playtesters_section containers (detailed feedback)
        2. Category-based paragraphs (original structure)
        """
        thoughts = []

        # Method 1: Try .review-playtesters_section (newer structure)
        playtester_sections = soup.find_all("div", class_="review-playtesters_section")
        for section in playtester_sections:
            # Extract all paragraphs from this section
            paragraphs = section.find_all("p")
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Filter out very short text and headers
                if text and len(text) > 50 and not text.endswith(":"):
                    thoughts.append(text)

        # Method 2: Try category-based extraction (original structure)
        if not thoughts:
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

        return thoughts[:20]  # Limit to 20 (increased from 10)
