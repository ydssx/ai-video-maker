"""
API 依赖项

包含所有API端点共用的依赖项，如数据库会话、认证等。
"""
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from loguru import logger
from pydantic import ValidationError
from sqlalchemy.orm import Session

from src.core.config import settings
from src.core.security import ALGORITHM
from src.db.session import get_db
from src.schemas.token import TokenPayload
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from src.schemas.user import UserInDB, TokenData
from src.db.repositories.user import user_repo


# OAuth2 方案
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "user:read": "Read user information",
        "user:write": "Modify user information",
        "admin": "Admin access"
    }
)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> UserInDB:
    """获取当前认证用户"""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope=\"{security_scopes.scope_str}\"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except JWTError as e:
        logger.error(f"JWT 验证失败: {str(e)}")
        raise credentials_exception
    except ValidationError as e:
        logger.error(f"Token 数据验证失败: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"未知的 Token 验证错误: {str(e)}")
        raise credentials_exception
    
    try:
        user = user_repo.get_by_username(db, username=token_data.username)
        if user is None:
            raise credentials_exception
    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="无法获取用户信息"
        )
    
    # 检查权限范围
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    return user
