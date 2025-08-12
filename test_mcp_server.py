#!/usr/bin/env python3
"""
Test script for Tennis Warehouse MCP Server
"""

import json
import sys
from tennis_warehouse_api import TennisWarehouseAPI, extract_products

def test_api_client():
    """Test the API client initialization and basic functionality"""
    print("🧪 Testing Tennis Warehouse API Client...")
    
    try:
        api = TennisWarehouseAPI()
        print("✅ API client initialized successfully")
        
        # Test a simple search
        print("\n🔍 Testing basic product search...")
        response = api.search_products(search_term="wilson", limit=3)
        
        if "error" in response:
            print(f"❌ API call failed: {response['error']}")
            return False
        
        products = extract_products(response)
        print(f"✅ Found {len(products)} products")
        
        if products:
            print("📦 Sample product:")
            sample = products[0]
            for key, value in sample.items():
                print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_bag_search():
    """Test bag-specific search functionality"""
    print("\n🎾 Testing bag search...")
    
    try:
        api = TennisWarehouseAPI()
        response = api.search_bags(limit=3)
        
        if "error" in response:
            print(f"❌ Bag search failed: {response['error']}")
            return False
        
        products = extract_products(response)
        print(f"✅ Found {len(products)} tennis bags")
        
        return True
        
    except Exception as e:
        print(f"❌ Bag search test failed: {e}")
        return False

def test_categories():
    """Test category listing functionality"""
    print("\n📂 Testing category retrieval...")
    
    try:
        api = TennisWarehouseAPI()
        response = api.get_categories()
        
        if "error" in response:
            print(f"❌ Category retrieval failed: {response['error']}")
            return False
        
        print("✅ Categories retrieved successfully")
        
        # Check if we got facet data
        facets = response.get("facet_counts", {}).get("facet_fields", {})
        print(f"📊 Found {len(facets)} facet categories")
        
        return True
        
    except Exception as e:
        print(f"❌ Category test failed: {e}")
        return False

def test_mcp_tools():
    """Test the MCP tool definitions (without running the server)"""
    print("\n🛠️  Testing MCP tool definitions...")
    
    try:
        import main
        
        # Check if tools are defined
        tool_names = [
            'search_tennis_products',
            'search_tennis_bags', 
            'search_tennis_racquets',
            'search_tennis_shoes',
            'get_product_categories',
            'check_product_availability',
            'get_tennis_deals'
        ]
        
        print("🔧 Checking MCP tools...")
        for tool_name in tool_names:
            if hasattr(main, tool_name):
                print(f"   ✅ {tool_name}")
            else:
                print(f"   ❌ {tool_name} - NOT FOUND")
                return False
        
        print("✅ All MCP tools defined correctly")
        return True
        
    except Exception as e:
        print(f"❌ MCP tool test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎾 Tennis Warehouse MCP Server Test Suite")
    print("=" * 50)
    
    tests = [
        test_api_client,
        test_bag_search,
        test_categories,
        test_mcp_tools
    ]
    
    results = []
    for test_func in tests:
        result = test_func()
        results.append(result)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("📊 Test Summary")
    print("=" * 50)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Tennis Warehouse MCP is ready to use.")
        print("\n📝 Next steps:")
        print("   1. Restart Claude Desktop")
        print("   2. Try asking: 'Find Wilson tennis racquets'")
        print("   3. Check that the 'tennis-warehouse' MCP shows up in Claude")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)