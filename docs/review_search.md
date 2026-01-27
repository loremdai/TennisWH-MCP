# 评测搜索功能说明

## 问题

用户在搜索产品评测时，LLM 经常无法找到正确的评测页面 URL，因为：

1. 评测页面 URL 命名规则不一致
2. LLM 只能猜测 URL，经常猜错
3. 例如："Babolat Pure Strike 100 16x20" 的评测 URL 是 `PS1620review.html`，而不是 `BPS1001620review.html`

## 解决方案

添加了新的 `search_review` 工具，可以搜索并找到正确的评测页面 URL。

## 使用方法

### 正确的工作流程

**之前**（经常失败）:
```
用户: "Babolat Pure Strike 100 16x20 的评测怎么样？"
→ LLM 猜测 URL: BPS1001620review.html
→ get_review(猜测的URL)
→ 404 错误
```

**现在**（推荐）:
```
用户: "Babolat Pure Strike 100 16x20 的评测怎么样？"
→ search_review("Pure Strike 100 16x20", "Babolat")
→ 返回实际的评测 URL 列表
→ get_review(正确的URL)
→ 成功获取评测数据
```

### 工具说明

#### search_review

搜索产品评测页面，返回实际存在的评测 URL。

**参数**:
- `product_name` (必需): 产品名称，如 "Pure Strike 100"
- `brand` (可选): 品牌名称，如 "Babolat"，帮助缩小搜索范围

**返回**:
```json
{
  "review_pages": [
    {
      "url": "https://www.tennis-warehouse.com/learning_center/racquet_reviews/PS1620review.html",
      "title": "Review"
    }
  ],
  "count": 10,
  "search_query": "Babolat Pure Strike 100 16x20 review",
  "suggestion": "Use the first URL with get_product_review tool to fetch the review data"
}
```

#### get_review

从评测页面提取详细的评测数据（性能评分、实验室数据、测试员反馈）。

**参数**:
- `review_url` (必需): 评测页面的完整 URL

## 测试结果

测试用例：Babolat Pure Strike 100 16x20

```bash
$ uv run python tests/test_search_review.py
```

**结果**:
- 找到 10 个评测页面
- 包括正确的 `PS1620review.html`（第10个）
- 所有 URL 都是实际存在的评测页面

## 技术实现

1. 使用搜索 API 查找评测相关内容
2. 解析 HTML 提取所有评测页面链接
3. 过滤出 `learning_center/racquet_reviews/` 目录下的链接
4. 返回完整的 URL 列表

## 更新内容

- 新增 `src/tools/product_tools.py::search_review_page()` 函数
- 在 MCP 服务器注册 `search_review` 工具
- 工具总数: 11 → 12
- 新增测试脚本: `tests/test_search_review.py`
