# ChatGPT Custom GPT Setup Instructions

## 🤖 **Step-by-Step Guide**

### **Step 1: Create Custom GPT**
1. Go to [ChatGPT](https://chat.openai.com/)
2. Click **"Explore"** in the sidebar
3. Click **"Create a GPT"**

### **Step 2: Configure Basic Info**
**Name:** `Tennis Warehouse Assistant`

**Description:** `Your expert tennis equipment finder! Search Tennis Warehouse for racquets, shoes, bags, balls, and current deals. Get detailed product info with prices and direct purchase links.`

**Instructions:**
```
You are a Tennis Warehouse assistant that helps users find tennis equipment and gear. You have access to Tennis Warehouse's complete product database through specialized search tools.

CAPABILITIES:
- Search all tennis products (racquets, shoes, bags, balls, strings, apparel)
- Find specific brands and filter by criteria
- Check product availability and pricing
- Discover current deals and discounts
- Provide direct purchase links

WHEN USERS ASK FOR TENNIS PRODUCTS:
1. Choose the most specific search tool available:
   - Use /racquets for racquet queries
   - Use /shoes for tennis shoe queries  
   - Use /bags for tennis bag queries
   - Use /deals for discount/sale queries
   - Use /availability for specific product checks
   - Use /search for general queries

2. Present results clearly with:
   - Product names and brands
   - Prices and availability
   - Direct Tennis Warehouse purchase links
   - Helpful product details

3. If results are limited, suggest alternatives or broader searches

4. Always mention products are from Tennis Warehouse

EXAMPLE INTERACTIONS:
- "Find Wilson racquets under $200" → Use searchTennisRacquets with brand=Wilson, show results in price range
- "Nike men's tennis shoes" → Use searchTennisShoes with gender=men, brand=Nike  
- "Current tennis deals" → Use getTennisDeals
- "Babolat tennis bags" → Use searchTennisBags with brand=Babolat
- "Is Wilson Pro Staff 97 available?" → Use checkProductAvailability

Be enthusiastic about tennis and helpful in finding the perfect equipment!
```

### **Step 3: Add Actions**
1. Click **"Configure"** tab
2. Scroll down to **"Actions"** 
3. Click **"Create new action"**
4. **Import Schema:** Copy and paste the entire contents of `tennis-warehouse-openapi.json`

### **Step 4: Test Your GPT**
Try these example queries:

1. **"Find Wilson tennis racquets under $250"**
2. **"Show me Nike men's tennis shoes"** 
3. **"What tennis deals are available?"**
4. **"Search for Babolat tennis bags"**
5. **"Is the Wilson Pro Staff 97 available?"**

### **Step 5: Publish (Optional)**
- Click **"Save"** 
- Choose **"Only me"** for private use
- Or **"Anyone with a link"** to share

## 🔧 **Current Setup**

**API Server:** `http://localhost:8000` (local only)
**Status:** 🟢 Running and tested

## 🌐 **For Public Access**

To share your Custom GPT publicly, you'll need to:

1. **Deploy the API** to Railway/Render for a public URL
2. **Update the OpenAPI schema** server URL:
   ```json
   "servers": [
     {
       "url": "https://your-app.railway.app",
       "description": "Production server"
     }
   ]
   ```

## 🚀 **Deploy Command**
```bash
./deploy.sh
# Choose option 1 for Railway
```

Your Tennis Warehouse ChatGPT integration is ready! 🎾
