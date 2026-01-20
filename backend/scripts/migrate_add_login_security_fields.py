"""
为users表添加登录安全相关字段
运行方式: python scripts/migrate_add_login_security_fields.py
"""
import asyncio
from sqlalchemy import text
from app.models import engine


async def add_login_security_fields():
    """为users表添加登录安全字段"""
    print("开始迁移：为users表添加登录安全字段...")

    async with engine.begin() as conn:
        try:
            # 检查字段是否已存在
            check_query = text("""
                SELECT COUNT(*) as count
                FROM pragma_table_info('users')
                WHERE name IN ('failed_login_attempts', 'last_failed_login', 'login_locked_until', 'last_login_date')
            """)
            result = await conn.execute(check_query)
            exists = result.scalar()

            if exists > 0:
                print("⚠️  登录安全字段已存在，跳过迁移")
                return

            # 添加字段
            print("正在添加登录安全字段...")

            # failed_login_attempts - 当天失败次数
            await conn.execute(text("""
                ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0
            """))
            print("✅ 添加 failed_login_attempts 字段")

            # last_failed_login - 最后一次失败登录时间
            await conn.execute(text("""
                ALTER TABLE users ADD COLUMN last_failed_login TIMESTAMP
            """))
            print("✅ 添加 last_failed_login 字段")

            # login_locked_until - 锁定到什么时候
            await conn.execute(text("""
                ALTER TABLE users ADD COLUMN login_locked_until TIMESTAMP
            """))
            print("✅ 添加 login_locked_until 字段")

            # last_login_date - 最后一次登录日期（用于判断是否新的一天）
            await conn.execute(text("""
                ALTER TABLE users ADD COLUMN last_login_date DATE
            """))
            print("✅ 添加 last_login_date 字段")

            print("✅ 所有登录安全字段添加成功")

        except Exception as e:
            print(f"❌ 迁移失败: {str(e)}")
            raise

    print("迁移完成！")


async def main():
    """主函数"""
    try:
        await add_login_security_fields()
    except Exception as e:
        print(f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
