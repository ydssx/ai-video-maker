"""
Pydantic 模型包

包含所有请求和响应模型。
"""
from .base import BaseModel, BaseResponse
from .token import Token, TokenPayload
from .user import (
    User,
    UserInDB,
    UserCreate,
    UserUpdate,
    UserLogin,
    UserRegister,
    UserPermissions,
    UserBase,
)
from .project import (
    Project,
    ProjectCreate,
    ProjectUpdate,
    ProjectInDB,
    ProjectInDBBase,
    ProjectWithAssets,
    ProjectListResponse,
)
from .asset import (
    Asset,
    AssetCreate,
    AssetUpdate,
    AssetInDB,
    AssetInDBBase,
    AssetUploadResponse,
    AssetListResponse,
    AssetBase,
)
from .video import (
    Video,
    VideoBase,
    VideoCreate,
    VideoUpdate,
    VideoInDB,
    VideoInDBBase,
    VideoWithRenditions,
    VideoListResponse,
    VideoRendition,
    VideoRenditionBase,
    VideoRenditionInDB,
)
from .api_models import (
    ScriptRequest,
    ScriptResponse,
    SceneData,
    VideoStyle,
    VideoDuration,
    VideoRequest,
    VideoResponse,
    VoiceConfig,
    TextStyle,
    AudioConfig,
    TransitionConfig,
    ExportConfig,
)

__all__ = [
    # Base
    'BaseModel',
    'BaseResponse',
    
    # Token
    'Token',
    'TokenPayload',
    
    # User
    'User',
    'UserBase',
    'UserInDB',
    'UserCreate',
    'UserUpdate',
    'UserLogin',
    'UserRegister',
    'UserPermissions',
    
    # Project
    'Project',
    'ProjectCreate',
    'ProjectUpdate',
    'ProjectInDB',
    'ProjectInDBBase',
    'ProjectWithAssets',
    'ProjectListResponse',
    
    # Asset
    'Asset',
    'AssetBase',
    'AssetCreate',
    'AssetUpdate',
    'AssetInDB',
    'AssetInDBBase',
    'AssetUploadResponse',
    'AssetListResponse',
    
    # Video
    'Video',
    'VideoBase',
    'VideoCreate',
    'VideoUpdate',
    'VideoInDB',
    'VideoInDBBase',
    'VideoWithRenditions',
    'VideoListResponse',
    'VideoRendition',
    'VideoRenditionBase',
    'VideoRenditionInDB',

    # Script / video API
    'ScriptRequest',
    'ScriptResponse',
    'SceneData',
    'VideoStyle',
    'VideoDuration',
    'VideoRequest',
    'VideoResponse',
    'VoiceConfig',
    'TextStyle',
    'AudioConfig',
    'TransitionConfig',
    'ExportConfig',
]
