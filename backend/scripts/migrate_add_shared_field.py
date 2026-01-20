"""
数据库迁移脚本：为 Paper 表添加 is_shared 字段
用于支持共享论文库和私人论文库的区分

运行方法：
    python scripts/migrate_add_shared_field.py

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
    print("开始数据库迁移：添加 is_shared 字段到 papers 表")
    print("=" * 60)

    async with engine.begin() as conn:
        # 检查字段是否已存在
        print("\n[1/3] 检查 is_shared 字段是否已存在...")
        result = await conn.execute(text("PRAGMA table_info(papers)"))
        columns = [row[1] for row in result.fetchall()]

        if 'is_shared' in columns:
            print("✓ is_shared 字段已存在，跳过迁移")
            return

        # 添加 is_shared 字段
        print("\n[2/3] 添加 is_shared 字段...")
        await conn.execute(text("""
            ALTER TABLE papers
            ADD COLUMN is_shared BOOLEAN DEFAULT 0 NOT NULL
        """))
        print("✓ is_shared 字段添加成功")

        # 验证字段添加成功
        print("\n[3/3] 验证字段添加...")
        result = await conn.execute(text("PRAGMA table_info(papers)"))
        columns_after = [row[1] for row in result.fetchall()]

        if 'is_shared' in columns_after:
            print("✓ 验证成功！字段已正确添加到数据库")
        else:
            print("✗ 验证失败！字段未添加")
            return

        # 显示当前论文统计
        result = await conn.execute(text("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN is_shared = 1 THEN 1 ELSE 0 END) as shared,
                SUM(CASE WHEN is_shared = 0 THEN 1 ELSE 0 END) as private
            FROM papers
            WHERE deleted_at IS NULL
        """))
        stats = result.fetchone()

        print("\n" + "=" * 60)
        print("迁移完成！")
        print("=" * 60)
        print(f"论文统计：")
        print(f"  - 总计：{stats[0]} 篇")
        print(f"  - 共享：{stats[1]} 篇")
        print(f"  - 私人：{stats[2]} 篇")
        print("\n说明：")
        print("  - is_shared = 0（False）: 私人论文，仅创建者和管理员可见")
        print("  - is_shared = 1（True）:  共享论文，所有用户可见")
        print("  - 现有论文默认为私人论文（is_shared = 0）")
        print("=" * 60)


async def rollback():
    """回滚迁移（删除字段）"""
    print("=" * 60)
    print("回滚迁移：删除 is_shared 字段")
    print("=" * 60)
    print("\n警告：SQLite 不支持 DROP COLUMN")
    print("如需回滚，请手动重建数据库或使用备份")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        asyncio.run(rollback())
    else:
        asyncio.run(migrate())
