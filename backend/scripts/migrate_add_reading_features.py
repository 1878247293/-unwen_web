"""
数据库迁移脚本：添加阅读功能相关字段和表
- 为papers表添加reading_progress字段
- 创建reading_history表
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import aiosqlite
from pathlib import Path


async def migrate():
    """执行数据库迁移"""
    db_path = Path(__file__).parent.parent / "data" / "database.db"

    print(f"数据库路径: {db_path}")

    if not db_path.exists():
        print("❌ 错误：数据库文件不存在")
        print(f"   请先运行初始化脚本创建数据库")
        return False

    try:
        async with aiosqlite.connect(db_path) as db:
            print("\n开始数据库迁移...")

            # 1. 检查papers表是否已有reading_progress字段
            print("\n步骤 1/3: 为papers表添加reading_progress字段")
            cursor = await db.execute("PRAGMA table_info(papers)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]

            if 'reading_progress' not in column_names:
                await db.execute("""
                    ALTER TABLE papers
                    ADD COLUMN reading_progress INTEGER NOT NULL DEFAULT 0
                """)
                print("✅ reading_progress字段添加成功")
            else:
                print("⏭️  reading_progress字段已存在，跳过")

            # 2. 检查reading_history表是否存在
            print("\n步骤 2/3: 创建reading_history表")
            cursor = await db.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='reading_history'
            """)
            table_exists = await cursor.fetchone()

            if not table_exists:
                await db.execute("""
                    CREATE TABLE reading_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        paper_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        start_time DATETIME NOT NULL,
                        end_time DATETIME,
                        duration_seconds INTEGER NOT NULL DEFAULT 0,
                        progress_before INTEGER NOT NULL DEFAULT 0,
                        progress_after INTEGER NOT NULL DEFAULT 0,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (paper_id) REFERENCES papers (id),
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)

                # 创建索引
                await db.execute("""
                    CREATE INDEX idx_reading_history_paper_id
                    ON reading_history(paper_id)
                """)
                await db.execute("""
                    CREATE INDEX idx_reading_history_user_id
                    ON reading_history(user_id)
                """)
                await db.execute("""
                    CREATE INDEX idx_reading_history_start_time
                    ON reading_history(start_time)
                """)

                print("✅ reading_history表创建成功")
            else:
                print("⏭️  reading_history表已存在，跳过")

            # 3. 提交更改
            print("\n步骤 3/3: 提交更改")
            await db.commit()
            print("✅ 数据库迁移完成")

            # 验证迁移结果
            print("\n验证迁移结果...")
            cursor = await db.execute("PRAGMA table_info(papers)")
            papers_columns = await cursor.fetchall()
            has_reading_progress = any(col[1] == 'reading_progress' for col in papers_columns)

            cursor = await db.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='reading_history'
            """)
            has_reading_history = await cursor.fetchone() is not None

            if has_reading_progress and has_reading_history:
                print("✅ 所有更改已成功应用")
                return True
            else:
                print("❌ 迁移验证失败")
                return False

    except Exception as e:
        print(f"❌ 迁移失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("=" * 60)
    print("  数据库迁移：添加阅读功能")
    print("=" * 60)
    print("")

    success = await migrate()

    print("")
    print("=" * 60)
    if success:
        print("  迁移完成！")
    else:
        print("  迁移失败！")
    print("=" * 60)
    print("")

    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
