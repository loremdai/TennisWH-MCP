#!/usr/bin/env python3
"""
Tennis Warehouse MCP Server - Secure API Gateway for LLMs
"""

import sys
import os
from typing import List, Dict, Any, Optional

try:
    from mcp.server.fastmcp import FastMCP
    print(f"✅ MCP imported successfully", file=sys.stderr)
except Exception as e:
    print(f"❌ Failed to import MCP: {e}", file=sys.stderr)
    sys.exit(1)

#from mcp.server.fastmcp import FastMCP
from tennis_warehouse_api import (
    TennisWarehouseAPI, 
    extract_products, 
    extract_categories,
    extract_price_ranges,
    extract_search_insights
)

# Initialize MCP server
mcp = FastMCP("tennis-warehouse")

# Initialize API client
try:
    tw_api = TennisWarehouseAPI()
    print("✅ Tennis Warehouse MCP server starting up...", file=sys.stderr)
except Exception as e:
    print(f"❌ Failed to initialize Tennis Warehouse API: {e}", file=sys.stderr)
    sys.exit(1)

@mcp.tool()
def search_tennis_products(
    query: str,
    category: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """Search Tennis Warehouse products with intelligent filtering.
    
    Args:
        query: Search term (e.g., "wilson racquet", "nike shoes", "head bag")
        category: Product category filter (e.g., "RACQUETS", "SHOES", "BAGS")
        max_results: Maximum number of results (1-20, default: 10)
    
    Returns:
        List of products with name, brand, price, availability, and URL
    """
    
    print(f"🔍 Searching products: query='{query}', category={category}", file=sys.stderr)
    
    # Input validation
    if not query or len(query.strip()) < 2:
        return [{"error": "Search query must be at least 2 characters"}]
        
    if max_results > 20:
        max_results = 20
    elif max_results < 1:
        max_results = 10
    
    # Map common category aliases
    category_mapping = {
        "BAGS": "SHOULDBAGS",
        "BAG": "SHOULDBAGS", 
        "MENS_SHOES": "MENSSHOES",
        "WOMENS_SHOES": "WOMENSSHOES",
        "MEN_SHOES": "MENSSHOES",
        "WOMEN_SHOES": "WOMENSSHOES"
    }
    
    if category:
        category = category_mapping.get(category.upper(), category.upper())
    
    # Call API
    raw_response = tw_api.search_products(
        search_term=query,
        category=category,
        limit=max_results
    )
    
    # Transform for LLM consumption
    products = extract_products(raw_response)
    
    # Check if we should provide smart search suggestions
    insights = extract_search_insights(raw_response)
    
    # Criteria for smart search: many results + multiple filter options
    should_use_smart_search = (
        len(products) >= 8 and  # Many results
        not any("error" in str(p) for p in products) and  # No errors
        (len(insights.get("brands", [])) >= 3 or len(insights.get("types", [])) >= 3)  # Multiple filter options
    )
    
    if should_use_smart_search:
        print(f"🧠 Using smart search - found {len(products)} products with filtering options", file=sys.stderr)
        
        # Provide conversational suggestions
        suggestions = generate_search_suggestions(insights, query, products[:3])
        
        # Format sample products with source citations
        formatted_samples = []
        for product in products[:3]:
            # Include citation directly in the description for better visibility
            name_with_source = product.get("name", "Unknown Product")
            if product.get("source_citation"):
                name_with_source += f" {product['source_citation']}"
            
            formatted_product = {
                "name": name_with_source,
                "brand": product.get("brand", "Unknown Brand"),
                "price": product.get("price", "Price not available"),
                "availability": product.get("availability", "Unknown"),
                "source": product.get("source_citation", ""),
                "product_url": product.get("product_url", "")
            }
            formatted_samples.append(formatted_product)
        
        # Return smart search response with suggestions + sample products
        smart_response = [{
            "type": "smart_search_suggestions",
            "query": query,
            "total_products": len(products),
            "suggestions": suggestions,
            "sample_products": formatted_samples,
            "source_info": "All product information and pricing from Tennis Warehouse. Click source links to view full details and purchase."
        }]
        
        return smart_response
    else:
        # Add source citations to standard results too and make them prominent
        for product in products:
            if product.get("product_url") and "source_citation" not in product:
                product["source_citation"] = f"[Tennis Warehouse]({product['product_url']})"
            
            # Add citation to product name for better visibility
            if product.get("source_citation") and not product.get("name", "").endswith("]"):
                product["name"] = f"{product.get('name', 'Unknown Product')} {product['source_citation']}"
        
        print(f"✅ Found {len(products)} products (using standard search)", file=sys.stderr)
        return products

@mcp.tool()
def search_tennis_bags(
    style: Optional[str] = None,
    brand: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """Search specifically for tennis bags with advanced filtering.
    
    Args:
        style: Bag style (e.g., "backpack", "tote", "duffel", "6 pack", "12 pack")
        brand: Brand filter (e.g., "Wilson", "Head", "Babolat", "Nike")
        max_results: Maximum number of results (1-20, default: 10)
    
    Returns:
        List of tennis bags with specifications and features
    """
    
    print(f"🎾 Searching bags: style={style}, brand={brand}", file=sys.stderr)
    
    if max_results > 20:
        max_results = 20
    elif max_results < 1:
        max_results = 10
    
    # Get all bags first
    raw_response = tw_api.search_bags(limit=max_results * 2)  # Get more to filter
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
                "wheeled": ["wheel", "rolling", "roll"]
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
    
    # Check if we should provide smart search suggestions
    insights = extract_search_insights(raw_response)
    query_term = f"{style or ''} {brand or ''} tennis bags".strip()
    
    # Criteria for smart search: many results + multiple filter options
    should_use_smart_search = (
        len(filtered_bags) >= 6 and  # Many bags found
        (len(insights.get("brands", [])) >= 3 or len(insights.get("types", [])) >= 3)  # Multiple filter options
    )
    
    if should_use_smart_search:
        print(f"🧠 Using smart search for bags - found {len(filtered_bags)} bags with filtering options", file=sys.stderr)
        
        # Provide conversational suggestions
        suggestions = generate_search_suggestions(insights, query_term)
        
        # Return smart search response
        smart_response = [{
            "type": "smart_search_suggestions",
            "query": query_term,
            "total_products": len(filtered_bags),
            "suggestions": suggestions,
            "sample_products": filtered_bags[:3]  # Show first 3 as examples
        }]
        
        return smart_response
    else:
        print(f"✅ Found {len(filtered_bags)} matching bags (using standard search)", file=sys.stderr)
        return filtered_bags

@mcp.tool()
def search_tennis_racquets(
    brand: Optional[str] = None,
    weight_range: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """Search for tennis racquets with brand and weight filtering.
    
    Args:
        brand: Racquet brand (e.g., "Wilson", "Head", "Babolat", "Yonex")
        weight_range: Weight preference (e.g., "light", "medium", "heavy")
        max_results: Maximum number of results (1-20, default: 10)
    
    Returns:
        List of tennis racquets with specifications
    """
    
    print(f"🎾 Searching racquets: brand={brand}, weight={weight_range}", file=sys.stderr)
    
    if max_results > 20:
        max_results = 20
    elif max_results < 1:
        max_results = 10
    
    # Build search term
    search_term = "racquet"
    if brand:
        search_term = f"{brand} racquet"
    
    raw_response = tw_api.search_products(
        search_term=search_term,
        category="RACQUETS",
        limit=max_results
    )
    
    products = extract_products(raw_response)
    
    # TODO: Add weight filtering when we understand the data structure better
    if weight_range:
        print(f"ℹ️  Weight filtering ({weight_range}) not yet implemented", file=sys.stderr)
    
    # Check if we should provide smart search suggestions
    insights = extract_search_insights(raw_response)
    query_term = f"{brand or ''} tennis racquet".strip()
    
    # Criteria for smart search: many results + multiple filter options
    should_use_smart_search = (
        len(products) >= 6 and  # Many racquets found
        not any("error" in str(p) for p in products) and  # No errors
        (len(insights.get("brands", [])) >= 3 or len(insights.get("types", [])) >= 3)  # Multiple filter options
    )
    
    if should_use_smart_search:
        print(f"🧠 Using smart search for racquets - found {len(products)} racquets with filtering options", file=sys.stderr)
        
        # Provide conversational suggestions
        suggestions = generate_search_suggestions(insights, query_term)
        
        # Return smart search response
        smart_response = [{
            "type": "smart_search_suggestions",
            "query": query_term,
            "total_products": len(products),
            "suggestions": suggestions,
            "sample_products": products[:3]  # Show first 3 as examples
        }]
        
        return smart_response
    else:
        print(f"✅ Found {len(products)} racquets (using standard search)", file=sys.stderr)
        return products

@mcp.tool()
def search_tennis_shoes(
    gender: Optional[str] = None,
    brand: Optional[str] = None,
    court_type: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]:
    """Search for tennis shoes with gender, brand, and court type filtering.
    
    Args:
        gender: Target gender ("men", "women", "unisex")
        brand: Shoe brand (e.g., "Nike", "Adidas", "Asics", "New Balance")
        court_type: Court surface (e.g., "hard court", "clay court", "all court")
        max_results: Maximum number of results (1-20, default: 10)
    
    Returns:
        List of tennis shoes with specifications
    """
    
    print(f"👟 Searching shoes: gender={gender}, brand={brand}, court={court_type}", file=sys.stderr)
    
    if max_results > 20:
        max_results = 20
    elif max_results < 1:
        max_results = 10
    
    # Determine category based on gender
    category = None
    if gender:
        gender_lower = gender.lower()
        if gender_lower in ["men", "mens", "male"]:
            category = "MENSSHOES"
        elif gender_lower in ["women", "womens", "female"]:
            category = "WOMENSSHOES"
    
    # Build search term
    search_terms = ["shoes"]
    if brand:
        search_terms.insert(0, brand)
    if court_type:
        search_terms.append(court_type.replace(" court", ""))
    
    search_term = " ".join(search_terms)
    
    raw_response = tw_api.search_products(
        search_term=search_term,
        category=category,
        limit=max_results
    )
    
    products = extract_products(raw_response)
    
    # Check if we should provide smart search suggestions
    insights = extract_search_insights(raw_response)
    query_term = f"{gender or ''} {brand or ''} {court_type or ''} tennis shoes".strip()
    
    # Criteria for smart search: many results + multiple filter options
    should_use_smart_search = (
        len(products) >= 6 and  # Many shoes found
        not any("error" in str(p) for p in products) and  # No errors
        (len(insights.get("brands", [])) >= 3 or len(insights.get("types", [])) >= 3)  # Multiple filter options
    )
    
    if should_use_smart_search:
        print(f"🧠 Using smart search for shoes - found {len(products)} shoes with filtering options", file=sys.stderr)
        
        # Provide conversational suggestions
        suggestions = generate_search_suggestions(insights, query_term)
        
        # Return smart search response
        smart_response = [{
            "type": "smart_search_suggestions",
            "query": query_term,
            "total_products": len(products),
            "suggestions": suggestions,
            "sample_products": products[:3]  # Show first 3 as examples
        }]
        
        return smart_response
    else:
        print(f"✅ Found {len(products)} shoes (using standard search)", file=sys.stderr)
        return products

@mcp.tool()
def get_product_categories() -> List[Dict[str, str]]:
    """Get all available product categories with product counts.
    
    Returns:
        List of categories with names, codes, and product counts
    """
    
    print(f"📂 Getting product categories", file=sys.stderr)
    
    raw_response = tw_api.get_categories()
    categories = extract_categories(raw_response)
    
    print(f"✅ Found {len(categories)} categories", file=sys.stderr)
    return categories

@mcp.tool()
def check_product_availability(product_name: str) -> Dict[str, Any]:
    """Check if a specific product is in stock.
    
    Args:
        product_name: Exact or partial product name to check
    
    Returns:
        Availability status with product details
    """
    
    print(f"📦 Checking availability for: {product_name}", file=sys.stderr)
    
    if not product_name or len(product_name.strip()) < 2:
        return {"error": "Product name must be at least 2 characters"}
    
    raw_response = tw_api.check_availability(product_name)
    products = extract_products(raw_response)
    
    if not products or "error" in products[0]:
        return {"found": False, "message": "Product not found", "error": products[0].get("error") if products else None}
    
    # Return the best match
    best_match = products[0]
    
    result = {
        "found": True,
        "name": best_match.get("name"),
        "brand": best_match.get("brand"),
        "price": best_match.get("price"),
        "in_stock": best_match.get("in_stock", False),
        "availability": best_match.get("availability", "Unknown"),
        "product_url": best_match.get("product_url")
    }
    
    print(f"✅ Product found: {result['name']} - {result['availability']}", file=sys.stderr)
    return result

@mcp.tool()
def get_tennis_deals(category: Optional[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
    """Find current deals and discounted tennis products.
    
    Args:
        category: Product category to search for deals (e.g., "RACQUETS", "SHOES")
        max_results: Maximum number of deals to return (1-20, default: 10)
    
    Returns:
        List of discounted products with deal information
    """
    
    print(f"💰 Looking for deals in category: {category}", file=sys.stderr)
    
    if max_results > 20:
        max_results = 20
    elif max_results < 1:
        max_results = 10
    
    # Search for terms that typically indicate sales/deals
    deal_terms = ["sale", "clearance", "discount", "special"]
    
    all_deals = []
    for term in deal_terms:
        raw_response = tw_api.search_products(
            search_term=term,
            category=category,
            limit=max_results
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
    
    print(f"✅ Found {len(unique_deals)} deals", file=sys.stderr)
    return unique_deals

# Helper functions for conversational search
def generate_search_suggestions(insights: Dict[str, Any], query: str, sample_products: List[Dict[str, Any]] = None) -> str:
    """Generate friendly suggestions based on search insights with sample products"""
    
    if "error" in insights:
        return f"❌ Unable to analyze search results: {insights['error']}"
    
    total_products = insights.get("total_products", 0)
    brands = insights.get("brands", [])
    types = insights.get("types", [])
    
    if total_products == 0:
        return f"🔍 No results found for '{query}'. Try a different search term or browse our categories."
    
    suggestions = []
    suggestions.append(f"🎾 I found {total_products} results for '{query}'!")
    
    # Add sample products with web-search-style source citations
    if sample_products:
        suggestions.append(f"\n📋 **Top Results:**")
        for i, product in enumerate(sample_products[:3], 1):
            name = product.get("name", "Unknown Product")
            price = product.get("price", "Price not available")
            brand = product.get("brand", "")
            
            # Clean product name (remove embedded citations)
            clean_name = name.split(" [Tennis Warehouse]")[0] if " [Tennis Warehouse]" in name else name
            
            # Create web-search-style entry
            suggestions.append(f"**{clean_name}** - {price}")
            if brand:
                suggestions.append(f"*{brand}* • Available now")
            
            # Add clickable Tennis Warehouse source badge
            if product.get("product_url"):
                suggestions.append(f"[🛒 Tennis Warehouse - View & Purchase]({product['product_url']})")
            suggestions.append("")  # Add spacing between products
    
    if len(brands) > 0 or len(types) > 0:
        suggestions.append(f"💡 I can see there are many options. Would you like to:")
        
        option_num = 1
        if len(brands) > 0:
            brand_names = [b.get("display_name", b.get("name", "")).replace(" Tennis Balls", "").replace(" Tennis", "") for b in brands[:5]]
            suggestions.append(f"   {option_num}. Filter by brand? (Available: {', '.join(brand_names)}{', and more...' if len(brands) > 5 else ''})")
            option_num += 1
            
        if len(types) > 0:
            type_names = [t.get("display_name", t.get("name", "")) for t in types[:5]]
            suggestions.append(f"   {option_num}. Filter by type? (Available: {', '.join(type_names)}{', and more...' if len(types) > 5 else ''})")
            option_num += 1
            
        suggestions.append(f"   {option_num}. Get a summary of the different options?")
        option_num += 1
        suggestions.append(f"   {option_num}. List all {total_products} results?")
        
        suggestions.append(f"\n🎯 Just type the number (1-{option_num-1}) to choose an option!")
        suggestions.append(f"\n*All product information from Tennis Warehouse - click links to view and purchase.*")
    else:
        suggestions.append(f"\n📋 Here are the {total_products} results I found:")
    
    return "\n".join(suggestions)

@mcp.tool()
def smart_search_tennis(
    query: str,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """Intelligent tennis product search with conversational filtering options.
    
    This tool searches for tennis products and analyzes the results to offer 
    smart filtering options like brand filters, type filters, summaries, etc.
    
    Args:
        query: Search term (e.g., "tennis balls", "wilson racquet", "nike shoes")
        max_results: Maximum number of results to analyze (1-50, default: 20)
    
    Returns:
        Search results with intelligent suggestions for filtering
    """
    
    print(f"🧠 Smart search: '{query}'", file=sys.stderr)
    
    # Input validation
    if not query or len(query.strip()) < 2:
        return [{"error": "Search query must be at least 2 characters"}]
        
    if max_results > 50:
        max_results = 50
    elif max_results < 1:
        max_results = 20
    
    # Call website search
    raw_response = tw_api.search_products(
        search_term=query,
        limit=max_results
    )
    
    # Extract insights and products
    insights = extract_search_insights(raw_response)
    products = extract_products(raw_response)
    
    # Generate suggestions with sample products
    suggestions = generate_search_suggestions(insights, query, products[:3])
    
    # Add sample products with citations to the main result
    sample_products = []
    if products and not any("error" in p for p in products):
        for product in products[:3]:
            # Add citation to product name for visibility
            name_with_source = product.get("name", "Unknown Product")
            if product.get("source_citation"):
                name_with_source += f" {product['source_citation']}"
            
            sample_product = {
                "name": name_with_source,
                "brand": product.get("brand", "Unknown Brand"),
                "price": product.get("price", "Price not available"),
                "availability": product.get("availability", "Unknown"),
                "product_url": product.get("product_url", ""),
                "source_citation": product.get("source_citation", "")
            }
            sample_products.append(sample_product)
    
    # Return consolidated result
    result = [{
        "suggestions": suggestions, 
        "insights": insights,
        "sample_products": sample_products,
        "source_info": "All product information and pricing from Tennis Warehouse. Click source links to view full details and purchase." if sample_products else ""
    }]
    
    print(f"✅ Smart search complete: {insights.get('total_products', 0)} products found", file=sys.stderr)
    return result

@mcp.tool()
def handle_search_option(
    query: str,
    option_number: int,
    max_results: int = 20
) -> List[Dict[str, Any]]:
    """Handle user selection from smart search options.
    
    Args:
        query: Original search query
        option_number: User's choice (1=filter by brand, 2=filter by type, 3=summary, 4=list all)
        max_results: Maximum number of results (1-50, default: 20)
    
    Returns:
        Results based on user's selection
    """
    
    print(f"🎯 Handling option {option_number} for query '{query}'", file=sys.stderr)
    
    # Get search insights first
    raw_response = tw_api.search_products(search_term=query, limit=max_results)
    insights = extract_search_insights(raw_response)
    
    if "error" in insights:
        return [{"error": insights["error"]}]
    
    brands = insights.get("brands", [])
    types = insights.get("types", [])
    total_products = insights.get("total_products", 0)
    
    # Handle different options
    if option_number == 1 and len(brands) > 0:
        # Filter by brand
        brand_options = []
        for i, brand in enumerate(brands[:10], 1):  # Show top 10 brands
            brand_options.append(f"   {i}. {brand.get('display_name', brand.get('name', 'Unknown'))}")
        
        response = f"🏷️ Available brands for '{query}':\n\n" + "\n".join(brand_options)
        response += f"\n\n💡 Type the brand number to filter, or tell me the brand name you want!"
        
        return [{"brand_options": response, "brands": brands}]
        
    elif option_number == 2 and len(types) > 0:
        # Filter by type
        type_options = []
        for i, type_item in enumerate(types[:10], 1):  # Show top 10 types
            type_options.append(f"   {i}. {type_item.get('display_name', type_item.get('name', 'Unknown'))}")
        
        response = f"🎯 Available types for '{query}':\n\n" + "\n".join(type_options)
        response += f"\n\n💡 Type the type number to filter, or tell me the type you want!"
        
        return [{"type_options": response, "types": types}]
        
    elif option_number == 3:
        # Summary of options with sample products
        products = extract_products(raw_response)
        
        summary = f"📊 Summary for '{query}' ({total_products} results):\n\n"
        
        if len(brands) > 0:
            brand_names = [b.get("display_name", b.get("name", "")).replace(" Tennis Balls", "").replace(" Tennis", "") for b in brands]
            summary += f"🏷️ **Available Brands:** {', '.join(brand_names)}\n\n"
        
        if len(types) > 0:
            type_names = [t.get("display_name", t.get("name", "")) for t in types]
            summary += f"🎯 **Available Types:** {', '.join(type_names)}\n\n"
        
        # Add sample products with sources
        if products and not any("error" in p for p in products):
            summary += f"📋 **Sample Products:**\n"
            for i, product in enumerate(products[:3], 1):
                name = product.get("name", "Unknown Product")
                price = product.get("price", "Price not available")
                source = product.get("source_citation", "")
                if not source and product.get("product_url"):
                    source = f"[Tennis Warehouse]({product['product_url']})"
                summary += f"{i}. **{name}** - {price}\n"
                if product.get("product_url"):
                    summary += f"   [🛒 Tennis Warehouse - View Product]({product['product_url']})\n"
            summary += "\n"
        
        summary += f"💡 You can filter by any of these options or browse all {total_products} results!"
        summary += f"\n\n*All products available on Tennis Warehouse - click links to view and purchase.*"
        
        return [{"summary": summary, "insights": insights}]
        
    elif option_number == 4:
        # List all results with source citations
        products = extract_products(raw_response)
        
        if products and not any("error" in p for p in products):
            # Ensure all products have prominent source citations
            for product in products:
                if product.get("product_url") and "source_citation" not in product:
                    product["source_citation"] = f"[Tennis Warehouse]({product['product_url']})"
                
                # Add clickable source badge instead of embedding in name
                if product.get("product_url"):
                    product["source_badge"] = f"[🛒 Tennis Warehouse]({product['product_url']})"
            
            response = f"📋 All {len(products)} results for '{query}' from Tennis Warehouse:"
            return [{"message": response, "source_info": "Click source links to view full details and purchase on Tennis Warehouse"}] + products
        else:
            return [{"error": "Unable to retrieve product list"}]
    
    else:
        return [{"error": f"Invalid option {option_number}. Please choose 1 (brands), 2 (types), 3 (summary), or 4 (list all)."}]

if __name__ == "__main__":
    print("🎾 Starting Tennis Warehouse MCP Server...", file=sys.stderr)
    mcp.run()