# Tennis Warehouse MCP 文档

欢迎查看 Tennis Warehouse MCP 服务器文档。

## 文档导航

- [使用指南](usage.md) - 如何使用 MCP 服务器
- [API 模块](api.md) - API 客户端和解析器文档
- [工具模块](tools.md) - MCP 工具函数文档
- [开发指南](development.md) - 开发和贡献指南

## 快速开始

```bash
# 安装依赖
uv sync

# 启动 MCP 服务器
./run_mcp.sh

# 或直接运行
uv run python main.py
```

## 项目结构

```
tennis-warehouse-mcp/
├── src/           # 源代码
│   ├── api/       # API 客户端和解析器
│   ├── tools/     # MCP 工具函数
│   └── utils/     # 工具和常量
├── tests/         # 测试脚本
├── docs/          # 文档
└── main.py        # 入口文件
```

## 主要功能

- 产品搜索 - 搜索网球产品
- 规格提取 - 获取详细技术参数
- 评测数据 - 提取性能评分和反馈
- 专业搜索 - 球拍、球包、球鞋专用搜索
- 优惠查找 - 发现促销产品
