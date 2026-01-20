#!/bin/bash
# 后端环境配置脚本 (Linux/Mac)
# 在激活虚拟环境后运行此脚本

set -e  # 遇到错误立即退出

echo "========================================"
echo "  后端环境配置与初始化"
echo "========================================"
echo ""

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ 错误：虚拟环境未激活！"
    echo ""
    echo "请先运行激活脚本："
    echo "  bash activate.sh"
    echo ""
    exit 1
fi

echo "✅ 检测到虚拟环境：$VIRTUAL_ENV"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 步骤1: 升级pip
echo "----------------------------------------"
echo "步骤 1/4: 升级 pip"
echo "----------------------------------------"
pip install --upgrade pip
echo "✅ pip 升级完成"
echo ""

# 步骤2: 安装依赖包
echo "----------------------------------------"
echo "步骤 2/4: 安装 Python 依赖包"
echo "----------------------------------------"
pip install -r requirements.txt
echo "✅ 依赖包安装完成"
echo ""

# 步骤3: 创建必要的目录
echo "----------------------------------------"
echo "步骤 3/4: 创建数据目录"
echo "----------------------------------------"
mkdir -p data/uploads/pdfs
mkdir -p data/uploads/avatars
mkdir -p data/backups
echo "✅ 目录创建完成"
echo ""

# 步骤4: 初始化数据库
echo "----------------------------------------"
echo "步骤 4/4: 初始化数据库"
echo "----------------------------------------"
python scripts/init_db.py
echo ""

# 完成
echo "========================================"
echo "  环境配置完成！"
echo "========================================"
echo ""
echo "📌 默认管理员账号："
echo "   用户名: admin"
echo "   密码:   admin123"
echo ""
echo "⚠️  重要：首次登录后请立即修改密码！"
echo ""
echo "🚀 启动后端服务："
echo "   python app/main.py"
echo ""
echo "📚 查看API文档："
echo "   http://localhost:8000/docs"
echo ""
echo "========================================"
