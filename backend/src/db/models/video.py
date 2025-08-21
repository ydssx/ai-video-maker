"""
视频模型

包含视频相关的数据库模型。
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.models.base import BaseModel


class VideoStatus(str, Enum):
    """视频状态枚举"""
    DRAFT = "draft"
    RENDERING = "rendering"
    READY = "ready"
    PUBLISHED = "published"
    FAILED = "failed"


class VideoQuality(str, Enum):
    """视频质量枚举"""
    SD = "sd"
    HD = "hd"
    FULL_HD = "full_hd"
    ULTRA_HD = "4k"


class Video(BaseModel, BaseModel):
    """
    视频模型
    
    存储视频渲染和发布信息
    """
    __tablename__ = "videos"
    
    # 基本信息
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # 视频状态和元数据
    status = Column(SQLEnum(VideoStatus), default=VideoStatus.DRAFT, nullable=False)
    quality = Column(SQLEnum(VideoQuality), default=VideoQuality.HD, nullable=False)
    duration = Column(Integer, nullable=True)  # 视频时长（秒）
    
    # 文件信息
    file_path = Column(String(512), nullable=True)
    file_size = Column(Integer, nullable=True)  # 文件大小（字节）
    thumbnail_path = Column(String(512), nullable=True)
    
    # 视频元数据
    metadata = Column(JSONB, default=dict, nullable=False)
    
    # 关系
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    project = relationship("Project", back_populates="videos")
    
    renditions = relationship("VideoRendition", back_populates="video", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Video(id={self.id}, title='{self.title}', status='{self.status}')>"
    
    @property
    def url(self) -> Optional[str]:
        """
        获取视频的URL
        
        Returns:
            Optional[str]: 视频的URL，如果不存在则返回None
        """
        if not self.file_path:
            return None
        return f"/videos/{self.file_path}"
    
    @property
    def thumbnail_url(self) -> Optional[str]:
        """
        获取缩略图的URL
        
        Returns:
            Optional[str]: 缩略图的URL，如果不存在则返回None
        """
        if not self.thumbnail_path:
            return None
        return f"/thumbnails/{self.thumbnail_path}"
    
    def start_rendering(self) -> None:
        """
        开始渲染视频
        """
        if self.status == VideoStatus.DRAFT:
            self.status = VideoStatus.RENDERING
    
    def complete_rendering(self, file_path: str, file_size: int, duration: int) -> None:
        """
        完成视频渲染
        
        Args:
            file_path: 视频文件路径
            file_size: 文件大小（字节）
            duration: 视频时长（秒）
        """
        self.status = VideoStatus.READY
        self.file_path = file_path
        self.file_size = file_size
        self.duration = duration
    
    def publish(self) -> None:
        """
        发布视频
        """
        if self.status == VideoStatus.READY:
            self.status = VideoStatus.PUBLISHED
    
    def fail_rendering(self, error_message: str) -> None:
        """
        标记视频渲染失败
        
        Args:
            error_message: 错误信息
        """
        self.status = VideoStatus.FAILED
        self.metadata = {
            **self.metadata,
            "error": error_message,
            "failed_at": datetime.utcnow().isoformat()
        }
