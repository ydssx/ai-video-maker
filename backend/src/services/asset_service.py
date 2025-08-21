"""
资源服务

处理资源相关的业务逻辑
"""
import os
from typing import BinaryIO, List, Optional, Tuple, Dict, Any

from fastapi import UploadFile, status
from sqlalchemy.orm import Session

from core.storage import get_storage
from core.exceptions import (
    ValidationError,
    StorageError,
    AssetNotFoundError,
    PermissionDeniedError
)
from db import crud, models
from db.models import User, Asset, AssetType, AssetStatus
from .permission_service import PermissionService


class AssetService:
    """资源服务"""
    
    def __init__(self, db: Session, current_user: User):
        """
        初始化资源服务
        
        Args:
            db: 数据库会话
            current_user: 当前用户
        """
        self.db = db
        self.current_user = current_user
        self.permission_service = PermissionService(db, current_user)
        self.storage = get_storage()
    
    def _get_asset_type(self, filename: str) -> AssetType:
        """
        根据文件名获取资源类型
        
        Args:
            filename: 文件名
            
        Returns:
            AssetType: 资源类型
        """
        _, ext = os.path.splitext(filename.lower())
        
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
            return AssetType.IMAGE
        elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']:
            return AssetType.VIDEO
        elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
            return AssetType.AUDIO
        elif ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']:
            return AssetType.DOCUMENT
        else:
            return AssetType.OTHER
    
    async def upload_asset(
        self,
        file: UploadFile,
        project_id: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> models.Asset:
        """
        上传资源文件
        
        Args:
            file: 上传的文件
            project_id: 关联的项目ID（可选）
            metadata: 文件元数据（可选）
            
        Returns:
            models.Asset: 创建的资源对象
            
        Raises:
            ValidationError: 文件验证失败
            StorageError: 存储操作失败
        """
        # 验证文件大小
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise ValidationError("文件大小不能超过10MB")
        
        # 检查项目权限
        if project_id is not None:
            self.permission_service.check_project_permission(project_id)
        
        # 生成存储路径
        file_path = self.storage.generate_file_path(
            file.filename,
            prefix=f"uploads/{self.current_user.id}"
        )
        
        # 上传文件
        try:
            # 重置文件指针
            await file.seek(0)
            await self.storage.upload_fileobj(
                file_path=file_path,
                file_obj=file.file,
                content_type=file.content_type,
                metadata=metadata or {}
            )
        except Exception as e:
            raise StorageError(f"文件上传失败: {str(e)}")
        
        # 创建资源记录
        asset_in = {
            "name": file.filename,
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "file_size": len(file_content),
            "mime_type": file.content_type or "application/octet-stream",
            "asset_type": self._get_asset_type(file.filename),
            "status": AssetStatus.READY,
            "owner_id": self.current_user.id,
            "project_id": project_id,
            "metadata": metadata or {}
        }
        
        return crud.asset.create(self.db, obj_in=asset_in)
    
    def generate_upload_url(
        self,
        filename: str,
        content_type: str,
        file_size: int,
        project_id: Optional[int] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> Tuple[models.Asset, str, Dict[str, Any]]:
        """
        生成预签名上传URL
        
        Args:
            filename: 文件名
            content_type: 文件类型
            file_size: 文件大小（字节）
            project_id: 关联的项目ID（可选）
            metadata: 文件元数据（可选）
            
        Returns:
            Tuple[models.Asset, str, Dict[str, Any]]: (资源对象, 上传URL, 额外字段)
            
        Raises:
            ValidationError: 参数验证失败
        """
        # 验证文件大小
        if file_size > 100 * 1024 * 1024:  # 100MB
            raise ValidationError("文件大小不能超过100MB")
        
        # 检查项目权限
        if project_id is not None:
            self.permission_service.check_project_permission(project_id)
        
        # 生成存储路径
        file_path = self.storage.generate_file_path(
            filename,
            prefix=f"uploads/{self.current_user.id}"
        )
        
        # 创建资源记录（状态为上传中）
        asset_in = {
            "name": filename,
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "file_size": file_size,
            "mime_type": content_type,
            "asset_type": self._get_asset_type(filename),
            "status": AssetStatus.UPLOADING,
            "owner_id": self.current_user.id,
            "project_id": project_id,
            "metadata": metadata or {}
        }
        
        asset = crud.asset.create(self.db, obj_in=asset_in)
        
        # 生成预签名URL
        try:
            upload_url, fields = self.storage.generate_upload_url(
                file_path=file_path,
                content_type=content_type,
                file_size=file_size,
                metadata={"asset_id": str(asset.id), **(metadata or {})}
            )
            
            return asset, upload_url, fields
            
        except Exception as e:
            # 如果生成URL失败，删除创建的资源记录
            crud.asset.remove(self.db, id=asset.id)
            raise StorageError(f"生成上传URL失败: {str(e)}")
    
    def get_asset(self, asset_id: int) -> models.Asset:
        """
        获取资源详情
        
        Args:
            asset_id: 资源ID
            
        Returns:
            models.Asset: 资源对象
            
        Raises:
            AssetNotFoundError: 资源不存在
            PermissionDeniedError: 没有权限访问资源
        """
        return self.permission_service.check_asset_permission(asset_id)
    
    def get_download_url(self, asset_id: int, filename: str = None) -> str:
        """
        获取资源下载URL
        
        Args:
            asset_id: 资源ID
            filename: 下载时显示的文件名（可选）
            
        Returns:
            str: 下载URL
            
        Raises:
            AssetNotFoundError: 资源不存在
            PermissionDeniedError: 没有权限访问资源
            StorageError: 获取下载URL失败
        """
        asset = self.permission_service.check_asset_permission(asset_id)
        
        try:
            return self.storage.get_download_url(
                file_path=asset.file_path,
                filename=filename or asset.name
            )
        except Exception as e:
            raise StorageError(f"获取下载URL失败: {str(e)}")
    
    def list_assets(
        self,
        project_id: Optional[int] = None,
        asset_type: Optional[AssetType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[models.Asset], int]:
        """
        获取资源列表
        
        Args:
            project_id: 项目ID（可选）
            asset_type: 资源类型（可选）
            skip: 跳过的记录数
            limit: 返回的最大记录数
            
        Returns:
            Tuple[List[models.Asset], int]: (资源列表, 总记录数)
        """
        # 检查项目权限
        if project_id is not None:
            self.permission_service.check_project_permission(project_id)
            
            # 如果是项目成员，可以查看项目中的所有资源
            if self.permission_service.check_is_superuser() or \
               crud.project.is_member(self.db, project_id=project_id, user_id=self.current_user.id):
                return crud.asset.get_by_project(
                    self.db,
                    project_id=project_id,
                    asset_type=asset_type,
                    skip=skip,
                    limit=limit
                )
        
        # 否则只返回用户自己的资源
        return crud.asset.get_multi_by_owner(
            self.db,
            owner_id=self.current_user.id,
            project_id=project_id,
            asset_type=asset_type,
            skip=skip,
            limit=limit
        )
    
    def update_asset(
        self,
        asset_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> models.Asset:
        """
        更新资源信息
        
        Args:
            asset_id: 资源ID
            name: 新名称（可选）
            description: 新描述（可选）
            metadata: 新元数据（可选）
            
        Returns:
            models.Asset: 更新后的资源对象
            
        Raises:
            AssetNotFoundError: 资源不存在
            PermissionDeniedError: 没有权限更新资源
        """
        asset = self.permission_service.check_asset_permission(asset_id, require_owner=True)
        
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if metadata is not None:
            update_data["metadata"] = {**(asset.metadata or {}), **metadata}
        
        if not update_data:
            return asset
            
        return crud.asset.update(self.db, db_obj=asset, obj_in=update_data)
    
    def delete_asset(self, asset_id: int) -> models.Asset:
        """
        删除资源
        
        Args:
            asset_id: 资源ID
            
        Returns:
            models.Asset: 删除的资源对象
            
        Raises:
            AssetNotFoundError: 资源不存在
            PermissionDeniedError: 没有权限删除资源
            StorageError: 删除文件失败
        """
        asset = self.permission_service.check_asset_permission(asset_id, require_owner=True)
        
        # 删除存储中的文件
        try:
            self.storage.delete_file(asset.file_path)
        except Exception as e:
            # 记录错误但继续删除数据库记录
            print(f"删除文件失败: {str(e)}")
        
        # 删除数据库记录
        return crud.asset.remove(self.db, id=asset_id)
    
    def mark_asset_ready(self, asset_id: int) -> models.Asset:
        """
        标记资源为就绪状态
        
        Args:
            asset_id: 资源ID
            
        Returns:
            models.Asset: 更新后的资源对象
            
        Raises:
            AssetNotFoundError: 资源不存在
            PermissionDeniedError: 没有权限更新资源
        """
        asset = self.permission_service.check_asset_permission(asset_id, require_owner=True)
        
        if asset.status != AssetStatus.READY:
            return crud.asset.update(
                self.db,
                db_obj=asset,
                obj_in={"status": AssetStatus.READY}
            )
        return asset
    
    def mark_asset_error(
        self,
        asset_id: int,
        error_message: str,
        error_details: Optional[Dict[str, Any]] = None
    ) -> models.Asset:
        """
        标记资源为错误状态
        
        Args:
            asset_id: 资源ID
            error_message: 错误信息
            error_details: 错误详情（可选）
            
        Returns:
            models.Asset: 更新后的资源对象
            
        Raises:
            AssetNotFoundError: 资源不存在
            PermissionDeniedError: 没有权限更新资源
        """
        asset = self.permission_service.check_asset_permission(asset_id, require_owner=True)
        
        metadata = {
            "error": error_message,
            "error_details": error_details or {},
            "error_at": "now"  # 将在模型中处理为当前时间
        }
        
        return crud.asset.update(
            self.db,
            db_obj=asset,
            obj_in={
                "status": AssetStatus.ERROR,
                "metadata": {**(asset.metadata or {}), **metadata}
            }
        )
