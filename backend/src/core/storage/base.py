"""
存储后端基类

定义存储后端的标准接口
"""
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional, Tuple, Dict, Any


class StorageBackend(ABC):
    """存储后端抽象基类"""
    
    @abstractmethod
    async def upload_fileobj(
        self,
        file_path: str,
        file_obj: BinaryIO,
        content_type: str = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """
        上传文件对象到存储
        
        Args:
            file_path: 文件在存储中的路径
            file_obj: 文件对象
            content_type: 文件类型
            metadata: 文件元数据
            
        Raises:
            StorageError: 上传失败时抛出
        """
        pass
    
    @abstractmethod
    def get_download_url(self, file_path: str, filename: str, expires_in: int = 3600) -> str:
        """
        获取文件下载URL
        
        Args:
            file_path: 文件路径
            filename: 下载时显示的文件名
            expires_in: URL过期时间（秒）
            
        Returns:
            str: 下载URL
            
        Raises:
            StorageError: 获取URL失败时抛出
        """
        pass
    
    @abstractmethod
    def delete_file(self, file_path: str) -> None:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Raises:
            StorageError: 删除失败时抛出
        """
        pass
    
    @abstractmethod
    def generate_upload_url(
        self,
        file_path: str,
        content_type: str,
        file_size: int,
        metadata: Optional[Dict[str, str]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        生成预签名上传URL
        
        Args:
            file_path: 文件路径
            content_type: 文件类型
            file_size: 文件大小（字节）
            metadata: 文件元数据
            
        Returns:
            Tuple[str, Dict[str, Any]]: (上传URL, 额外字段)
            
        Raises:
            StorageError: 生成URL失败时抛出
        """
        pass
    
    def generate_file_path(self, filename: str, prefix: str = "") -> str:
        """
        生成唯一的文件路径
        
        Args:
            filename: 原始文件名
            prefix: 路径前缀
            
        Returns:
            str: 生成的文件路径
        """
        import os
        import uuid
        from datetime import datetime
        
        # 提取文件扩展名
        _, ext = os.path.splitext(filename)
        # 生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}{ext.lower()}"
        
        # 添加日期目录
        date_str = datetime.utcnow().strftime("%Y/%m/%d")
        
        # 组合完整路径
        if prefix:
            return f"{prefix.rstrip('/')}/{date_str}/{unique_filename}"
        return f"{date_str}/{unique_filename}"
