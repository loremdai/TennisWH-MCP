"""Helper functions for tools"""

from typing import Dict, Any, List


def generate_search_suggestions(
    insights: Dict[str, Any], query: str, sample_products: List[Dict[str, Any]] = None
) -> str:
    """Generate friendly suggestions based on search insights with sample products"""

    if "error" in insights:
        return f"Error: Unable to analyze search results: {insights['error']}"

    total_products = insights.get("total_products", 0)
    brands = insights.get("brands", [])
    types = insights.get("types", [])

    if total_products == 0:
        return f"Search: No results found for '{query}'. Try a different search term or browse our categories."

    suggestions = []
    suggestions.append(f"I found {total_products} results for '{query}'!")

    # Add sample products with web-search-style source citations
    if sample_products:
        suggestions.append("\n📋 **Top Results:**")
        for i, product in enumerate(sample_products[:3], 1):
            name = product.get("name", "Unknown Product")
            price = product.get("price", "Price not available")
            brand = product.get("brand", "")

            # Clean product name (remove embedded citations)
            clean_name = (
                name.split(" [Tennis Warehouse]")[0]
                if " [Tennis Warehouse]" in name
                else name
            )

            # Create web-search-style entry
            suggestions.append(f"**{clean_name}** - {price}")
            if brand:
                suggestions.append(f"*{brand}* • Available now")

            # Add clickable Tennis Warehouse source badge
            if product.get("product_url"):
                suggestions.append(
                    f"[🛒 Tennis Warehouse - View & Purchase]({product['product_url']})"
                )
            suggestions.append("")  # Add spacing between products

    if len(brands) > 0 or len(types) > 0:
        suggestions.append("💡 I can see there are many options. Would you like to:")

        option_num = 1
        if len(brands) > 0:
            brand_names = [
                b.get("display_name", b.get("name", ""))
                .replace(" Tennis Balls", "")
                .replace(" Tennis", "")
                for b in brands[:5]
            ]
            suggestions.append(
                f"   {option_num}. Filter by brand? (Available: {', '.join(brand_names)}{', and more...' if len(brands) > 5 else ''})"
            )
            option_num += 1

        if len(types) > 0:
            type_names = [t.get("display_name", t.get("name", "")) for t in types[:5]]
            suggestions.append(
                f"   {option_num}. Filter by type? (Available: {', '.join(type_names)}{', and more...' if len(types) > 5 else ''})"
            )
            option_num += 1

        suggestions.append(f"   {option_num}. Get a summary of the different options?")
        option_num += 1
        suggestions.append(f"   {option_num}. List all {total_products} results?")

        suggestions.append(
            f"\n🎯 Just type the number (1-{option_num - 1}) to choose an option!"
        )
        suggestions.append(
            "\n*All product information from Tennis Warehouse - click links to view and purchase.*"
        )
    else:
        suggestions.append(f"\n📋 Here are the {total_products} results I found:")

    return "\n".join(suggestions)


def handle_search_option(
    option: str, insights: Dict[str, Any], query: str
) -> Dict[str, Any]:
    """Handle user's search option selection"""

    if "error" in insights:
        return {"error": insights["error"]}

    try:
        option_num = int(option)
    except ValueError:
        return {
            "error": "Invalid option. Please provide a number.",
            "available_options": "1-4 depending on available filters",
        }

    brands = insights.get("brands", [])
    types = insights.get("types", [])

    # Determine what option_num means based on available filters
    current_option = 1

    # Option 1: Filter by brand (if brands available)
    if len(brands) > 0:
        if option_num == current_option:
            return {
                "action": "filter_by_brand",
                "available_brands": [
                    b.get("display_name", b.get("name", "")) for b in brands
                ],
                "message": f"Here are the available brands: {', '.join([b.get('display_name', b.get('name', '')) for b in brands[:10]])}",
            }
        current_option += 1

    # Option 2: Filter by type (if types available)
    if len(types) > 0:
        if option_num == current_option:
            return {
                "action": "filter_by_type",
                "available_types": [
                    t.get("display_name", t.get("name", "")) for t in types
                ],
                "message": f"Here are the available types: {', '.join([t.get('display_name', t.get('name', '')) for t in types[:10]])}",
            }
        current_option += 1

    # Option 3: Get summary
    if option_num == current_option:
        summary = f"Summary for '{query}':\n"
        summary += f"- Total products: {insights.get('total_products', 0)}\n"
        if brands:
            summary += f"- Available brands: {len(brands)}\n"
        if types:
            summary += f"- Available types: {len(types)}\n"
        return {"action": "show_summary", "summary": summary}

    current_option += 1

    # Option 4: List all results
    if option_num == current_option:
        return {
            "action": "list_all",
            "message": f"Listing all {insights.get('total_products', 0)} results for '{query}'",
        }

    return {"error": f"Invalid option number: {option_num}"}
