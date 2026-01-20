"""
为ideas表添加references字段的数据库迁移脚本
运行方式: python scripts/migrate_add_references_to_ideas.py
"""
import asyncio
from sqlalchemy import text
from app.models import engine


async def add_references_field():
    """为ideas表添加references字段"""
    print("开始迁移：为ideas表添加references字段...")

    async with engine.begin() as conn:
        try:
            # 检查字段是否已存在
            check_query = text("""
                SELECT COUNT(*) as count
                FROM pragma_table_info('ideas')
                WHERE name = 'references'
            """)
            result = await conn.execute(check_query)
            exists = result.scalar()

            if exists > 0:
                print("⚠️  references字段已存在，跳过迁移")
                return

            # 添加references字段
            print("正在添加references字段...")
            await conn.execute(text("""
                ALTER TABLE ideas ADD COLUMN references TEXT
            """))

            print("✅ references字段添加成功")

        except Exception as e:
            print(f"❌ 迁移失败: {str(e)}")
            raise

    print("迁移完成！")


async def main():
    """主函数"""
    try:
        await add_references_field()
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
