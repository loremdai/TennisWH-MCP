# Tennis Warehouse MCP Server - Enhanced

🎾 **Secure MCP wrapper for Tennis Warehouse with detailed product specifications**

This is an enhanced version of the Tennis Warehouse MCP server that adds the ability to extract detailed technical specifications from product pages, including Swingweight, Stiffness, Balance, and 15+ other parameters.

## ✨ New Features (Enhanced Version)

### 🔬 `get_product_specs(product_url)`
Extract detailed technical specifications from Tennis Warehouse product pages.

**What it extracts:**
- **Racquets**: Head Size, Weight, Balance, Swingweight, Stiffness, String Pattern, Beam Width, Power Level, Stroke Style, Swing Speed, Composition, and more
- **Shoes**: Weight, Cushioning, Outsole, Support features
- **Other products**: All available specifications from product detail pages

**Example usage:**
```
🤖 "What's the Swingweight of the Wilson Blade 98 16x19 v9?"
```

The LLM will:
1. Search for the product using `smart_search_tennis`
2. Extract the product URL
3. Call `get_product_specs` to get detailed specifications
4. Return the Swingweight value

**Supported page types:**
- ✅ Product detail pages (`descpage`)
- ✅ Review pages (`racquet_reviews`)
- ✅ Multiple HTML table structures

### 🎯 Enhanced Tool Descriptions

All tools now have improved descriptions that help LLMs understand:
- When to use `smart_search_tennis` (for basic product info)
- When to use `get_product_specs` (for detailed technical parameters)
- How to combine tools for complex queries

### 🐛 Bug Fixes

- Fixed `get_categories()` - now returns proper category list
- Fixed `search_bags()` - uses correct search parameters
- Improved error handling across all tools

---

## 🛡️ Security Benefits

- **API Gateway**: Protects internal Tennis Warehouse APIs from direct LLM access
- **Data Filtering**: Only exposes customer-relevant product information
- **Input Validation**: Sanitizes and validates all search parameters
- **Rate Limiting**: Controls API usage and prevents abuse
- **Error Handling**: Clean error messages instead of internal stack traces

## 🔧 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/loremdai/tennis-warehouse-mcp-enhanced.git
   cd tennis-warehouse-mcp-enhanced
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install "mcp[cli]" httpx requests pydantic beautifulsoup4
   ```

4. **Configure Claude Desktop or CherryStudio:**
   
   For **Claude Desktop**, add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "tennis-warehouse": {
         "command": "/path/to/tennis-warehouse-mcp-enhanced/.venv/bin/python3",
         "args": ["/path/to/tennis-warehouse-mcp-enhanced/main.py"],
         "env": {
           "TW_API_TIMEOUT": "10",
           "TW_MAX_RESULTS": "20"
         }
       }
     }
   }
   ```

   For **CherryStudio**, add the MCP server in settings with the same configuration.

5. **Restart your LLM client** to load the new MCP server

## 🎯 Available Tools

### Core Search Tools

#### `search_tennis_products(query, category, max_results)`
Search Tennis Warehouse products with intelligent filtering.

**Example:**
```
🤖 "Find Wilson racquets under $200"
```

#### `smart_search_tennis(query, max_results)`
Intelligent search with conversational filtering options.

**Note**: Returns basic info (name, price, URL) but NOT detailed specs.

**Example:**
```
🤖 "Search for Wilson Blade 98"
```

#### `search_tennis_bags(style, brand, max_results)`  
Search specifically for tennis bags with advanced filtering.

**Example:**
```
🤖 "Show me Head backpack tennis bags"
```

#### `search_tennis_racquets(brand, weight_range, max_results)`
Search for tennis racquets with brand and weight filtering.

**Example:**
```
🤖 "Find Babolat lightweight racquets"
```

#### `search_tennis_shoes(gender, brand, court_type, max_results)`
Search for tennis shoes with gender, brand, and court type filtering.

**Example:**
```
🤖 "Find Nike men's hard court tennis shoes"
```

### Product Information Tools

#### `get_product_specs(product_url)` ⭐ NEW
Extract detailed technical specifications from product pages.

**Example:**
```
🤖 "Get the full specs for https://www.tennis-warehouse.com/Wilson_Blade_98_16x19_v9/descpageRCWILSON-WB9816.html"
```

