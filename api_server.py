#!/usr/bin/env python3
"""
Tennis Warehouse Public API Server
FastAPI wrapper for MCP functionality to enable public access
"""

import sys
import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import our existing Tennis Warehouse functionality
from tennis_warehouse_api import (
    TennisWarehouseAPI, 
    extract_products, 
    extract_search_insights
)

# Import MCP functions (but remove MCP decorators)
import importlib.util
spec = importlib.util.spec_from_file_location("main", "main.py")
main_module = importlib.util.module_from_spec(spec)

# Initialize FastAPI app
app = FastAPI(
    title="Tennis Warehouse API",
    description="Public API for Tennis Warehouse product search and information",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for public access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Tennis Warehouse API
tw_api = TennisWarehouseAPI()

@app.get("/")
async def root():
    """API Information"""
    return {
        "name": "Tennis Warehouse API",
        "version": "1.0.0",
        "description": "Search tennis products from Tennis Warehouse",
        "endpoints": {
            "search": "/search - General product search",
            "smart-search": "/smart-search - Intelligent search with filtering options",
            "bags": "/bags - Tennis bag search",
            "racquets": "/racquets - Tennis racquet search", 
            "shoes": "/shoes - Tennis shoe search",
            "deals": "/deals - Current deals and discounts",
            "availability": "/availability - Check product availability",
            "categories": "/categories - Get product categories"
        },
        "docs": "/docs"
    }

@app.get("/search")
async def search_products(
    query: str = Query(..., description="Search term (e.g., 'wilson racquet', 'nike shoes')"),
    category: Optional[str] = Query(None, description="Product category filter"),
    max_results: int = Query(10, ge=1, le=20, description="Maximum number of results")
) -> List[Dict[str, Any]]:
    """Search Tennis Warehouse products with intelligent filtering"""
    
    if not query or len(query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    try:
        # Use existing search logic
        raw_response = tw_api.search_products(
            search_term=query,
            limit=max_results
        )
        
        products = extract_products(raw_response)
        
        if products and "error" in products[0]:
            raise HTTPException(status_code=500, detail=products[0]["error"])
        
        return products
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/smart-search")
async def smart_search(
    query: str = Query(..., description="Search term"),
    max_results: int = Query(20, ge=1, le=50, description="Maximum number of results to analyze")
) -> Dict[str, Any]:
    """Intelligent search with conversational filtering options"""
    
    if not query or len(query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    try:
        # Call website search
        raw_response = tw_api.search_products(
            search_term=query,
            limit=max_results
        )
        
        # Extract insights and products
        insights = extract_search_insights(raw_response)
        products = extract_products(raw_response)
        
        # Generate suggestions (simplified version)
        total_products = insights.get("total_products", 0)
        brands = insights.get("brands", [])
        types = insights.get("types", [])
        
        suggestions = []
        if total_products > 0:
            suggestions.append(f"Found {total_products} results for '{query}'!")
            
            if len(brands) > 0:
                brand_names = [b.get("display_name", b.get("name", "")) for b in brands[:5]]
                suggestions.append(f"Available brands: {', '.join(brand_names)}")
                
            if len(types) > 0:
                type_names = [t.get("display_name", t.get("name", "")) for t in types[:5]]
                suggestions.append(f"Available types: {', '.join(type_names)}")
        
        # Sample products
        sample_products = []
        if products and not any("error" in p for p in products):
            sample_products = products[:3]
        
        return {
            "query": query,
            "total_results": total_products,
            "suggestions": suggestions,
            "insights": insights,
            "sample_products": sample_products,
            "all_products": products
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Smart search failed: {str(e)}")

@app.get("/bags")
async def search_bags(
    style: Optional[str] = Query(None, description="Bag style (e.g., 'backpack', 'tote')"),
    brand: Optional[str] = Query(None, description="Brand name"),
    max_results: int = Query(10, ge=1, le=20, description="Maximum results")
) -> List[Dict[str, Any]]:
    """Search for tennis bags"""
    
    try:
        search_term = "tennis bag"
        if brand:
            search_term = f"{brand} tennis bag"
        if style:
            search_term = f"{style} tennis bag"
            
        raw_response = tw_api.search_products(
            search_term=search_term,
            limit=max_results
        )
        
        products = extract_products(raw_response)
        
        if products and "error" in products[0]:
            raise HTTPException(status_code=500, detail=products[0]["error"])
        
        return products
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bag search failed: {str(e)}")

@app.get("/racquets")
async def search_racquets(
    brand: Optional[str] = Query(None, description="Racquet brand"),
    weight_range: Optional[str] = Query(None, description="Weight preference"),
    max_results: int = Query(10, ge=1, le=20, description="Maximum results")
) -> List[Dict[str, Any]]:
    """Search for tennis racquets"""
    
    try:
        search_term = "tennis racquet"
        if brand:
            search_term = f"{brand} racquet"
            
        raw_response = tw_api.search_products(
            search_term=search_term,
            limit=max_results
        )
        
        products = extract_products(raw_response)
        
        if products and "error" in products[0]:
            raise HTTPException(status_code=500, detail=products[0]["error"])
        
        return products
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Racquet search failed: {str(e)}")

@app.get("/shoes")
async def search_shoes(
    gender: Optional[str] = Query(None, description="Gender (men/women)"),
    brand: Optional[str] = Query(None, description="Shoe brand"),
    court_type: Optional[str] = Query(None, description="Court type"),
    max_results: int = Query(10, ge=1, le=20, description="Maximum results")
) -> List[Dict[str, Any]]:
    """Search for tennis shoes"""
    
    try:
        search_term = "tennis shoes"
        if gender:
            search_term = f"{gender} tennis shoes"
        if brand:
            search_term = f"{brand} tennis shoes"
            
        raw_response = tw_api.search_products(
            search_term=search_term,
            limit=max_results
        )
        
        products = extract_products(raw_response)
        
        if products and "error" in products[0]:
            raise HTTPException(status_code=500, detail=products[0]["error"])
        
        return products
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shoe search failed: {str(e)}")

@app.get("/deals")
async def get_deals(
    category: Optional[str] = Query(None, description="Product category"),
    max_results: int = Query(10, ge=1, le=20, description="Maximum results")
) -> List[Dict[str, Any]]:
    """Find current deals and discounted products"""
    
    try:
        deal_terms = ["sale", "clearance", "discount", "special"]
        all_deals = []
        
        for term in deal_terms:
            raw_response = tw_api.search_products(
                search_term=term,
                limit=max_results
            )
            
            products = extract_products(raw_response)
            if products and "error" not in products[0]:
                all_deals.extend(products)
            
            if len(all_deals) >= max_results:
                break
        
        # Remove duplicates
        seen_names = set()
        unique_deals = []
        for deal in all_deals:
            name = deal.get("name", "")
            if name not in seen_names:
                seen_names.add(name)
                unique_deals.append(deal)
                
            if len(unique_deals) >= max_results:
                break
        
        return unique_deals
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deals search failed: {str(e)}")

@app.get("/availability")
async def check_availability(
    product_name: str = Query(..., description="Product name to check")
) -> Dict[str, Any]:
    """Check if a specific product is available"""
    
    if not product_name or len(product_name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Product name must be at least 2 characters")
    
    try:
        raw_response = tw_api.search_products(
            search_term=product_name,
            limit=5
        )
        
        products = extract_products(raw_response)
        
        if not products or "error" in products[0]:
            return {
                "found": False,
                "message": "Product not found",
                "error": products[0].get("error") if products else None
            }
        
        # Return the best match
        best_match = products[0]
        
        return {
            "found": True,
            "name": best_match.get("name"),
            "brand": best_match.get("brand"),
            "price": best_match.get("price"),
            "in_stock": best_match.get("in_stock", False),
            "availability": best_match.get("availability", "Unknown"),
            "product_url": best_match.get("product_url")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Availability check failed: {str(e)}")

@app.get("/categories")
async def get_categories() -> List[Dict[str, str]]:
    """Get available product categories"""
    
    categories = [
        {"name": "Tennis Racquets", "code": "RACQUETS"},
        {"name": "Tennis Shoes", "code": "SHOES"},
        {"name": "Tennis Bags", "code": "BAGS"},
        {"name": "Tennis Balls", "code": "BALLS"},
        {"name": "Tennis Strings", "code": "STRINGS"},
        {"name": "Men's Apparel", "code": "MENS_APPAREL"},
        {"name": "Women's Apparel", "code": "WOMENS_APPAREL"},
        {"name": "Junior Tennis", "code": "JUNIOR"}
    ]
    
    return categories

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors gracefully"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )