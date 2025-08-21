"""
API 依赖项

包含所有API端点共用的依赖项，如数据库会话、认证等。
"""
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from core.config import settings
from core.security import ALGORITHM
from db.session import SessionLocal
from schemas.token import TokenPayload

# OAuth2 密码授权流程
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

def get_db() -> Generator:
    """
    获取数据库会话
    
    Yields:
        Session: SQLAlchemy 数据库会话
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# 示例：获取当前用户
def get_current_user():
    """
    获取当前认证用户
    
    这是一个示例函数，需要根据实际认证系统实现
    """
    async def _get_current_user(
        token: str = Depends(reusable_oauth2),
        db: Session = Depends(get_db),
    ):
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[ALGORITHM]
            )
            token_data = TokenPayload(**payload)
        except (jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无法验证凭据",
            )
        # 这里添加获取用户逻辑
        # user = crud.user.get(db, id=token_data.sub)
        # if not user:
        #     raise HTTPException(status_code=404, detail="用户不存在")
        # return user
        return None
    
    return _get_current_user

# 示例：获取当前活跃用户
def get_current_active_user():
    """
    获取当前活跃用户
    
    这是一个示例函数，需要根据实际认证系统实现
    """
    async def _get_current_active_user(
        current_user = Depends(get_current_user()),
    ):
        # 这里添加用户状态检查逻辑
        # if not crud.user.is_active(current_user):
        #     raise HTTPException(status_code=400, detail="用户未激活")
        # return current_user
        return None
    
    return _get_current_active_user
