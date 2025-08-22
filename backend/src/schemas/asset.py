"""
资源模型

包含与媒体资源相关的Pydantic模型。
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator

from src.db.models.asset import AssetType, AssetStatus


class AssetBase(BaseModel):
    """资源基础模型"""
    name: str = Field(..., min_length=1, max_length=255, description="资源名称")
    description: Optional[str] = Field(None, description="资源描述")
    file_name: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件存储路径")
    file_size: int = Field(..., ge=0, description="文件大小（字节）")
    mime_type: str = Field(..., description="MIME类型")
    asset_type: AssetType = Field(..., description="资源类型")
    status: AssetStatus = Field(AssetStatus.UPLOADING, description="资源状态")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="资源元数据")
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "name": "背景图片",
                "description": "项目背景图片",
                "file_name": "background.jpg",
                "file_path": "uploads/1/background.jpg",
                "file_size": 1024000,
                "mime_type": "image/jpeg",
                "asset_type": "image",
                "status": "ready",
                "metadata": {
                    "width": 1920,
                    "height": 1080,
                    "duration": None
                }
            }
        }


class AssetCreate(AssetBase):
    """创建资源模型"""
    pass


class AssetUpdate(BaseModel):
    """更新资源模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="资源名称")
    description: Optional[str] = Field(None, description="资源描述")
    metadata: Optional[Dict[str, Any]] = Field(None, description="资源元数据")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "更新后的资源名称",
                "description": "更新后的资源描述",
                "metadata": {
                    "tags": ["background", "high_quality"]
                }
            }
        }


class AssetInDBBase(AssetBase):
    """数据库资源基础模型"""
    id: int = Field(..., description="资源ID")
    owner_id: int = Field(..., description="所有者ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config(AssetBase.Config):
        orm_mode = True
        schema_extra = {
            **AssetBase.Config.schema_extra["example"],
            "id": 1,
            "owner_id": 1,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }


class Asset(AssetInDBBase):
    """资源模型（API响应）"""
    url: Optional[HttpUrl] = Field(None, description="资源访问URL")
    
    class Config(AssetInDBBase.Config):
        schema_extra = {
            **AssetInDBBase.Config.schema_extra,
            "url": "http://example.com/uploads/1/background.jpg"
        }


class AssetInDB(AssetInDBBase):
    """数据库资源模型"""
    pass


class AssetUploadResponse(BaseModel):
    """资源上传响应模型"""
    id: int = Field(..., description="资源ID")
    upload_url: str = Field(..., description="上传URL")
    fields: Dict[str, str] = Field(..., description="上传表单字段")
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "upload_url": "https://storage.example.com/upload",
                "fields": {
                    "key": "uploads/1/background.jpg",
                    "Content-Type": "image/jpeg",
                    "x-amz-credential": "..."
                }
            }
        }


class AssetListResponse(BaseModel):
    """资源列表响应模型"""
    items: List[Asset] = Field(..., description="资源列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页记录数")
    total_pages: int = Field(..., description="总页数")
