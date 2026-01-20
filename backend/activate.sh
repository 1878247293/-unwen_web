#!/bin/bash
# 激活后端虚拟环境脚本 (Linux/Mac)

echo "================================"
echo "激活后端虚拟环境"
echo "================================"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR"

# 检查虚拟环境是否存在
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "❌ 虚拟环境不存在！"
    echo "正在创建虚拟环境..."
    python3 -m venv "$BACKEND_DIR/venv"
    echo "✅ 虚拟环境创建成功！"
fi

# 激活虚拟环境
echo "正在激活虚拟环境..."
source "$BACKEND_DIR/venv/bin/activate"

echo "✅ 虚拟环境已激活！"
echo ""
echo "现在可以运行配置脚本："
echo "  bash setup.sh"
echo ""
echo "或直接启动后端："
echo "  python app/main.py"
echo ""
echo "退出虚拟环境请输入："
echo "  deactivate"
echo "================================"

# 启动一个新的shell会话，保持虚拟环境激活状态
exec $SHELL
