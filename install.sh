#!/bin/bash

# Draw.io Architecture MCP Server 安装脚本
# 支持 macOS 和 Linux

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查系统
check_system() {
    print_info "检查系统环境..."
    
    # 检查操作系统
    if [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_info "检测到 macOS 系统"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_info "检测到 Linux 系统"
    else
        print_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
    
    # 检查 Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_info "Python 版本: $PYTHON_VERSION"
        
        # 检查 Python 版本是否 >= 3.8
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python 版本满足要求 (>= 3.8)"
        else
            print_error "Python 版本过低，需要 3.8 或更高版本"
            exit 1
        fi
    else
        print_error "未找到 Python3，请先安装 Python 3.8+"
        exit 1
    fi
    
    # 检查 pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 已安装"
    else
        print_error "未找到 pip3，请先安装 pip"
        exit 1
    fi
}

# 安装依赖
install_dependencies() {
    print_info "安装 Python 依赖包..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_success "依赖包安装完成"
    else
        print_error "未找到 requirements.txt 文件"
        exit 1
    fi
}

# 测试安装
test_installation() {
    print_info "测试 MCP 服务器功能..."
    
    if [ -f "test_mcp_server.py" ]; then
        if python3 test_mcp_server.py; then
            print_success "MCP 服务器测试通过"
        else
            print_warning "MCP 服务器测试失败，但安装可能仍然有效"
        fi
    else
        print_warning "未找到测试脚本，跳过测试"
    fi
}

# 配置 Trae IDE
configure_trae() {
    print_info "配置 Trae IDE..."
    
    if [[ "$OS" == "macos" ]]; then
        CONFIG_DIR="$HOME/Library/Application Support/Trae"
        CONFIG_FILE="$CONFIG_DIR/mcp_config.json"
    else
        CONFIG_DIR="$HOME/.config/trae"
        CONFIG_FILE="$CONFIG_DIR/mcp_config.json"
    fi
    
    # 创建配置目录
    mkdir -p "$CONFIG_DIR"
    
    # 获取当前目录的绝对路径
    CURRENT_DIR=$(pwd)
    
    # 检查是否已有配置文件
    if [ -f "$CONFIG_FILE" ]; then
        print_info "检测到现有配置文件，将备份并更新..."
        cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        
        # 读取现有配置并合并
        if command -v jq &> /dev/null; then
            # 使用 jq 合并配置
            jq --arg name "draw-architecture" \
               --arg cmd "python3" \
               --arg script "$CURRENT_DIR/mcp_server.py" \
               --arg pythonpath "$CURRENT_DIR" \
               '.mcpServers[$name] = {"command": $cmd, "args": [$script], "env": {"PYTHONPATH": $pythonpath}}' \
               "$CONFIG_FILE" > "$CONFIG_FILE.tmp" && mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
        else
            # 手动合并（简单方式）
            print_warning "未安装 jq，将生成新的配置文件"
            cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "draw-architecture": {
      "command": "python3",
      "args": ["$CURRENT_DIR/mcp_server.py"],
      "env": {
        "PYTHONPATH": "$CURRENT_DIR"
      }
    }
  }
}
EOF
        fi
    else
        # 生成新的配置文件
        cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "draw-architecture": {
      "command": "python3",
      "args": ["$CURRENT_DIR/mcp_server.py"],
      "env": {
        "PYTHONPATH": "$CURRENT_DIR"
      }
    }
  }
}
EOF
    fi
    
    print_success "Trae IDE 配置已更新"
    print_info "配置文件位置: $CONFIG_FILE"
    print_info "请重启 Trae IDE 以加载新配置"
}

# 显示使用说明
show_usage() {
    print_info "安装完成！使用说明:"
    echo
    echo "1. 重启 AI 客户端 (Claude Desktop / Cline / Trae IDE)"
    echo "2. 在对话中测试功能:"
    echo "   - 请帮我生成一个系统架构图"
    echo "   - 请提供架构图绘制的提示词"
    echo "   - 请验证这个 draw.io 文件的格式"
    echo
    echo "3. 支持的客户端:"
    echo "   - Claude Desktop: 自动配置完成"
    echo "   - Cline: 使用生成的 cline_config.json"
    echo "   - Trae IDE: 自动配置到用户配置目录"
    echo
    echo "4. 查看更多示例:"
    echo "   - 阅读 README.md"
    echo "   - 查看 examples/ 目录"
    echo
    echo "5. 如果遇到问题:"
    echo "   - 运行测试: python3 test_mcp_server.py"
    echo "   - 查看日志文件"
    echo "   - 检查配置文件"
    echo "   - 确保客户端已重启"
    echo
}

# 主函数
main() {
    echo "=================================================="
    echo "  Draw.io Architecture MCP Server 安装程序"
    echo "=================================================="
    echo
    
    # 检查是否在正确的目录
    if [ ! -f "mcp_server.py" ]; then
        print_error "请在包含 mcp_server.py 的目录中运行此脚本"
        exit 1
    fi
    
    # 执行安装步骤
    check_system
    echo
    
    install_dependencies
    echo
    
    test_installation
    echo
    
    # 询问是否配置客户端
    read -p "是否配置 Trae IDE? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        configure_trae
        echo
    fi
    
    show_usage
    
    print_success "安装完成！"
}

# 运行主函数
main "$@"