"""
权限服务

处理资源访问权限验证
"""
from typing import Optional

from sqlalchemy.orm import Session

from db import crud
from db.models import User, Asset, Project
from core.exceptions import (
    PermissionDeniedError,
    AssetNotFoundError,
    ProjectNotFoundError
)


class PermissionService:
    """权限服务"""
    
    def __init__(self, db: Session, current_user: User):
        """
        初始化权限服务
        
        Args:
            db: 数据库会话
            current_user: 当前用户
        """
        self.db = db
        self.current_user = current_user
    
    def check_is_owner(self, resource_owner_id: int) -> bool:
        """
        检查当前用户是否是资源所有者
        
        Args:
            resource_owner_id: 资源所有者的用户ID
            
        Returns:
            bool: 如果是资源所有者返回True，否则返回False
        """
        return self.current_user.id == resource_owner_id
    
    def check_is_superuser(self) -> bool:
        """
        检查当前用户是否是超级用户
        
        Returns:
            bool: 如果是超级用户返回True，否则返回False
        """
        return self.current_user.is_superuser
    
    def check_asset_permission(self, asset_id: int, require_owner: bool = False) -> Asset:
        """
        检查用户是否有权限访问资源
        
        Args:
            asset_id: 资源ID
            require_owner: 是否要求是资源所有者
            
        Returns:
            Asset: 资源对象
            
        Raises:
            AssetNotFoundError: 资源不存在
            PermissionDeniedError: 没有权限访问资源
        """
        # 获取资源
        asset = crud.asset.get(self.db, id=asset_id)
        if not asset:
            raise AssetNotFoundError()
        
        # 超级用户可以访问所有资源
        if self.check_is_superuser():
            return asset
        
        # 检查是否是资源所有者
        if self.check_is_owner(asset.owner_id):
            return asset
        
        # 如果资源属于项目，检查项目权限
        if asset.project_id:
            project = crud.project.get(self.db, id=asset.project_id)
            if not project:
                raise ProjectNotFoundError()
                
            # 检查是否是项目成员
            if crud.project.is_member(self.db, project_id=project.id, user_id=self.current_user.id):
                # 如果要求是所有者，检查是否是项目所有者
                if require_owner and not crud.project.is_owner(self.db, project_id=project.id, user_id=self.current_user.id):
                    raise PermissionDeniedError("需要项目所有者权限")
                return asset
        
        # 如果既不是所有者，也不是项目成员，且不是超级用户
        if require_owner:
            raise PermissionDeniedError("需要资源所有者权限")
        else:
            raise PermissionDeniedError()
    
    def check_project_permission(
        self,
        project_id: int,
        require_admin: bool = False,
        require_owner: bool = False
    ) -> Project:
        """
        检查用户是否有权限访问项目
        
        Args:
            project_id: 项目ID
            require_admin: 是否要求是项目管理员
            require_owner: 是否要求是项目所有者
            
        Returns:
            Project: 项目对象
            
        Raises:
            ProjectNotFoundError: 项目不存在
            PermissionDeniedError: 没有权限访问项目
        """
        # 获取项目
        project = crud.project.get(self.db, id=project_id)
        if not project:
            raise ProjectNotFoundError()
        
        # 超级用户可以访问所有项目
        if self.check_is_superuser():
            return project
        
        # 检查是否是项目所有者
        if self.check_is_owner(project.owner_id):
            return project
        
        # 检查是否是项目成员
        if crud.project.is_member(self.db, project_id=project.id, user_id=self.current_user.id):
            # 检查是否需要管理员权限
            if require_admin and not crud.project.is_admin(self.db, project_id=project.id, user_id=self.current_user.id):
                raise PermissionDeniedError("需要项目管理员权限")
            # 检查是否需要所有者权限
            if require_owner and not crud.project.is_owner(self.db, project_id=project.id, user_id=self.current_user.id):
                raise PermissionDeniedError("需要项目所有者权限")
            return project
        
        # 如果既不是成员，也不是超级用户
        raise PermissionDeniedError("没有权限访问该项目")
