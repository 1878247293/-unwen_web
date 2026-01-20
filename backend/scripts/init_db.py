"""
数据库初始化脚本
"""
import asyncio
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models import init_db
from app.services.user_service import create_default_admin


async def main():
    """主函数"""
    print("=" * 50)
    print("开始初始化数据库...")
    print("=" * 50)

    # 创建数据库表
    await init_db()

    # 创建默认管理员
    await create_default_admin()

    print("=" * 50)
    print("数据库初始化完成！")
    print("=" * 50)
    print("\n默认管理员账号信息：")
    print("用户名: admin")
    print("密码: admin123")
    print("\n请登录后立即修改密码！\n")


if __name__ == "__main__":
    asyncio.run(main())
