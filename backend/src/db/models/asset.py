"""
资源模型

包含用户上传的媒体资源相关的数据库模型。
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.models.base import BaseModel


class AssetType(str, Enum):
    """资源类型枚举"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    OTHER = "other"


class AssetStatus(str, Enum):
    """资源状态枚举"""
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class Asset(BaseModel, BaseModel):
    """
    资源模型
    
    存储用户上传的媒体资源信息
    """
    __tablename__ = "assets"
    
    # 基本信息
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)  # 文件大小（字节）
    mime_type = Column(String(100), nullable=False)
    
    # 资源类型和状态
    asset_type = Column(SQLEnum(AssetType), nullable=False)
    status = Column(SQLEnum(AssetStatus), default=AssetStatus.UPLOADING, nullable=False)
    
    # 元数据
    metadata_ = Column("metadata", JSONB, default=dict, nullable=False)
    
    # 关系
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="assets")
    
    project_assets = relationship("ProjectAsset", back_populates="asset", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Asset(id={self.id}, name='{self.name}', type='{self.asset_type}')>"
    
    @property
    def url(self) -> str:
        """
        获取资源的URL
        
        Returns:
            str: 资源的URL
        """
        # 这里应该根据实际的文件存储服务生成URL
        return f"/assets/{self.file_path}"
    
    def update_metadata(self, **kwargs) -> None:
        """
        更新资源元数据
        
        Args:
            **kwargs: 要更新的元数据键值对
        """
        if not self.metadata_:
            self.metadata_ = {}
        self.metadata_.update(kwargs)
    
    def mark_as_ready(self) -> None:
        """
        标记资源为就绪状态
        """
        self.status = AssetStatus.READY
    
    def mark_as_error(self, error_message: str) -> None:
        """
        标记资源为错误状态
        
        Args:
            error_message: 错误信息
        """
        self.status = AssetStatus.ERROR
        self.metadata_ = {
            **self.metadata_,
            "error": error_message,
            "error_at": datetime.utcnow().isoformat()
        }
