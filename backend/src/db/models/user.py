"""
用户模型

包含用户相关的数据库模型。
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON
from sqlalchemy.orm import relationship, scoped_session

from .base import BaseModel


class User(BaseModel):
    """
    用户模型
    
    存储用户账户信息和基本资料
    """
    __tablename__ = "users"
    
    # 基本信息
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    
    # 用户状态
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    scopes = Column(Text)
    
    # 个人信息
    # full_name = Column(String(100), nullable=True)
    # avatar = Column(String(255), nullable=True)
    # bio = Column(Text, nullable=True)
    
    # 设置和首选项
    preferences = Column(JSON, default=dict, nullable=False)
    
    # 关系
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"
    
    @property
    def is_authenticated(self) -> bool:
        """
        用户是否已认证
        
        Returns:
            bool: 如果用户已认证返回True
        """
        return self.is_active
    
    @classmethod
    def create(
        cls,
        username: str,
        password: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        is_superuser: bool = False,
    ) -> 'User':
        """
        创建新用户
        
        Args:
            username: 用户名
            password: 明文密码
            email: 电子邮箱
            full_name: 全名
            is_superuser: 是否是超级用户
            
        Returns:
            User: 新创建的用户实例
        """
        from core.security import get_password_hash
        
        return cls(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            is_superuser=is_superuser,
        )
    
    def verify_password(self, password: str) -> bool:
        """
        验证密码
        
        Args:
            password: 要验证的明文密码
            
        Returns:
            bool: 密码是否匹配
        """
        from core.security import verify_password
        return verify_password(password, self.hashed_password)
