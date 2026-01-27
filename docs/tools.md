# 工具模块文档

工具模块包含 MCP 服务器注册的所有工具函数。

## 模块结构

```
src/tools/
├── __init__.py        # 模块导出
├── search_tools.py    # 搜索工具
├── product_tools.py   # 产品工具
└── helpers.py         # 辅助函数
```

## search_tools.py

搜索相关的工具函数。

### search_tennis_products

基础产品搜索。

```python
def search_tennis_products(
    tw_api: TennisWarehouseAPI,
    query: str,
    category: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]
```

### search_tennis_bags

球包专用搜索。

```python
def search_tennis_bags(
    tw_api: TennisWarehouseAPI,
    style: Optional[str] = None,
    brand: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]
```

支持的样式：
- `backpack` - 背包
- `tote` - 手提包
- `duffel` - 旅行包
- `6 pack` - 6 支装
- `12 pack` - 12 支装
- `wheeled` - 带轮

### search_tennis_racquets

球拍专用搜索。

```python
def search_tennis_racquets(
    tw_api: TennisWarehouseAPI,
    brand: Optional[str] = None,
    weight_range: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]
```

### search_tennis_shoes

球鞋专用搜索。

```python
def search_tennis_shoes(
    tw_api: TennisWarehouseAPI,
    gender: Optional[str] = None,
    brand: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]
```

### smart_search_tennis

智能搜索（带过滤建议）。

```python
def smart_search_tennis(
    tw_api: TennisWarehouseAPI,
    query: str,
    max_results: int = 20
) -> List[Dict[str, Any]]
```

### get_tennis_deals

查找优惠产品。

```python
def get_tennis_deals(
    tw_api: TennisWarehouseAPI,
    category: Optional[str] = None,
    max_results: int = 10
) -> List[Dict[str, Any]]
```

## product_tools.py

产品信息相关的工具函数。

### get_product_specs

获取产品详细规格。

```python
def get_product_specs(
    tw_api: TennisWarehouseAPI,
    product_url: str
) -> Dict[str, Any]
```

**返回**:
```python
{
    "product_url": "...",
    "specifications": {
        "Head Size": "98 sq. in.",
        "Weight": "11.3 oz",
        "Swingweight": "320",
        ...
    },
    "spec_count": 10
}
```

### get_product_review

获取产品评测数据。

```python
def get_product_review(
    tw_api: TennisWarehouseAPI,
    review_url: str
) -> Dict[str, Any]
```

**返回**:
```python
{
    "url": "...",
    "scores": {
        "Power": 9.2,
        "Control": 7.7,
        "Maneuverability": 8.5,
        ...
    },
    "lab_data": {
        "Flex Rating": "65",
        "Swingweight": "320",
        ...
    },
    "feedback": {
        "positives": [...],
        "negatives": [...],
        "playtester_thoughts": [...]
    }
}
```

### get_product_categories

获取所有产品分类。

```python
def get_product_categories() -> list
```

### check_product_availability

检查产品库存。

```python
def check_product_availability(
    tw_api: TennisWarehouseAPI,
    product_name: str
) -> Dict[str, Any]
```

## helpers.py

辅助函数。

### generate_search_suggestions

生成搜索建议。

```python
def generate_search_suggestions(
    insights: Dict[str, Any],
    query: str,
    sample_products: List[Dict[str, Any]] = None
) -> str
```

### handle_search_option

处理用户选项。

```python
def handle_search_option(
    option: str,
    insights: Dict[str, Any],
    query: str
) -> Dict[str, Any]
```

## 使用示例

```python
from src.api import TennisWarehouseAPI
from src.tools import (
    search_tennis_products,
    get_product_specs,
    get_product_review
)

# 初始化 API
api = TennisWarehouseAPI()

# 搜索产品
products = search_tennis_products(api, "wilson blade", max_results=5)

# 获取规格
specs = get_product_specs(api, products[0]['product_url'])

# 获取评测
review = get_product_review(api, review_url)
```
