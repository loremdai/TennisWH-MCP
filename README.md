# Tennis Warehouse MCP Server

🎾 **Secure MCP wrapper for Tennis Warehouse's internal APIs**

This MCP server provides LLMs with safe, business-friendly access to Tennis Warehouse product data through their internal Solr search API.

## 🛡️ Security Benefits

- **API Gateway**: Protects internal Tennis Warehouse APIs from direct LLM access
- **Data Filtering**: Only exposes customer-relevant product information
- **Input Validation**: Sanitizes and validates all search parameters
- **Rate Limiting**: Controls API usage and prevents abuse
- **Error Handling**: Clean error messages instead of internal stack traces

## 🔧 Installation

1. **Create virtual environment:**
   ```bash
   cd tennis-warehouse-mcp
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install "mcp[cli]" httpx requests pydantic
   ```

3. **Configure Claude Desktop:**
   Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "tennis-warehouse": {
         "command": "/path/to/tennis-warehouse-mcp/.venv/bin/python3",
         "args": ["/path/to/tennis-warehouse-mcp/main.py"],
         "env": {
           "TW_API_TIMEOUT": "10",
           "TW_MAX_RESULTS": "20"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop** to load the new MCP server

## 🎯 Available Tools

### `search_tennis_products(query, category, max_results)`
Search Tennis Warehouse products with intelligent filtering.

**Example:**
```
🤖 "Find Wilson racquets under $200"
```

### `search_tennis_bags(style, brand, max_results)`  
Search specifically for tennis bags with advanced filtering.

**Example:**
```
🤖 "Show me Head backpack tennis bags"
```

### `search_tennis_racquets(brand, weight_range, max_results)`
Search for tennis racquets with brand and weight filtering.

**Example:**
```
🤖 "Find Babolat lightweight racquets"
```

### `search_tennis_shoes(gender, brand, court_type, max_results)`
Search for tennis shoes with gender, brand, and court type filtering.

**Example:**
```
🤖 "Find Nike men's hard court tennis shoes"
```

### `get_product_categories()`
Get all available product categories with product counts.

### `check_product_availability(product_name)`
Check if a specific product is in stock.

**Example:**
```
🤖 "Is the Wilson Pro Staff 97 available?"
```

### `get_tennis_deals(category, max_results)`
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
| ✅ Clean error messages | ❌ Database stack traces |

## 🔍 Example Tennis Warehouse API Mapping

**Internal Solr API:**
```
https://static.tennis-warehouse.com/solr/solr_query.php?search=products&facet_set%5B%5D=facet_set_BAGFILTER&filter_cat=SHOULDBAGS
```

**MCP Tool:**
```python
search_tennis_bags(style="backpack", brand="Wilson")
```

**LLM Result:**
```json
[
  {
    "name": "Wilson Pro Staff Backpack",
    "brand": "Wilson", 
    "price": "$89.99",
    "availability": "Available",
    "product_url": "https://www.tennis-warehouse.com/..."
  }
]
```

## ⚙️ Configuration

Environment variables can be set in Claude Desktop config:

- `TW_API_TIMEOUT`: API timeout in seconds (default: 10)
- `TW_MAX_RESULTS`: Maximum results per query (default: 20)

## 🧪 Testing

Test the API client:
```bash
source .venv/bin/activate
python3 -c "
from tennis_warehouse_api import TennisWarehouseAPI
api = TennisWarehouseAPI()
print('✅ Tennis Warehouse API client working!')
"
```

## 🏗️ Architecture

```
🤖 LLM (Claude)
    ↓ (MCP Protocol)
🛡️ Tennis Warehouse MCP Server
    ↓ (HTTP/JSON)
🔒 Tennis Warehouse Internal Solr API
    ↓
📊 Product Database
```

## 🎾 LLM Usage Examples

Once configured, LLMs can use natural language to search Tennis Warehouse:

- *"Find me Wilson tennis bags under $100"*
- *"What Nike tennis shoes are available for women?"*
- *"Show me current deals on Babolat racquets"*
- *"Is the Head Speed MP racquet in stock?"*
- *"Find lightweight tennis racquets for beginners"*

The MCP server handles all the complexity of mapping these requests to the internal Solr API while keeping sensitive data protected! 🎾✨