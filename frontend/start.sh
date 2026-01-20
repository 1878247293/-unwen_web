#!/bin/bash
# 一键配置并启动前端 (Linux/Mac)

set -e

echo "========================================"
echo "  一键配置并启动前端服务"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 步骤1: 检查 Node.js
echo "🔍 检查 Node.js 环境..."

if ! command -v node &> /dev/null; then
    echo "❌ 错误：未安装 Node.js"
    echo ""
    echo "请先安装 Node.js (版本 >= 16):"
    echo "  https://nodejs.org/"
    echo ""
    exit 1
fi

NODE_VERSION=$(node -v)
echo "✅ Node.js: $NODE_VERSION"
echo ""

# 步骤2: 检查是否需要安装依赖
if [ ! -d "node_modules" ] || [ ! -f ".setup_done" ]; then
    echo "📥 首次运行，开始配置环境..."
    echo ""

    # 安装依赖
    echo "安装 npm 依赖包..."
    echo "📦 使用淘宝镜像加速: https://registry.npmmirror.com"
    echo ""

    npm install --registry=https://registry.npmmirror.com

    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ 依赖安装失败"
        echo ""
        echo "请尝试："
        echo "  1. 检查网络连接"
        echo "  2. 检查 Node.js 版本是否 >= 16"
        echo "  3. 手动运行: bash setup.sh"
        exit 1
    fi

    echo ""
    echo "✅ 依赖安装完成"
    echo ""

    # 标记配置完成
    touch .setup_done

    echo "========================================"
    echo "  配置完成！"
    echo "========================================"
    echo ""
else
    echo "✅ 环境已配置"
    echo ""
fi

# 步骤3: 启动开发服务器
echo "========================================"
echo "  启动前端开发服务器"
echo "========================================"
echo ""
echo "🚀 服务即将启动..."
echo ""
echo "访问地址："
echo "  - 前端应用: http://localhost:5173"
echo "  - 网络访问: http://[your-ip]:5173"
echo ""
echo "代理配置："
echo "  - API代理: http://localhost:5173/api -> http://localhost:8000/api"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""
echo "========================================"
echo ""

# 启动应用
npm run dev
