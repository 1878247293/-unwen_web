"""
用户服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.models import User, UserAIQuota
from app.models.db_session import AsyncSessionLocal
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash
from app.config import settings


async def create_default_admin():
    """创建默认管理员账号"""
    async with AsyncSessionLocal() as db:
        # 检查是否已存在管理员
        result = await db.execute(
            select(User).where(User.username == settings.ADMIN_USERNAME)
        )
        existing_admin = result.scalar_one_or_none()

        if not existing_admin:
            # 创建管理员账号
            admin = User(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                password=get_password_hash(settings.ADMIN_PASSWORD),
                role="admin",
                status="active",
                department="系统管理"
            )
            db.add(admin)
            await db.commit()
            await db.refresh(admin)

            # 创建AI额度记录
            ai_quota = UserAIQuota(
                user_id=admin.id,
                daily_limit=99999,
                monthly_limit=99999,
            )
            db.add(ai_quota)
            await db.commit()

            print(f"默认管理员账号已创建: {settings.ADMIN_USERNAME}")
        else:
            print("管理员账号已存在")


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """创建新用户"""
    # 创建用户
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=get_password_hash(user_data.password),
        role="user",
        status="pending",  # 默认待审核状态
        department=user_data.department,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 创建AI额度记录
    ai_quota = UserAIQuota(
        user_id=new_user.id,
        daily_limit=50,
        monthly_limit=1000,
    )
    db.add(ai_quota)
    await db.commit()

    return new_user


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """根据邮箱获取用户"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, username: str, password: str):
    """
    验证用户登录
    返回: (user, error_message)
    - 成功: (User对象, None)
    - 用户不存在: (None, "用户名不存在")
    - 密码错误: (None, "密码错误")
    """
    from app.utils.security import verify_password

    # 尝试通过用户名查找
    user = await get_user_by_username(db, username)

    # 如果用户名找不到，尝试通过邮箱查找
    if not user:
        user = await get_user_by_email(db, username)

    if not user:
        return None, "用户名不存在"

    # 验证密码
    if not verify_password(password, user.password):
        return None, "密码错误"

    return user, None