**Returns:**
```json
{
  "specifications": {
    "Head Size": "98 in² / 632.26 cm²",
    "Length": "27in / 68.58cm",
    "Strung Weight": "11.4oz / 323g",
    "Balance": "12.6in / 32cm / 7 pts HL",
    "Swingweight": "326",
    "Stiffness": "62",
    "String Pattern": "16 Mains / 19 Crosses",
    "Beam Width": "21mm / 21mm / 21mm",
    "Power Level": "Low-Medium",
    "Stroke Style": "Medium-Full",
    "Swing Speed": "Medium-Fast"
  }
}
```

#### `get_product_categories()`
Get all available product categories.

#### `check_product_availability(product_name)`
Check if a specific product is in stock.

**Example:**
```
🤖 "Is the Wilson Pro Staff 97 available?"
```

#### `get_tennis_deals(category, max_results)`
Find current deals and discounted tennis products.

**Example:**
```
🤖 "Show me current racquet deals"
```

## 📊 What LLMs Get vs. Internal API

| **LLM Gets (Safe)** | **Internal API Has (Protected)** |
|---|---|
| ✅ Product name, brand, price | ❌ Internal product IDs |
| ✅ Availability status | ❌ Exact inventory counts |
| ✅ Public product URLs | ❌ Supplier costs |
| ✅ Category information | ❌ Restock schedules |
| ✅ **Technical specifications** ⭐ | ❌ Database stack traces |
| ✅ Clean error messages | ❌ Internal system details |

## 🧪 Testing

### Test the API client:
```bash
source .venv/bin/activate
python3 -c "
from tennis_warehouse_api import TennisWarehouseAPI
api = TennisWarehouseAPI()
print('✅ Tennis Warehouse API client working!')
"
```

### Test product specs extraction:
```bash
python3 test_babolat.py
```

### Test with CherryStudio:

See [TEST_PROMPTS.md](TEST_PROMPTS.md) for comprehensive test scenarios.

**Quick test:**
```
请帮我查询 Wilson Blade 98 16x19 v9 的详细技术参数，包括 Swingweight 和 Stiffness。
```

## 🏗️ Architecture

```
🤖 LLM (Claude/CherryStudio)
    ↓ (MCP Protocol)
🛡️ Tennis Warehouse MCP Server
    ├─ Search Tools (API Gateway)
    │   ↓ (HTTP/JSON)
    │  🔒 Tennis Warehouse Solr API
    │
    └─ Specs Extraction ⭐ NEW
        ↓ (HTTP + BeautifulSoup)
       🌐 Product Detail Pages
           ↓
        📊 Product Database
```

## 🎾 LLM Usage Examples

### Basic Search
- *"Find me Wilson tennis bags under $100"*
- *"What Nike tennis shoes are available for women?"*
- *"Show me current deals on Babolat racquets"*
- *"Is the Head Speed MP racquet in stock?"*

### Technical Specifications ⭐ NEW
- *"What's the Swingweight of the Wilson Blade 98?"*
- *"Compare the Stiffness of Wilson Blade 98 and Head Radical MP"*
- *"Show me all the specs for the Babolat Pure Drive 2025"*
- *"I need a racquet with Swingweight around 320 and Stiffness under 65"*

The MCP server handles all the complexity of mapping these requests to the internal APIs and extracting detailed specifications while keeping sensitive data protected! 🎾✨

## 📚 Documentation

- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Detailed feature overview
- [TEST_PROMPTS.md](TEST_PROMPTS.md) - Test scenarios for CherryStudio
- [TOOL_IMPROVEMENTS.md](TOOL_IMPROVEMENTS.md) - Explanation of tool enhancements

## 🙏 Credits

This project is based on [tennis-warehouse-mcp](https://github.com/avimunk1/tennis-warehouse-mcp) by [avimunk1](https://github.com/avimunk1).

### Enhancements by loremdai

- ✨ Added `get_product_specs` tool for detailed technical parameters
- 🔬 Support for 15+ product specifications extraction
- 🎯 Improved tool descriptions for better LLM understanding
- 🐛 Fixed `get_categories` and `search_bags` methods
- 📝 Added comprehensive documentation and test files
- 🏗️ Enhanced HTML parsing with multiple pattern support

## 📄 License

Same license as the original project.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Note**: This MCP server is for educational and personal use. Always respect Tennis Warehouse's terms of service and rate limits.