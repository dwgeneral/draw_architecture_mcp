# Draw Architecture MCP Server

一个专业的架构图绘制 MCP 服务器，集成智谱AI大模型，能够根据文本描述自动生成 draw.io 格式的系统架构图。

## 功能特性

- 🤖 **AI 驱动生成**：集成智谱AI免费大模型，智能理解架构需求
- 🎨 **智能架构图生成**：根据文本描述自动生成专业的系统架构图
- 📊 **Draw.io 兼容**：生成标准的 .drawio 格式文件，可直接导入 draw.io 编辑
- 🏗️ **多种架构模式**：支持微服务、分层架构、事件驱动等多种架构模式
- 🎯 **专业提示词**：内置专业的架构设计提示词模板
- 🔧 **MCP 协议**：基于 Model Context Protocol，可与支持 MCP 的 AI 助手集成
- 💰 **免费使用**：使用智谱AI的免费额度，无需付费即可体验

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

### 3. 配置智谱AI API Key

#### 获取API Key
1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册账号并登录
3. 在控制台获取API Key（新用户有免费额度）

#### 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的API Key
echo "ZHIPUAI_API_KEY=your_actual_api_key_here" > .env
```

### 4. 配置 MCP 客户端

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
        "PYTHONPATH": "/path/to/draw_architecture_mcp",
        "ZHIPUAI_API_KEY": "your_api_key_here"
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
      "args": ["/path/to/draw_architecture_mcp/mcp_server.py"],
      "env": {
        "ZHIPUAI_API_KEY": "your_api_key_here"
      }
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

### 基本用法

在支持 MCP 的 AI 客户端中，你可以这样使用：

```
请帮我绘制一个电商系统的架构图，包括：
- 前端：Web应用、移动App
- 后端：用户服务、商品服务、订单服务
- 数据库：MySQL、Redis
- 消息队列：Kafka
```

### 高级用法

```
绘制一个微服务架构的在线教育平台：

前端层：
- React Web应用
- Flutter移动应用
- 管理后台

网关层：
- API网关（Kong）
- 负载均衡（Nginx）

业务服务层：
- 用户认证服务
- 课程管理服务
- 视频播放服务
- 支付服务
- 消息通知服务

数据层：
- MySQL（用户数据、课程数据）
- MongoDB（视频元数据）
- Redis（缓存、会话）
- Elasticsearch（搜索）

基础设施：
- Docker容器化
- Kubernetes编排
- 监控（Prometheus + Grafana）
- 日志（ELK Stack）
```

## 技术架构

### AI 模型集成
- **智谱AI GLM-4-Flash**：免费的大语言模型，专门优化架构图生成
- **专业提示词模板**：内置完整的架构设计指导模板
- **智能回退机制**：AI调用失败时自动回退到规则引擎

### 生成流程
1. **需求分析**：解析用户的架构描述
2. **模板整合**：将用户需求与专业提示词模板结合
3. **AI生成**：调用智谱AI生成完整的draw.io XML代码
4. **格式验证**：确保生成的XML符合draw.io标准
5. **文件保存**：保存为.drawio格式文件

### 支持的架构模式
- 分层架构（Layered Architecture）
- 微服务架构（Microservices）
- 事件驱动架构（Event-Driven）
- 六边形架构（Hexagonal）
- CQRS架构
- 服务网格（Service Mesh）

AI 助手会使用 `generate_architecture_diagram` 工具生成对应的 draw.io 文件。

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

### v1.0.0 (2025-06-14)
- 初始版本发布
- 支持基础架构图生成
- 提供文件验证功能
- 完整的 MCP 协议实现

## 联系方式

- 项目主页: [GitHub Repository](https://github.com/dwgeneral/draw_architecture_mcp)
- 问题反馈: [Issues](https://github.com/dwgeneral/draw_architecture_mcp/issues)
- 功能建议: [Discussions](https://github.com/dwgeneral/draw_architecture_mcp/discussions)
