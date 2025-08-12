# Tennis Warehouse Public API

🎾 **Public HTTP API for Tennis Warehouse product search** - Compatible with ChatGPT, Claude, Gemini, and all AI platforms.

## 🚀 Quick Start

### Live API
```
Base URL: https://your-app.railway.app
```

### Test the API
```bash
curl "https://your-app.railway.app/search?query=wilson%20racquet&max_results=5"
```

## 📋 Available Endpoints

### 🔍 **General Search**
```http
GET /search?query={search_term}&category={category}&max_results={limit}
```

**Parameters:**
- `query` (required): Search term (e.g., "wilson racquet", "nike shoes")
- `category` (optional): Product category filter  
- `max_results` (optional): 1-20, default 10

**Example:**
```bash
curl "https://your-app.railway.app/search?query=tennis%20balls&max_results=5"
```

### 🧠 **Smart Search** 
```http
GET /smart-search?query={search_term}&max_results={limit}
```

Returns intelligent filtering suggestions and insights.

**Example:**
```bash
curl "https://your-app.railway.app/smart-search?query=racquet&max_results=20"
```

### 👜 **Tennis Bags**
```http
GET /bags?style={style}&brand={brand}&max_results={limit}
```

**Example:**
```bash
curl "https://your-app.railway.app/bags?brand=wilson&style=backpack"
```

### 🎾 **Tennis Racquets**
```http
GET /racquets?brand={brand}&weight_range={weight}&max_results={limit}
```

**Example:**
```bash
curl "https://your-app.railway.app/racquets?brand=babolat"
```

### 👟 **Tennis Shoes**
```http
GET /shoes?gender={gender}&brand={brand}&court_type={type}&max_results={limit}
```

**Example:**
```bash
curl "https://your-app.railway.app/shoes?gender=men&brand=nike"
```

### 💰 **Current Deals**
```http
GET /deals?category={category}&max_results={limit}
```

**Example:**
```bash
curl "https://your-app.railway.app/deals?max_results=10"
```

### 📦 **Check Availability**
```http
GET /availability?product_name={product_name}
```

**Example:**
```bash
curl "https://your-app.railway.app/availability?product_name=Wilson%20Pro%20Staff"
```

### 📂 **Product Categories**
```http
GET /categories
```

## 📖 API Documentation

Once deployed, visit:
- **Swagger UI**: `https://your-app.railway.app/docs`
- **ReDoc**: `https://your-app.railway.app/redoc`

## 🤖 AI Platform Integration

### **ChatGPT Custom GPT**
1. Create Custom GPT
2. Add Action with OpenAPI schema:
```yaml
openapi: 3.0.0
info:
  title: Tennis Warehouse API
  version: 1.0.0
servers:
  - url: https://your-app.railway.app
paths:
  /search:
    get:
      operationId: searchProducts
      summary: Search tennis products
      parameters:
        - name: query
          in: query
          required: true
          schema:
            type: string
            description: Search term for tennis products
        - name: max_results
          in: query
          schema:
            type: integer
            default: 10
            minimum: 1
            maximum: 20
      responses:
        '200':
          description: Product search results
```

### **Claude (Anthropic)**
For Claude API integration:
```python
import requests

def search_tennis_products(query: str, max_results: int = 10):
    """Search Tennis Warehouse for products"""
    response = requests.get(
        f"https://your-app.railway.app/search",
        params={"query": query, "max_results": max_results}
    )
    return response.json()
```

### **Gemini (Google)**
Use as external function:
```python
def search_tennis_function_declaration():
    return {
        "name": "search_tennis_products",
        "description": "Search Tennis Warehouse for tennis equipment",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Product search term"},
                "max_results": {"type": "integer", "description": "Number of results"}
            },
            "required": ["query"]
        }
    }
```

## 🔒 Rate Limiting & Security

### **Current Limits**
- Max 20 results per request
- 10 second timeout per request
- No authentication required (public)

### **Production Considerations**
For heavy usage, consider adding:
- API key authentication
- Request rate limiting
- Caching layer
- Error monitoring

## 📊 Response Format

### **Product Object**
```json
{
  "name": "Wilson Pro Staff 97 v14",
  "brand": "Wilson",
  "price": "$249.95",
  "code": "WR001234",
  "in_stock": true,
  "availability": "Available",
  "product_url": "https://www.tennis-warehouse.com/wilson-pro-staff-97-v14",
  "source_citation": "[Tennis Warehouse](https://www.tennis-warehouse.com/wilson-pro-staff-97-v14)"
}
```

### **Smart Search Response**
```json
{
  "query": "tennis racquet",
  "total_results": 45,
  "suggestions": [
    "Found 45 results for 'tennis racquet'!",
    "Available brands: Wilson, Babolat, Head, Prince",
    "Available types: Power, Control, Lightweight"
  ],
  "insights": {
    "brands": [...],
    "types": [...],
    "total_products": 45
  },
  "sample_products": [...],
  "all_products": [...]
}
```

## 🚢 Deployment Options

### **1. Railway (Recommended)**
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/tennis-warehouse-api)

```bash
# Clone and deploy
git clone <your-repo>
cd tennis-warehouse-mcp
railway up
```

### **2. Render**
1. Connect GitHub repo
2. Build Command: `pip install -r requirements-api.txt`
3. Start Command: `uvicorn api_server:app --host 0.0.0.0 --port $PORT`

### **3. Vercel**
```bash
npm i -g vercel
vercel --prod
```

### **4. Docker**
```bash
docker build -t tennis-warehouse-api .
docker run -p 8000:8000 tennis-warehouse-api
```

## 🧪 Testing

### **Local Development**
```bash
pip install -r requirements-api.txt
uvicorn api_server:app --reload
```

Visit: `http://localhost:8000/docs`

### **Test Script**
```python
import requests

base_url = "https://your-app.railway.app"

# Test search
response = requests.get(f"{base_url}/search", params={"query": "wilson", "max_results": 3})
print(response.json())

# Test smart search  
response = requests.get(f"{base_url}/smart-search", params={"query": "racquet"})
print(response.json())
```

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: `/docs` endpoint
- **Source**: Tennis Warehouse website data

## ⚖️ Legal Notice

This API provides access to publicly available Tennis Warehouse product information. All product data, pricing, and availability information is sourced from Tennis Warehouse's public website. This is an unofficial API and is not affiliated with Tennis Warehouse.

For purchasing products, users are directed to official Tennis Warehouse links provided in the API responses.