"""
数据库模型包

包含所有数据库模型的定义。
"""
# 导入所有模型，确保它们在SQLAlchemy的元数据中被注册
from .base import BaseModel
from .user import User
from .project import Project, ProjectStatus
from .asset import Asset, AssetType, AssetStatus
from .project_asset import ProjectAsset
from .video import Video, VideoStatus, VideoQuality
from .video_rendition import VideoRendition, RenditionStatus

# 导出所有模型
__all__ = [
    'BaseModel',
    'User',
    'Project',
    'ProjectStatus',
    'Asset',
    'AssetType',
    'AssetStatus',
    'ProjectAsset',
    'Video',
    'VideoStatus',
    'VideoQuality',
    'VideoRendition',
    'RenditionStatus',
]
