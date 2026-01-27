# API 模块文档

API 模块负责与 Tennis Warehouse 网站交互，提取产品数据。

## 模块结构

```
src/api/
├── __init__.py    # 模块导出
├── client.py      # API 客户端
└── parsers.py     # HTML 解析器
```

## client.py

### TennisWarehouseAPI

主要的 API 客户端类。

#### 初始化

```python
from src.api import TennisWarehouseAPI

api = TennisWarehouseAPI()
```

#### 方法

##### search_products

搜索产品。

```python
def search_products(
    search_term: str = None,
    category: str = None,
    limit: int = 20
) -> Dict[str, Any]
```

**参数**:
- `search_term` - 搜索关键词
- `category` - 产品分类（可选）
- `limit` - 结果数量限制

**返回**: 包含 HTML 内容的字典

##### get_product_specs

获取产品规格。

```python
def get_product_specs(product_url: str) -> Dict[str, Any]
```

**参数**:
- `product_url` - 产品页面 URL

**返回**: 包含规格数据的字典

##### get_product_review

获取产品评测。

```python
def get_product_review(review_url: str) -> Dict[str, Any]
```

**参数**:
- `review_url` - 评测页面 URL

**返回**: 包含评测数据的字典，包括：
- `scores` - 性能评分
- `lab_data` - 实验室数据
- `feedback` - 反馈信息

#### 私有方法

- `_extract_specs_from_page(soup)` - 从页面提取规格
- `_extract_breakdown_scores(soup)` - 提取性能评分
- `_extract_lab_data(soup)` - 提取实验室数据
- `_extract_positives_negatives(soup)` - 提取优缺点
- `_extract_playtester_thoughts(soup)` - 提取测试员反馈

## parsers.py

HTML 解析工具函数。

### extract_products

从搜索结果提取产品列表。

```python
def extract_products(website_response: Dict[str, Any]) -> List[Dict[str, Any]]
```

**返回**: 产品列表，每个产品包含：
- `name` - 产品名称
- `brand` - 品牌
- `price` - 价格
- `availability` - 库存状态
- `product_url` - 产品链接

### extract_search_insights

提取搜索洞察（品牌、类型等）。

```python
def extract_search_insights(website_response: Dict[str, Any]) -> Dict[str, Any]
```

**返回**: 包含品牌、类型、产品数量等信息

### extract_categories

提取产品分类。

```python
def extract_categories(solr_response: Dict[str, Any]) -> List[Dict[str, Any]]
```

### extract_price_ranges

提取价格范围。

```python
def extract_price_ranges(solr_response: Dict[str, Any]) -> List[Dict[str, Any]]
```

## 使用示例

```python
from src.api import TennisWarehouseAPI, extract_products

# 初始化客户端
api = TennisWarehouseAPI()

# 搜索产品
response = api.search_products(search_term="wilson racquet", limit=10)

# 解析产品
products = extract_products(response)

for product in products:
    print(f"{product['name']} - {product['price']}")

# 获取规格
specs = api.get_product_specs(products[0]['product_url'])
print(specs['specs'])

# 获取评测
review = api.get_product_review(review_url)
print(f"Power: {review['scores']['Power']}")
```
