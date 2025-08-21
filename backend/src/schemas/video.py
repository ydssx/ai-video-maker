"""
视频模型

包含与视频相关的Pydantic模型。
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, HttpUrl, validator

from db.models.video import VideoStatus, VideoQuality


class VideoBase(BaseModel):
    """视频基础模型"""
    title: str = Field(..., min_length=1, max_length=255, description="视频标题")
    description: Optional[str] = Field(None, description="视频描述")
    status: VideoStatus = Field(VideoStatus.DRAFT, description="视频状态")
    quality: VideoQuality = Field(VideoQuality.HD, description="视频质量")
    duration: Optional[int] = Field(None, ge=0, description="视频时长（秒）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="视频元数据")
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "title": "我的第一个视频",
                "description": "这是一个示例视频",
                "status": "draft",
                "quality": "hd",
                "duration": 120,
                "metadata": {
                    "aspect_ratio": "16:9",
                    "fps": 30,
                    "has_audio": True
                }
            }
        }


class VideoCreate(VideoBase):
    """创建视频模型"""
    project_id: int = Field(..., description="所属项目ID")
    
    class Config(VideoBase.Config):
        schema_extra = {
            **VideoBase.Config.schema_extra["example"],
            "project_id": 1
        }


class VideoUpdate(BaseModel):
    """更新视频模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="视频标题")
    description: Optional[str] = Field(None, description="视频描述")
    status: Optional[VideoStatus] = Field(None, description="视频状态")
    quality: Optional[VideoQuality] = Field(None, description="视频质量")
    metadata: Optional[Dict[str, Any]] = Field(None, description="视频元数据")
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "title": "更新后的视频标题",
                "description": "更新后的视频描述",
                "status": "rendering",
                "quality": "full_hd",
                "metadata": {
                    "tags": ["tutorial", "introduction"]
                }
            }
        }


class VideoInDBBase(VideoBase):
    """数据库视频基础模型"""
    id: int = Field(..., description="视频ID")
    project_id: int = Field(..., description="所属项目ID")
    file_path: Optional[str] = Field(None, description="视频文件路径")
    file_size: Optional[int] = Field(None, ge=0, description="文件大小（字节）")
    thumbnail_path: Optional[str] = Field(None, description="缩略图路径")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config(VideoBase.Config):
        orm_mode = True
        schema_extra = {
            **VideoBase.Config.schema_extra["example"],
            "id": 1,
            "project_id": 1,
            "file_path": "videos/1/final.mp4",
            "file_size": 10485760,
            "thumbnail_path": "thumbnails/1/thumbnail.jpg",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }


class Video(VideoInDBBase):
    """视频模型（API响应）"""
    url: Optional[HttpUrl] = Field(None, description="视频访问URL")
    thumbnail_url: Optional[HttpUrl] = Field(None, description="缩略图访问URL")
    
    class Config(VideoInDBBase.Config):
        schema_extra = {
            **VideoInDBBase.Config.schema_extra,
            "url": "http://example.com/videos/1/final.mp4",
            "thumbnail_url": "http://example.com/thumbnails/1/thumbnail.jpg"
        }


class VideoInDB(VideoInDBBase):
    """数据库视频模型"""
    pass


class VideoRenditionBase(BaseModel):
    """视频转码版本基础模型"""
    format: str = Field(..., description="视频格式（如mp4, webm）")
    resolution: str = Field(..., description="分辨率（如1920x1080）")
    bitrate: Optional[int] = Field(None, description="比特率（kbps）")
    status: str = Field("queued", description="转码状态")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="转码元数据")
    
    class Config:
        schema_extra = {
            "example": {
                "format": "mp4",
                "resolution": "1920x1080",
                "bitrate": 5000,
                "status": "completed",
                "metadata": {
                    "codec": "h264",
                    "profile": "high"
                }
            }
        }


class VideoRenditionInDB(VideoRenditionBase):
    """数据库视频转码版本模型"""
    id: int = Field(..., description="转码版本ID")
    video_id: int = Field(..., description="所属视频ID")
    file_path: Optional[str] = Field(None, description="文件路径")
    file_size: Optional[int] = Field(None, ge=0, description="文件大小（字节）")
    duration: Optional[int] = Field(None, ge=0, description="视频时长（秒）")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config(VideoRenditionBase.Config):
        orm_mode = True
        schema_extra = {
            **VideoRenditionBase.Config.schema_extra["example"],
            "id": 1,
            "video_id": 1,
            "file_path": "renditions/1/1080p.mp4",
            "file_size": 5242880,
            "duration": 120,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }


class VideoRendition(VideoRenditionInDB):
    """视频转码版本模型（API响应）"""
    url: Optional[HttpUrl] = Field(None, description="转码后视频访问URL")
    
    class Config(VideoRenditionInDB.Config):
        schema_extra = {
            **VideoRenditionInDB.Config.schema_extra,
            "url": "http://example.com/renditions/1/1080p.mp4"
        }


class VideoWithRenditions(Video):
    """包含转码版本的视频模型"""
    renditions: List[VideoRendition] = Field(default_factory=list, description="转码版本列表")
    
    class Config(Video.Config):
        schema_extra = {
            **Video.Config.schema_extra,
            "renditions": [
                {
                    "id": 1,
                    "video_id": 1,
                    "format": "mp4",
                    "resolution": "1920x1080",
                    "bitrate": 5000,
                    "status": "completed",
                    "file_path": "renditions/1/1080p.mp4",
                    "file_size": 5242880,
                    "duration": 120,
                    "metadata": {"codec": "h264"},
                    "url": "http://example.com/renditions/1/1080p.mp4",
                    "created_at": "2023-01-01T00:00:00",
                    "updated_at": "2023-01-01T00:00:00"
                }
            ]
        }


class VideoListResponse(BaseModel):
    """视频列表响应模型"""
    items: List[Video] = Field(..., description="视频列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页记录数")
    total_pages: int = Field(..., description="总页数")
