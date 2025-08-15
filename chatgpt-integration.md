# ChatGPT Integration Guide

🤖 **How to use Tennis Warehouse MCP with ChatGPT**

## 🚀 Quick Setup

### **Option 1: Use the REST API (Recommended)**

Your FastAPI server is running at: `http://localhost:8000`

**Available for ChatGPT:**
- ✅ Custom GPTs with Actions
- ✅ ChatGPT Plus/Pro
- ✅ API integrations
- ✅ Web development

### **Option 2: Deploy to Public URL**

For broader access, deploy to Railway/Render to get a public URL.

## 📋 **API Endpoints for ChatGPT**

### **🔍 General Search**
```http
GET /search?query={search_term}&max_results={limit}
```

### **🧠 Smart Search** 
```http
GET /smart-search?query={search_term}&max_results={limit}
```

### **👜 Tennis Bags**
```http
GET /bags?style={style}&brand={brand}&max_results={limit}
```

### **🎾 Tennis Racquets**
```http
GET /racquets?brand={brand}&max_results={limit}
```

### **👟 Tennis Shoes**
```http
GET /shoes?gender={gender}&brand={brand}&max_results={limit}
```

### **💰 Current Deals**
```http
GET /deals?max_results={limit}
```

### **📦 Check Availability**
```http
GET /availability?product_name={product_name}
```

### **📂 Categories**
```http
GET /categories
```

## 🤖 **ChatGPT Custom GPT Setup**

### **Step 1: Create Custom GPT**
1. Go to ChatGPT → "Explore GPTs" → "Create a GPT"
2. Name: "Tennis Warehouse Assistant"
3. Description: "Search tennis equipment from Tennis Warehouse"

### **Step 2: Configure Actions**
1. Click "Configure" → "Actions"
2. Click "Create new action"
3. Import the OpenAPI schema below:

```yaml
openapi: 3.0.0
info:
  title: Tennis Warehouse API
  description: Search tennis products from Tennis Warehouse
  version: 1.0.0
servers:
  - url: http://localhost:8000
    description: Local development server
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
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    name:
                      type: string
                    brand:
                      type: string
                    price:
                      type: string
                    availability:
                      type: string
                    product_url:
                      type: string
  /smart-search:
    get:
      operationId: smartSearch
      summary: Intelligent search with filtering options
      parameters:
        - name: query
          in: query
          required: true
          schema:
            type: string
        - name: max_results
          in: query
          schema:
            type: integer
            default: 20
            minimum: 1
            maximum: 50
      responses:
        '200':
          description: Smart search results with suggestions
  /racquets:
    get:
      operationId: searchRacquets
      summary: Search tennis racquets
      parameters:
        - name: brand
          in: query
          schema:
            type: string
            description: Racquet brand (e.g., Wilson, Babolat, Head)
        - name: max_results
          in: query
          schema:
            type: integer
            default: 10
            minimum: 1
            maximum: 20
      responses:
        '200':
          description: Tennis racquet search results
  /shoes:
    get:
      operationId: searchShoes
      summary: Search tennis shoes
      parameters:
        - name: gender
          in: query
          schema:
            type: string
            description: Gender (men/women)
        - name: brand
          in: query
          schema:
            type: string
            description: Shoe brand (e.g., Nike, Adidas)
        - name: max_results
          in: query
          schema:
            type: integer
            default: 10
      responses:
        '200':
          description: Tennis shoe search results
  /bags:
    get:
      operationId: searchBags
      summary: Search tennis bags
      parameters:
        - name: style
          in: query
          schema:
            type: string
            description: Bag style (e.g., backpack, tote)
        - name: brand
          in: query
          schema:
            type: string
        - name: max_results
          in: query
          schema:
            type: integer
            default: 10
      responses:
        '200':
          description: Tennis bag search results
  /deals:
    get:
      operationId: getDeals
      summary: Find current deals and discounts
      parameters:
        - name: max_results
          in: query
          schema:
            type: integer
            default: 10
      responses:
        '200':
          description: Current deals and discounted products
  /availability:
    get:
      operationId: checkAvailability
      summary: Check product availability
      parameters:
        - name: product_name
          in: query
          required: true
          schema:
            type: string
            description: Product name to check
      responses:
        '200':
          description: Product availability status
```

### **Step 3: Instructions for ChatGPT**
Add these instructions:

```
You are a Tennis Warehouse assistant that helps users find tennis equipment. You have access to Tennis Warehouse's product database through API actions.

When users ask about tennis products:
1. Use the appropriate search endpoint (search, racquets, shoes, bags, deals, availability)
2. Present results in a clear, organized format
3. Include prices, availability, and links to Tennis Warehouse
4. Suggest alternatives if specific products aren't found
5. Use smart-search for broad queries to provide filtering options

Always mention that products are from Tennis Warehouse and include purchase links.

Examples:
- "Find Wilson racquets under $200" → Use /racquets with brand=Wilson
- "Show me Nike tennis shoes for men" → Use /shoes with gender=men, brand=Nike
- "What tennis deals are available?" → Use /deals
- "Is the Wilson Pro Staff available?" → Use /availability

Be helpful and provide detailed product information!
```

## 🌐 **For Public Access (Deploy First)**

If you deploy to Railway/Render, update the server URL:

```yaml
servers:
  - url: https://your-app.railway.app
    description: Production server
```

## 🧪 **Test Examples**

Try these queries with your ChatGPT Custom GPT:

1. **"Find Wilson tennis racquets under $250"**
2. **"Show me Nike men's tennis shoes"**
3. **"What tennis deals are available right now?"**
4. **"Search for Babolat tennis bags"**
5. **"Is the Wilson Pro Staff 97 available?"**

## 🔧 **Current Limitations**

- **Local Only**: Currently runs on localhost:8000
- **Single User**: Only accessible from your machine
- **No Authentication**: Open API (fine for local use)

## 🚀 **Next Steps**

1. **Test locally** with the Custom GPT
2. **Deploy to Railway** for public access
3. **Share with others** using the public URL
4. **Monitor usage** and adjust rate limits if needed

Your Tennis Warehouse API is now ready for ChatGPT integration! 🎾
