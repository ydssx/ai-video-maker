"""
视频转码版本模型

存储同一视频的不同转码版本。
"""
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.models.base import BaseModel


class RenditionStatus(str, Enum):
    """转码状态枚举"""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VideoRendition(BaseModel, BaseModel):
    """
    视频转码版本模型
    
    存储同一视频的不同转码版本（不同分辨率、格式等）
    """
    __tablename__ = "video_renditions"
    
    # 外键
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    
    # 转码信息
    status = Column(SQLEnum(RenditionStatus), default=RenditionStatus.QUEUED, nullable=False)
    format = Column(String(20), nullable=False)  # mp4, webm 等
    resolution = Column(String(20), nullable=False)  # 例如: 1920x1080
    bitrate = Column(Integer, nullable=True)  # 比特率 (kbps)
    
    # 文件信息
    file_path = Column(String(512), nullable=True)
    file_size = Column(Integer, nullable=True)  # 文件大小（字节）
    duration = Column(Integer, nullable=True)  # 视频时长（秒）
    
    # 元数据
    metadata = Column(JSONB, default=dict, nullable=False)
    
    # 关系
    video = relationship("Video", back_populates="renditions")
    
    def __repr__(self) -> str:
        return f"<VideoRendition(id={self.id}, format='{self.format}', resolution='{self.resolution}')>"
    
    @property
    def url(self) -> Optional[str]:
        """
        获取转码后视频的URL
        
        Returns:
            Optional[str]: 视频的URL，如果不存在则返回None
        """
        if not self.file_path:
            return None
        return f"/renditions/{self.file_path}"
    
    def start_processing(self) -> None:
        """
        开始处理转码
        """
        if self.status == RenditionStatus.QUEUED:
            self.status = RenditionStatus.PROCESSING
    
    def complete_processing(self, file_path: str, file_size: int, duration: int) -> None:
        """
        完成转码处理
        
        Args:
            file_path: 转码后文件路径
            file_size: 文件大小（字节）
            duration: 视频时长（秒）
        """
        self.status = RenditionStatus.COMPLETED
        self.file_path = file_path
        self.file_size = file_size
        self.duration = duration
    
    def fail_processing(self, error_message: str) -> None:
        """
        标记转码失败
        
        Args:
            error_message: 错误信息
        """
        self.status = RenditionStatus.FAILED
        self.metadata = {
            **self.metadata,
            "error": error_message,
            "failed_at": self.updated_at.isoformat()
        }
