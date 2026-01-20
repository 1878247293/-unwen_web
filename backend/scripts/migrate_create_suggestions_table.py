"""
数据库迁移脚本：创建改进建议表
用于支持用户向管理员提出改进建议功能

运行方法：
    python scripts/migrate_create_suggestions_table.py

创建时间：2026-01-12
"""
import sys
import os
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.models import engine

async def create_suggestions_table():
    """创建suggestions表"""
    async with engine.begin() as conn:
        # 检查表是否存在
        result = await conn.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='suggestions'
        """))

        if result.fetchone():
            print("✅ suggestions表已存在，跳过创建")
            return

        # 创建suggestions表
        await conn.execute(text("""
            CREATE TABLE suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                completed_by INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (completed_by) REFERENCES users(id) ON DELETE SET NULL
            )
        """))

        # 创建索引
        await conn.execute(text("""
            CREATE INDEX idx_suggestions_user_id ON suggestions(user_id)
        """))

        await conn.execute(text("""
            CREATE INDEX idx_suggestions_status ON suggestions(status)
        """))

        await conn.execute(text("""
            CREATE INDEX idx_suggestions_created_at ON suggestions(created_at DESC)
        """))

        print("✅ suggestions表创建成功")
        print("   - 字段: id, content, user_id, status, created_at, completed_at, completed_by")
        print("   - 索引: user_id, status, created_at")

if __name__ == "__main__":
    print("开始创建suggestions表...")
    asyncio.run(create_suggestions_table())
    print("迁移完成！")
