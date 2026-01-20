"""
JWT令牌工具
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码访问令牌"""
    try:
        print(f"🔍 [decode_access_token] Attempting to decode token")
        print(f"🔍 [decode_access_token] SECRET_KEY: {settings.SECRET_KEY[:20]}...")
        print(f"🔍 [decode_access_token] ALGORITHM: {settings.ALGORITHM}")

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print(f"✅ [decode_access_token] Successfully decoded: {payload}")
        return payload
    except JWTError as e:
        print(f"❌ [decode_access_token] JWTError: {type(e).__name__}: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ [decode_access_token] Unexpected error: {type(e).__name__}: {str(e)}")
        return None
