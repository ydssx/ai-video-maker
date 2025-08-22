"""
用户仓库

处理用户相关的数据库操作。
"""
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from src.core.security import get_password_hash, verify_password
from src.db.models.user import User
from src.db.repositories.base import CRUDBase
from src.schemas.user import UserCreate, UserUpdate


class UserRepository(CRUDBase[User, UserCreate, UserUpdate]):
    """
    用户仓库类
    
    处理用户相关的数据库操作
    """
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """
        通过邮箱获取用户
        
        Args:
            db: 数据库会话
            email: 用户邮箱
            
        Returns:
            Optional[User]: 找到的用户或None
        """
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """
        通过用户名获取用户
        
        Args:
            db: 数据库会话
            username: 用户名
            
        Returns:
            Optional[User]: 找到的用户或None
        """
        return db.query(User).filter(User.username == username).first()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        创建新用户
        
        Args:
            db: 数据库会话
            obj_in: 包含用户创建数据的Pydantic模型
            
        Returns:
            User: 创建的用户
            
        Raises:
            HTTPException: 如果用户名或邮箱已存在
        """
        # 检查用户名是否已存在
        db_user = self.get_by_username(db, username=obj_in.username)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在",
            )
        
        # 检查邮箱是否已存在
        if obj_in.email:
            db_user = self.get_by_email(db, email=obj_in.email)
            if db_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已注册",
                )
        
        # 创建用户
        user_data = obj_in.dict(exclude={"password"})
        hashed_password = get_password_hash(obj_in.password)
        
        # 确保 is_active 字段值是正确的（优先使用传入的值，默认为 True）
        if 'is_active' not in user_data:
            user_data['is_active'] = True
            
        db_user = User(
            **user_data,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        更新用户信息
        
        Args:
            db: 数据库会话
            db_obj: 要更新的用户记录
            obj_in: 包含更新数据的Pydantic模型或字典
            
        Returns:
            User: 更新后的用户
            
        Raises:
            HTTPException: 如果新用户名或邮箱已存在
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # 如果更新了密码，进行哈希处理
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        # 检查用户名是否已存在
        if "username" in update_data and update_data["username"] != db_obj.username:
            existing_user = self.get_by_username(db, username=update_data["username"])
            if existing_user and existing_user.id != db_obj.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="用户名已存在",
                )
        
        # 检查邮箱是否已存在
        if "email" in update_data and update_data["email"] != db_obj.email:
            existing_user = self.get_by_email(db, email=update_data["email"])
            if existing_user and existing_user.id != db_obj.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已注册",
                )
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def authenticate(
        self, db: Session, *, username: str, password: str
    ) -> Optional[User]:
        """
        用户认证
        
        Args:
            db: 数据库会话
            username: 用户名
            password: 密码
            
        Returns:
            Optional[User]: 认证成功的用户或None
        """
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def is_active(self, user: User) -> bool:
        """
        检查用户是否激活
        
        Args:
            user: 用户对象
            
        Returns:
            bool: 用户是否激活
        """
        return user.is_active
    
    def is_superuser(self, user: User) -> bool:
        """
        检查用户是否是超级用户
        
        Args:
            user: 用户对象
            
        Returns:
            bool: 用户是否是超级用户
        """
        return user.is_superuser


# 创建用户仓库实例
user_repo = UserRepository(User)
