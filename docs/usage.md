# 使用指南

## 安装

```bash
# 克隆仓库
git clone <repository-url>
cd tennis-warehouse-mcp

# 安装依赖
uv sync
```

## 启动服务器

### 方式 1: 使用启动脚本

```bash
./run_mcp.sh
```

### 方式 2: 直接运行

```bash
uv run python main.py
```

### 方式 3: 使用 src/main.py

```bash
uv run python src/main.py
```

### 在 CherryStudio 等客户端中配置

如果你要在 CherryStudio 等支持 MCP 的客户端中配置此服务器，请根据客户端界面使用以下设置：

- **名称**: Tennis Warehouse (或任意自定义名称)
- **类型**: 标准输入 / 输出 (stdio)
- **命令**: `uv` (或是系统上 `uv` 命令的绝对路径，可通过在终端执行 `which uv` 获取)
- **参数** (注意：每行填入一个参数):
  ```text
  --directory
  /绝对路径/tennis-warehouse-mcp
  run
  python
  /绝对路径/tennis-warehouse-mcp/main.py
  ```
- **环境变量** (可选，每行填入一个):
  ```text
  TW_API_TIMEOUT=10
  TW_MAX_RESULTS=20
  ```

## 可用工具

MCP 服务器提供 11 个工具函数：

### 1. search_products

搜索网球产品。

```python
search_products(
    query="wilson racquet",
    category="RACQUETS",  # 可选
    max_results=10
)
```

### 2. get_specs

获取产品详细规格。

```python
get_specs(
    product_url="https://www.tennis-warehouse.com/..."
)
```

### 3. get_review

获取产品评测数据。

```python
get_review(
    review_url="https://www.tennis-warehouse.com/learning_center/..."
)
```

### 4. search_bags

搜索网球包。

```python
search_bags(
    style="backpack",  # 可选
    brand="Wilson",    # 可选
    max_results=10
)
```

### 5. search_racquets

搜索网球拍。

```python
search_racquets(
    brand="Babolat",      # 可选
    weight_range="light", # 可选
    max_results=10
)
```

### 6. search_shoes

搜索网球鞋。

```python
search_shoes(
    gender="men",    # 可选
    brand="Nike",    # 可选
    max_results=10
)
```

### 7. get_categories

获取所有产品分类。

```python
get_categories()
```

### 8. check_availability

检查产品库存。

```python
check_availability(
    product_name="Wilson Blade 98"
)
```

### 9. get_deals

查找优惠产品。

```python
get_deals(
    category="RACQUETS",  # 可选
    max_results=10
)
```

### 10. smart_search

智能搜索（带过滤建议）。

```python
smart_search(
    query="tennis balls",
    max_results=20
)
```

### 11. handle_option

处理搜索选项。

```python
handle_option(
    option="1",
    insights={...},
    query="..."
)
```

## 工作流示例

### 查找产品规格

```python
# 1. 搜索产品
results = search_products(query="Wilson Blade 98")

# 2. 获取产品 URL
product_url = results[0]["product_url"]

# 3. 获取详细规格
specs = get_specs(product_url=product_url)
```

### 查找产品评测

```python
# 1. 搜索产品
results = smart_search(query="Dunlop FX 500")

# 2. 找到评测 URL（通常在产品页面）
review_url = "https://www.tennis-warehouse.com/learning_center/racquet_reviews/DF500review.html"

# 3. 获取评测数据
review = get_review(review_url=review_url)
```

## 配置

环境变量：

- `TW_API_TIMEOUT` - API 超时时间（默认: 10 秒）
- `TW_MAX_RESULTS` - 最大结果数（默认: 20）

## 测试

```bash
# 运行测试
uv run python tests/test_product_review.py
```
