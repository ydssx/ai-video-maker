"""
用户模型

包含与用户相关的Pydantic模型。
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, validator

from src.core.validators import validate_password


# 基础属性
class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="电子邮箱")
    is_active: bool = Field(True, description="是否激活")
    is_superuser: bool = Field(False, description="是否超级用户")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "is_active": True,
                "is_superuser": False,
            }
        }


# 创建用户时的模型
class UserCreate(UserBase):
    """创建用户模型"""
    password: str = Field(..., min_length=8, max_length=100, description="密码")
    
    @validator('password')
    def password_complexity(cls, v: str) -> str:
        """验证密码复杂度"""
        return validate_password(v)
    
    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "full_name": "John Doe",
                "password": "securepassword123",
                "is_active": True,
                "is_superuser": False,
            }
        }


# 更新用户时的模型
class UserUpdate(UserBase):
    """更新用户模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="电子邮箱")
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="新密码")
    
    @validator('password')
    def password_complexity(cls, v: Optional[str]) -> Optional[str]:
        """验证密码复杂度"""
        if v is None:
            return v
        return validate_password(v)
    
    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe_updated",
                "email": "johndoe.updated@example.com",
                "full_name": "John Doe Updated",
                "password": "newsecurepassword123",
            }
        }


# 数据库中的用户模型
class UserInDBBase(UserBase):
    """数据库用户基础模型"""
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        orm_mode = True

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None
    scopes: List[str] = []

    @validator('scopes', pre=True, always=True)
    def set_scopes(cls, v):
        return v or []

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []


# API响应中的用户模型
class User(UserInDBBase):
    """API响应中的用户模型"""
    pass


# 用户登录模型
class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    
    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "password": "securepassword123",
            }
        }


# 用户注册模型
class UserRegister(UserCreate):
    """用户注册模型"""
    password_confirm: str = Field(..., description="确认密码")
    
    @validator('password_confirm')
    def passwords_match(cls, v: str, values: Dict[str, Any], **kwargs: Any) -> str:
        """验证两次输入的密码是否一致"""
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不匹配')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "full_name": "John Doe",
                "password": "securepassword123",
                "password_confirm": "securepassword123",
            }
        }


# 用户权限模型
class UserPermissions(BaseModel):
    """用户权限模型"""
    scopes: List[str] = Field(default_factory=list, description="权限列表")
