"""
数据库模型基类

包含所有模型共用的字段和方法。
"""
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, Integer

from src.db.session import Base


class BaseModel(Base):
    """
    所有数据库模型的基类

    提供通用字段和方法。子类须显式设置 __tablename__。
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
