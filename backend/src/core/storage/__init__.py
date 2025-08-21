"""
存储模块

提供统一的存储接口，支持多种存储后端（本地文件系统、S3、OSS等）
"""
import os
from typing import BinaryIO, Optional, Union

from ..config import settings
from .base import StorageBackend
from .local import LocalStorage
from .s3 import S3Storage


def get_storage() -> StorageBackend:
    """
    获取存储后端实例
    
    Returns:
        StorageBackend: 存储后端实例
    """
    storage_type = settings.STORAGE_TYPE.lower()
    
    if storage_type == "s3":
        return S3Storage(
            bucket_name=settings.S3_BUCKET_NAME,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
        )
    else:  # 默认为本地存储
        upload_dir = os.path.join(settings.BASE_DIR, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        return LocalStorage(upload_dir=upload_dir)


__all__ = ["StorageBackend", "LocalStorage", "S3Storage", "get_storage"]
