#!/bin/bash
# 一键配置并启动后端 (Linux/Mac)

set -e

echo "========================================"
echo "  一键配置并启动后端服务"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 步骤1: 检查并创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
    echo ""
fi

# 步骤2: 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate
echo "✅ 虚拟环境已激活"
echo ""

# 步骤3: 检查是否需要安装依赖
if [ ! -f ".setup_done" ]; then
    echo "📥 首次运行，开始配置环境..."
    echo ""

    # 升级pip
    echo "升级 pip..."
    pip install --upgrade pip
    echo ""

    # 安装依赖
    echo "安装依赖包..."
    pip install -r requirements.txt
    echo ""

    # 创建目录
    echo "创建数据目录..."
    mkdir -p data/uploads/pdfs
    mkdir -p data/uploads/avatars
    mkdir -p data/backups
    echo ""

    # 初始化数据库
    echo "初始化数据库..."
    python scripts/init_db.py
    echo ""

    # 标记配置完成
    touch .setup_done

    echo "========================================"
    echo "  配置完成！"
    echo "========================================"
    echo ""
    echo "📌 默认管理员账号："
    echo "   用户名: admin"
    echo "   密码:   admin123"
    echo ""
    echo "⚠️  重要：首次登录后请立即修改密码！"
    echo ""
else
    echo "✅ 环境已配置"
    echo ""
fi

# 步骤4: 启动服务
echo "========================================"
echo "  启动后端服务"
echo "========================================"
echo ""
echo "🚀 服务即将启动..."
echo ""
echo "访问地址："
echo "  - API文档: http://localhost:8000/docs"
echo "  - 健康检查: http://localhost:8000/health"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""
echo "========================================"
echo ""

# 启动应用（使用模块方式）
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
