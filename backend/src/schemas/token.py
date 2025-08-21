"""
认证令牌模型

包含与认证令牌相关的Pydantic模型。
"""
from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    访问令牌响应模型
    
    包含访问令牌和令牌类型。
    """
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型，通常是'bearer'")


class TokenPayload(BaseModel):
    """
    令牌负载模型
    
    包含JWT令牌中的声明。
    """
    sub: Optional[str] = Field(None, description="主题（通常是用户ID）")
    exp: Optional[int] = Field(None, description="过期时间戳")
    iat: Optional[int] = Field(None, description="签发时间戳")
    jti: Optional[str] = Field(None, description="JWT ID")
    scopes: list[str] = Field(default_factory=list, description="权限范围")
