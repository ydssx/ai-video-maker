"""
本地文件系统存储实现
"""
import os
import shutil
from pathlib import Path
from typing import BinaryIO, Optional, Dict, Any, Tuple

from .base import StorageBackend
from ...exceptions import StorageError


class LocalStorage(StorageBackend):
    """本地文件系统存储实现"""
    
    def __init__(self, upload_dir: str):
        """
        初始化本地存储
        
        Args:
            upload_dir: 上传文件存储目录
        """
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
    
    async def upload_fileobj(
        self,
        file_path: str,
        file_obj: BinaryIO,
        content_type: str = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """
        上传文件对象到本地文件系统
        """
        try:
            # 确保目录存在
            full_path = os.path.join(self.upload_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # 写入文件
            with open(full_path, "wb") as f:
                shutil.copyfileobj(file_obj, f)
                
        except Exception as e:
            raise StorageError(f"Failed to upload file: {str(e)}")
    
    def get_download_url(self, file_path: str, filename: str, expires_in: int = 3600) -> str:
        """
        获取文件下载URL（本地文件系统直接返回文件路径）
        """
        return f"/api/v1/assets/{file_path}/download"
    
    def delete_file(self, file_path: str) -> None:
        """
        删除文件
        """
        try:
            full_path = os.path.join(self.upload_dir, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
        except Exception as e:
            raise StorageError(f"Failed to delete file: {str(e)}")
    
    def generate_upload_url(
        self,
        file_path: str,
        content_type: str,
        file_size: int,
        metadata: Optional[Dict[str, str]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        生成上传URL（本地文件系统直接返回路径）
        """
        # 确保目录存在
        full_path = os.path.join(self.upload_dir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # 返回直接上传的URL和空字段
        return f"/api/v1/assets/upload/{file_path}", {}
    
    def get_local_path(self, file_path: str) -> str:
        """
        获取文件的本地路径
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 本地文件系统路径
        """
        return os.path.join(self.upload_dir, file_path)
