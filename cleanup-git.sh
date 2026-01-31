#!/bin/bash

# Git 仓库清理脚本
# 用于从 Git 跟踪中移除不必要的文件（如 venv, __pycache__, node_modules 等）
# 但不会删除本地文件

echo "========================================="
echo "Git 仓库清理脚本"
echo "========================================="
echo ""

# 显示当前 Git 状态
echo "当前 Git 状态:"
git status --short | wc -l | xargs echo "待上传文件数量:"
echo ""

# 显示已跟踪的不应该跟踪的文件数量
echo "已跟踪的不应该跟踪的文件数量:"
git ls-files | grep -E "(__pycache__|venv/|node_modules/|\.pyc|database\.db)" | wc -l
echo ""

# 询问是否继续
read -p "是否继续清理? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "操作已取消"
    exit 1
fi

echo ""
echo "开始清理..."
echo ""

# 从 Git 缓存中移除文件（但不删除本地文件）
echo "1. 移除 Python 虚拟环境 (venv/)..."
git rm -r --cached backend/venv/ 2>/dev/null || echo "   venv/ 已清理或不存在"

echo "2. 移除 Python 缓存文件 (__pycache__)..."
find backend -name "__pycache__" -type d -exec git rm -r --cached {} + 2>/dev/null || echo "   __pycache__ 已清理或不存在"

echo "3. 移除 Node 依赖 (node_modules/)..."
git rm -r --cached frontend/node_modules/ 2>/dev/null || echo "   node_modules/ 已清理或不存在"

echo "4. 移除数据库文件..."
git rm --cached backend/data/database.db 2>/dev/null || echo "   database.db 已清理或不存在"

echo "5. 移除上传文件目录..."
git rm -r --cached backend/data/uploads/ 2>/dev/null || echo "   uploads/ 已清理或不存在"

echo "6. 移除备份文件目录..."
git rm -r --cached backend/data/backups/ 2>/dev/null || echo "   backups/ 已清理或不存在"

echo "7. 移除日志文件..."
git rm --cached backend/logs/*.log 2>/dev/null || echo "   日志文件已清理或不存在"

echo "8. 移除进程ID文件..."
git rm --cached backend/backend.pid 2>/dev/null || echo "   backend.pid 已清理或不存在"
git rm --cached frontend/frontend.pid 2>/dev/null || echo "   frontend.pid 已清理或不存在"

echo ""
echo "清理完成！"
echo ""

# 添加 .gitignore
echo "添加 .gitignore..."
git add .gitignore

# 显示清理后的状态
echo "========================================="
echo "清理后的 Git 状态:"
echo "========================================="
git status --short | wc -l | xargs echo "待上传文件数量:"
echo ""

# 显示待提交的内容
echo "待提交的更改:"
git status --short
echo ""

# 提示提交
echo "========================================="
echo "下一步操作:"
echo "========================================="
echo "1. 检查上面的更改是否正确"
echo "2. 如果正确，运行以下命令提交:"
echo "   git commit -m \"chore: 更新 .gitignore 并从仓库中移除不必要的文件\""
echo "   git push origin main"
echo ""
echo "3. 如果不正确，运行以下命令恢复:"
echo "   git reset --hard HEAD"
echo ""
