"""
认证相关API路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta, date

from app.models import get_db
from app.schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse
from app.services import user_service
from app.utils.security import create_access_token
from app.utils.response import success_response, error_response

router = APIRouter()

# 登录安全配置
MAX_LOGIN_ATTEMPTS = 10  # 最大失败次数
LOCKOUT_DURATION_MINUTES = 5  # 冷却时间（分钟）


async def check_login_cooldown(db: AsyncSession, username: str):
    """检查账号是否在冷却期内"""
    query = text("""
        SELECT id, failed_login_attempts, last_failed_login, login_locked_until, last_login_date
        FROM users
        WHERE username = :username OR email = :username
    """)
    result = await db.execute(query, {"username": username})
    user_data = result.fetchone()

    if not user_data:
        return None, None

    user_id, attempts, last_failed, locked_until, last_login_date_val = user_data
    now = datetime.utcnow()
    today = date.today()

    # 如果是新的一天，重置计数器
    if last_login_date_val and last_login_date_val != today.isoformat():
        reset_query = text("""
            UPDATE users
            SET failed_login_attempts = 0, login_locked_until = NULL, last_login_date = :today
            WHERE id = :user_id
        """)
        await db.execute(reset_query, {"user_id": user_id, "today": today.isoformat()})
        await db.commit()
        return None, None

    # 检查是否在冷却期内
    if locked_until:
        if isinstance(locked_until, str):
            locked_until = datetime.fromisoformat(locked_until)

        if now < locked_until:
            remaining_seconds = int((locked_until - now).total_seconds())
            remaining_minutes = remaining_seconds // 60
            return user_id, f"账号已被锁定，请在 {remaining_minutes + 1} 分钟后重试"

    return user_id, None


async def record_login_failure(db: AsyncSession, user_id: int):
    """记录登录失败"""
    now = datetime.utcnow()
    today = date.today()

    # 增加失败次数
    query = text("""
        UPDATE users
        SET failed_login_attempts = failed_login_attempts + 1,
            last_failed_login = :now,
            last_login_date = :today
        WHERE id = :user_id
    """)
    await db.execute(query, {"user_id": user_id, "now": now, "today": today.isoformat()})

    # 获取当前失败次数
    check_query = text("""
        SELECT failed_login_attempts FROM users WHERE id = :user_id
    """)
    result = await db.execute(check_query, {"user_id": user_id})
    attempts = result.scalar()

    # 如果超过最大次数，设置冷却期
    if attempts >= MAX_LOGIN_ATTEMPTS:
        locked_until = now + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        lock_query = text("""
            UPDATE users
            SET login_locked_until = :locked_until
            WHERE id = :user_id
        """)
        await db.execute(lock_query, {"user_id": user_id, "locked_until": locked_until})
        await db.commit()
        return attempts, True  # 返回次数和是否被锁定

    await db.commit()
    return attempts, False


async def reset_login_attempts(db: AsyncSession, user_id: int):
    """重置登录失败次数"""
    query = text("""
        UPDATE users
        SET failed_login_attempts = 0,
            last_failed_login = NULL,
            login_locked_until = NULL,
            last_login_date = :today
        WHERE id = :user_id
    """)
    await db.execute(query, {"user_id": user_id, "today": date.today().isoformat()})
    await db.commit()


@router.post("/register", response_model=dict)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = await user_service.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    # 检查邮箱是否已存在
    existing_email = await user_service.get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    # 创建用户
    new_user = await user_service.create_user(db, user_data)

    return success_response(
        data={"user_id": new_user.id, "status": new_user.status},
        message="注册成功，请等待管理员审核"
    )


@router.post("/login", response_model=dict)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """用户登录"""
    # 1. 检查是否在冷却期内
    user_id, cooldown_message = await check_login_cooldown(db, login_data.username)
    if cooldown_message:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=cooldown_message
        )

    # 2. 验证用户（返回 user 和 error_message）
    user, error_message = await user_service.authenticate_user(
        db,
        login_data.username,
        login_data.password
    )

    if not user:
        # 如果用户存在但密码错误，记录失败次数
        if user_id and error_message == "密码错误":
            attempts, is_locked = await record_login_failure(db, user_id)
            remaining = MAX_LOGIN_ATTEMPTS - attempts

            if is_locked:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"密码错误次数过多，账号已被锁定 {LOCKOUT_DURATION_MINUTES} 分钟"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"密码错误，今日还可尝试 {remaining} 次（超过{MAX_LOGIN_ATTEMPTS}次将锁定{LOCKOUT_DURATION_MINUTES}分钟）"
                )

        # 用户名不存在的情况
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message  # "用户名不存在"
        )

    # 3. 检查账号状态
    if user.status == "pending":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号待审核，请等待管理员审核"
        )

    if user.status == "disabled":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    # 4. 登录成功，重置失败次数
    await reset_login_attempts(db, user.id)

    # 5. 创建访问令牌（sub必须是字符串）
    access_token = create_access_token(data={"sub": str(user.id)})
    print(f"🔍 [Login] Created token for user_id={user.id}: {access_token[:20]}...")

    # 6. 构造响应
    user_response = UserResponse.model_validate(user)
    token_response = TokenResponse(
        access_token=access_token,
        user=user_response
    )

    response_data = token_response.model_dump()
    print(f"🔍 [Login] Response data keys: {response_data.keys()}")
    print(f"🔍 [Login] access_token in response: {response_data.get('access_token')[:20] if response_data.get('access_token') else 'None'}...")

    return success_response(
        data=response_data,
        message="登录成功"
    )


@router.post("/logout", response_model=dict)
async def logout():
    """用户登出（前端删除token即可）"""
    return success_response(message="登出成功")
