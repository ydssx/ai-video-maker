"""
安全工具模块

包含密码哈希、JWT令牌生成和验证等安全相关功能。
"""
from datetime import datetime, timedelta
from typing import Any, Optional, Union
import secrets

from jose import jwt
from passlib.context import CryptContext

from .config import settings

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT算法
ALGORITHM = settings.algorithm


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)


def verify_token(token: str) -> dict:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        dict: 解码后的令牌数据
        
    Raises:
        HTTPException: 如果令牌无效或已过期
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access"
) -> str:
    """
    创建JWT令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间差
        token_type: 令牌类型 (access/refresh)
        
    Returns:
        str: 编码后的JWT令牌
    """
    to_encode = data.copy()
    now = datetime.utcnow()
    
    # 设置过期时间
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    
    # 添加标准声明
    to_encode.update({
        "exp": expire,
        "iat": now,
        "type": token_type,
        "jti": secrets.token_urlsafe(16)  # JWT ID
    })
    
    # 生成令牌
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    创建刷新令牌

    Args:
        data: 要编码的数据

    Returns:
        str: 编码后的刷新令牌
    """
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    return create_access_token(data, expires_delta=expires_delta, token_type="refresh")

