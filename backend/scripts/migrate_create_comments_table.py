"""
数据库迁移脚本：创建评论表
用于支持论文评论功能

运行方法：
    python scripts/migrate_create_comments_table.py

创建时间：2026-01-12
"""
import sys
import os
import asyncio

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.models import engine


async def migrate():
    """执行数据库迁移"""
    print("=" * 60)
    print("开始数据库迁移：创建 comments 表")
    print("=" * 60)

    async with engine.begin() as conn:
        # 检查表是否已存在
        print("\n[1/3] 检查 comments 表是否已存在...")
        result = await conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='comments'"
        ))
        existing_table = result.fetchone()

        if existing_table:
            print("✓ comments 表已存在，跳过迁移")
            return

        # 创建评论表
        print("\n[2/3] 创建 comments 表...")
        await conn.execute(text("""
            CREATE TABLE comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                parent_id INTEGER,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                FOREIGN KEY (paper_id) REFERENCES papers (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (parent_id) REFERENCES comments (id)
            )
        """))
        print("✓ comments 表创建成功")

        # 创建索引
        print("\n[3/3] 创建索引...")
        await conn.execute(text(
            "CREATE INDEX idx_comments_paper_id ON comments (paper_id)"
        ))
        await conn.execute(text(
            "CREATE INDEX idx_comments_user_id ON comments (user_id)"
        ))
        await conn.execute(text(
            "CREATE INDEX idx_comments_parent_id ON comments (parent_id)"
        ))
        print("✓ 索引创建成功")

        # 验证表创建成功
        result = await conn.execute(text("PRAGMA table_info(comments)"))
        columns = [row[1] for row in result.fetchall()]

        print("\n" + "=" * 60)
        print("迁移完成！")
        print("=" * 60)
        print(f"comments 表字段：{', '.join(columns)}")
        print("\n说明：")
        print("  - paper_id: 论文ID")
        print("  - user_id: 评论用户ID")
        print("  - content: 评论内容")
        print("  - parent_id: 父评论ID（用于回复功能，NULL表示顶层评论）")
        print("  - deleted_at: 软删除时间戳")
        print("=" * 60)


async def rollback():
    """回滚迁移（删除表）"""
    print("=" * 60)
    print("回滚迁移：删除 comments 表")
    print("=" * 60)

    async with engine.begin() as conn:
        # 检查表是否存在
        result = await conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='comments'"
        ))
        existing_table = result.fetchone()

        if not existing_table:
            print("✓ comments 表不存在，无需回滚")
            return

        # 删除表
        await conn.execute(text("DROP TABLE IF EXISTS comments"))
        print("✓ comments 表已删除")

    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(rollback())
    else:
        asyncio.run(migrate())
