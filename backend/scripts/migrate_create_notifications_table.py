"""
数据库迁移脚本：创建通知表
用于支持站内通知系统

运行方法：
    python scripts/migrate_create_notifications_table.py

创建时间：2026-01-13
"""
import sys
import os
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.models import engine

async def create_notifications_table():
    """创建notifications表"""
    async with engine.begin() as conn:
        # 检查表是否存在
        result = await conn.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='notifications'
        """))

        if result.fetchone():
            print("✅ notifications表已存在，跳过创建")
            return

        # 创建notifications表
        await conn.execute(text("""
            CREATE TABLE notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                link TEXT,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sender_id INTEGER,
                related_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """))

        # 创建索引
        await conn.execute(text("""
            CREATE INDEX idx_notifications_user_id ON notifications(user_id)
        """))

        await conn.execute(text("""
            CREATE INDEX idx_notifications_is_read ON notifications(is_read)
        """))

        await conn.execute(text("""
            CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC)
        """))

        await conn.execute(text("""
            CREATE INDEX idx_notifications_type ON notifications(type)
        """))

        print("✅ notifications表创建成功")
        print("   - 字段: id, user_id, type, title, content, link, is_read, created_at, sender_id, related_id")
        print("   - 索引: user_id, is_read, created_at, type")

if __name__ == "__main__":
    print("开始创建notifications表...")
    asyncio.run(create_notifications_table())
    print("迁移完成！")
