"""
数据库仓库包

包含所有数据库仓库类，用于处理数据访问逻辑。
"""
from .base import CRUDBase
from .user import user_repo, UserRepository

__all__ = [
    'CRUDBase',
    'user_repo',
    'UserRepository',
]
