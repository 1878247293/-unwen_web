"""
FastAPI依赖项
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User, get_db
from app.utils.security import decode_access_token

# OAuth2密码认证方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """获取当前用户"""
    print(f"🔍 [get_current_user] Received token: {token[:20] if token else 'None'}...")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 解码令牌
    payload = decode_access_token(token)
    print(f"🔍 [get_current_user] Decoded payload: {payload}")

    if payload is None:
        print("❌ [get_current_user] Failed to decode token")
        raise credentials_exception

    user_id_str = payload.get("sub")
    print(f"🔍 [get_current_user] Extracted user_id (string): {user_id_str}")

    if user_id_str is None:
        print("❌ [get_current_user] No user_id in payload")
        raise credentials_exception

    # 将字符串转换为整数
    try:
        user_id: int = int(user_id_str)
        print(f"🔍 [get_current_user] Converted to int: {user_id}")
    except (ValueError, TypeError) as e:
        print(f"❌ [get_current_user] Failed to convert user_id to int: {e}")
        raise credentials_exception

    # 查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    print(f"🔍 [get_current_user] Found user: {user.username if user else 'None'}")

    if user is None:
        print("❌ [get_current_user] User not found in database")
        raise credentials_exception

    if user.status != "active":
        print(f"❌ [get_current_user] User status is {user.status}, not active")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号未激活或已被禁用"
        )

    print(f"✅ [get_current_user] Success for user: {user.username}")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前激活用户"""
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号未激活"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """获取当前管理员用户"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


def check_permission(user: User, resource_user_id: int) -> bool:
    """检查用户是否有权限操作资源"""
    # 管理员拥有所有权限
    if user.role == "admin":
        return True
    # 用户只能操作自己的资源
    return user.id == resource_user_id
