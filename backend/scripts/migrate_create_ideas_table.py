"""
创建ideas表的数据库迁移脚本
用于存储用户的研究想法和灵感记录
"""
import sys
import os
import asyncio

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.models import engine


async def create_ideas_table():
    """创建ideas表"""
    async with engine.begin() as conn:
        # 检查表是否已存在
        result = await conn.execute(text("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='ideas'
        """))

        if result.fetchone():
            print("✓ ideas表已存在，跳过创建")
            return

        # 创建ideas表
        await conn.execute(text("""
            CREATE TABLE ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        print("✓ ideas表创建成功")

        # 创建索引
        await conn.execute(text("""
            CREATE INDEX idx_ideas_user_id ON ideas(user_id)
        """))
        print("✓ 创建索引: idx_ideas_user_id")

        await conn.execute(text("""
            CREATE INDEX idx_ideas_created_at ON ideas(created_at DESC)
        """))
        print("✓ 创建索引: idx_ideas_created_at")

        await conn.execute(text("""
            CREATE INDEX idx_ideas_deleted_at ON ideas(deleted_at)
        """))
        print("✓ 创建索引: idx_ideas_deleted_at")


async def main():
    """主函数"""
    try:
        print("开始创建ideas表...")
        await create_ideas_table()
        print("\n✅ 数据库迁移完成！")

        print("\n表结构说明:")
        print("- id: 主键")
        print("- user_id: 用户ID（外键，级联删除）")
        print("- title: 想法标题（可选）")
        print("- content: 想法内容（必填，支持Markdown）")
        print("- created_at: 创建时间")
        print("- updated_at: 更新时间")
        print("- deleted_at: 软删除时间")

    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
