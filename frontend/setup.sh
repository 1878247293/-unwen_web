#!/bin/bash
# 前端环境配置脚本 (Linux/Mac)

set -e  # 遇到错误立即退出

echo "========================================"
echo "  前端环境配置与初始化"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 步骤1: 检查 Node.js 和 npm
echo "----------------------------------------"
echo "步骤 1/3: 检查环境"
echo "----------------------------------------"

if ! command -v node &> /dev/null; then
    echo "❌ 错误：未安装 Node.js"
    echo ""
    echo "请先安装 Node.js (版本 >= 16):"
    echo "  https://nodejs.org/"
    echo ""
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ 错误：未安装 npm"
    exit 1
fi

NODE_VERSION=$(node -v)
NPM_VERSION=$(npm -v)

echo "✅ Node.js: $NODE_VERSION"
echo "✅ npm: $NPM_VERSION"
echo ""

# 步骤2: 清理旧的依赖（可选）
echo "----------------------------------------"
echo "步骤 2/3: 清理旧依赖"
echo "----------------------------------------"

if [ -d "node_modules" ]; then
    echo "发现旧的 node_modules，是否删除并重新安装？(y/N)"
    read -t 5 -n 1 -r CLEAN_DEPS || CLEAN_DEPS="n"
    echo ""

    if [[ $CLEAN_DEPS =~ ^[Yy]$ ]]; then
        echo "正在删除 node_modules..."
        rm -rf node_modules package-lock.json
        echo "✅ 清理完成"
    else
        echo "跳过清理"
    fi
else
    echo "未发现旧依赖，跳过清理"
fi
echo ""

# 步骤3: 安装依赖
echo "----------------------------------------"
echo "步骤 3/3: 安装 npm 依赖包"
echo "----------------------------------------"

# 自动使用淘宝镜像加速下载
echo "正在安装依赖..."
echo "📦 使用淘宝镜像加速: https://registry.npmmirror.com"
echo ""

npm install --registry=https://registry.npmmirror.com

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 依赖包安装完成"
else
    echo ""
    echo "❌ 依赖包安装失败"
    echo ""
    echo "请检查："
    echo "  1. 网络连接是否正常"
    echo "  2. Node.js 版本是否 >= 16"
    echo "  3. 磁盘空间是否充足"
    exit 1
fi

echo ""

# 完成
echo "========================================"
echo "  环境配置完成！"
echo "========================================"
echo ""
echo "📋 已安装的依赖："
echo "  - React + React DOM"
echo "  - React Router"
echo "  - Ant Design"
echo "  - Axios"
echo "  - Zustand"
echo "  - React Color"
echo "  - 其他开发依赖..."
echo ""
echo "🚀 启动开发服务器："
echo "   npm run dev"
echo ""
echo "📦 构建生产版本："
echo "   npm run build"
echo ""
echo "👀 预览生产版本："
echo "   npm run preview"
echo ""
echo "========================================"
