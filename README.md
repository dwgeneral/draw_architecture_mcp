# Draw.io 架构图 MCP 服务

一个专门用于生成 draw.io 架构图的 MCP (Model Context Protocol) 服务，让 AI 助手能够更方便地创建专业的系统架构图。

## 功能特性

- 🎨 **专业架构图生成**: 基于描述自动生成符合规范的 draw.io 架构图
- 📋 **提示词模板**: 提供专业的架构图绘制提示词
- ✅ **文件验证**: 验证 draw.io 文件格式的正确性
- 🔧 **XML 格式修复**: 自动处理 XML 转义和格式问题
- 🚀 **易于集成**: 标准 MCP 协议，支持多种 AI 客户端

## 安装配置

### 1. 环境要求

- Python 3.8+
- 支持 MCP 的 AI 客户端（如 Claude Desktop、Cline 等）

### 2. 安装依赖

```bash
# 克隆或下载项目
cd draw_architecture_mcp

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 MCP 客户端

#### Claude Desktop 配置

编辑 Claude Desktop 的配置文件：

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

添加以下配置：

```json
{
  "mcpServers": {
    "draw-architecture": {
      "command": "python3",
      "args": ["/path/to/draw_architecture_mcp/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/draw_architecture_mcp"
      }
    }
  }
}
```

#### Cline 配置

在 Cline 的设置中添加 MCP 服务器：

```json
{
  "mcpServers": {
    "draw-architecture": {
      "command": "python3",
      "args": ["/path/to/draw_architecture_mcp/mcp_server.py"]
    }
  }
}
```

### 4. 验证安装

重启 AI 客户端，在对话中询问是否可以使用架构图生成功能。如果配置正确，AI 助手应该能够访问以下工具：

- `generate_architecture_diagram`: 生成架构图
- `get_architecture_prompt`: 获取提示词模板
- `validate_drawio_file`: 验证文件格式

## 使用方法

### 1. 生成架构图

```
请帮我生成一个电商系统的架构图，包括：
- 前端：Web端、移动端、小程序
- 后端：用户服务、商品服务、订单服务、支付服务
- 数据库：MySQL、Redis、Elasticsearch
- 中间件：消息队列、API网关
```

AI 助手会使用 `generate_architecture_diagram` 工具生成对应的 draw.io 文件。

### 2. 获取专业提示词

```
请提供 draw.io 架构图绘制的专业提示词模板
```

AI 助手会使用 `get_architecture_prompt` 工具返回完整的提示词模板。

### 3. 验证文件格式

```
请验证这个 draw.io 文件的格式是否正确：/path/to/diagram.drawio
```

AI 助手会使用 `validate_drawio_file` 工具检查文件格式。

## API 参考

### 工具列表

#### `generate_architecture_diagram`

生成 draw.io 格式的架构图。

**参数**:
- `description` (string, 必需): 架构描述
- `diagram_name` (string, 可选): 图表名称，默认为"系统架构图"
- `output_file` (string, 可选): 输出文件路径

**示例**:
```json
{
  "description": "微服务架构，包含用户服务、订单服务、支付服务",
  "diagram_name": "电商系统架构",
  "output_file": "./ecommerce_architecture.drawio"
}
```

#### `get_architecture_prompt`

获取专业的架构图绘制提示词模板。

**参数**: 无

#### `validate_drawio_file`

验证 draw.io 文件格式。

**参数**:
- `file_path` (string, 必需): 要验证的文件路径

### 资源列表

#### `prompt://draw-architecture`

提供完整的 draw.io 架构图绘制提示词模板。

## 项目结构

```
draw_architecture_mcp/
├── mcp_server.py              # MCP 服务器主文件
├── draw_architecture_prompt.md # 提示词模板
├── requirements.txt           # Python 依赖
├── mcp_config.json           # MCP 配置示例
├── README.md                 # 项目文档
└── examples/                 # 示例文件
    ├── sample_architecture.drawio
    └── usage_examples.md
```

## 开发指南

### 本地开发

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行测试
pytest tests/

# 代码格式化
black mcp_server.py

# 类型检查
mypy mcp_server.py
```

### 扩展功能

1. **添加新的图表类型**: 在 `generate_drawio_xml` 函数中添加新的模板
2. **增强验证功能**: 在 `validate_drawio_file` 工具中添加更多检查项
3. **支持更多格式**: 添加导出为 PNG、SVG 等格式的功能

## 常见问题

### Q: 生成的文件无法在 draw.io 中打开？

A: 使用 `validate_drawio_file` 工具检查文件格式，常见问题包括：
- 缺少 XML 声明
- HTML 标签未正确转义
- XML 结构不完整

### Q: 如何自定义架构图样式？

A: 修改 `mcp_server.py` 中的 `generate_drawio_xml` 函数，调整颜色、字体、布局等样式参数。

### Q: 支持哪些 AI 客户端？

A: 支持所有实现 MCP 协议的客户端，包括：
- Claude Desktop
- Cline (VS Code 扩展)
- 其他支持 MCP 的 AI 工具

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 更新日志

### v1.0.0 (2024-01-XX)
- 初始版本发布
- 支持基础架构图生成
- 提供文件验证功能
- 完整的 MCP 协议实现

## 联系方式

- 项目主页: [GitHub Repository](https://github.com/your-repo/draw-architecture-mcp)
- 问题反馈: [Issues](https://github.com/your-repo/draw-architecture-mcp/issues)
- 功能建议: [Discussions](https://github.com/your-repo/draw-architecture-mcp/discussions)