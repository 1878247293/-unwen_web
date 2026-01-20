#!/bin/bash
# 清理并重装前端依赖 (Linux/Mac)

echo "========================================"
echo "  清理前端环境"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "⚠️  警告：此操作将删除以下内容："
echo "  - node_modules/ (依赖包)"
echo "  - package-lock.json (依赖锁文件)"
echo "  - dist/ (构建输出)"
echo "  - .setup_done (配置标记)"
echo ""
echo "是否继续？(y/N)"
read -n 1 -r CONFIRM
echo ""

if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "🗑️  正在清理..."
echo ""

# 删除文件
rm -rf node_modules
rm -f package-lock.json
rm -rf dist
rm -f .setup_done

echo "✅ 清理完成！"
echo ""
echo "现在可以重新安装："
echo "  bash setup.sh"
echo ""
echo "或一键启动："
echo "  bash start.sh"
echo ""
