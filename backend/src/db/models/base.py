"""
数据库模型基类

包含所有模型共用的字段和方法。
"""
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import as_declarative, declared_attr

from src.db.session import Base


@as_declarative()
class BaseModel:
    """
    所有数据库模型的基类
    
    提供通用字段和方法
    """
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    
    @declared_attr
    def __tablename__(cls) -> str:
        """
        生成表名
        
        将类名转换为下划线命名法的表名
        例如: UserProfile -> user_profile
        """
        return ''.join(
            ['_' + i.lower() if i.isupper() else i for i in cls.__name__]
        ).lstrip('_')
    
    def to_dict(self) -> Dict[str, Any]:
        """
        将模型实例转换为字典
        
        Returns:
            Dict[str, Any]: 包含模型字段的字典
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update(self, **kwargs) -> None:
        """
        更新模型字段
        
        Args:
            **kwargs: 要更新的字段和值
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
