from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Union
from enum import Enum
from datetime import datetime

class VideoStyle(str, Enum):
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    COMMERCIAL = "commercial"
    NEWS = "news"

class VideoDuration(str, Enum):
    SHORT = "15s"
    MEDIUM = "30s"
    LONG = "60s"

class ScriptRequest(BaseModel):
    topic: str
    style: VideoStyle = VideoStyle.EDUCATIONAL
    duration: VideoDuration = VideoDuration.MEDIUM
    language: str = "zh"

class SceneData(BaseModel):
    text: str
    duration: float
    image_keywords: List[str]
    transition: str = "fade"

class ScriptResponse(BaseModel):
    title: str
    scenes: List[SceneData]
    total_duration: float
    style: VideoStyle

class VoiceConfig(BaseModel):
    provider: str = "gtts"  # "gtts" 或 "openai"
    voice: str = "zh"  # gtts: "zh", "en" 等; openai: "alloy", "echo" 等
    speed: float = 1.0
    enabled: bool = True

class TextStyle(BaseModel):
    fontFamily: str = "Arial"
    fontSize: int = 48
    fontColor: str = "#ffffff"
    position: str = "center"

class AudioConfig(BaseModel):
    background_music: Optional[str] = None
    volume: float = 1.0
    fade_in: bool = False
    fade_out: bool = False

class TransitionConfig(BaseModel):
    type: str = "fade"
    duration: float = 0.5

class ExportConfig(BaseModel):
    resolution: str = "720p"
    fps: int = 30
    format: str = "mp4"
    quality: str = "high"

from typing import Union

class VideoRequest(BaseModel):
    script: Union[ScriptResponse, Dict]  # 支持ScriptResponse对象或字典
    template_id: str = "default"
    voice_config: VoiceConfig = VoiceConfig()
    text_style: Optional[TextStyle] = None
    audio_config: Optional[AudioConfig] = None
    transition_config: Optional[List[TransitionConfig]] = None
    export_config: Optional[ExportConfig] = None
    
    @validator('template_id')
    def validate_template_id(cls, v):
        """验证模板ID格式"""
        try:
            from utils.validators import security_validator
            if not security_validator.validate_template_id(v):
                raise ValueError('Invalid template ID format')
        except ImportError:
            # 如果验证器不可用，进行基本验证
            import re
            if not re.match(r'^[a-zA-Z0-9_-]+$', v):
                raise ValueError('Invalid template ID format')
        return v
    
    @validator('script')
    def validate_script(cls, v):
        """验证和清理脚本内容"""
        try:
            from utils.validators import security_validator
            if isinstance(v, dict):
                return security_validator.validate_script_content(v)
        except ImportError:
            # 如果验证器不可用，进行基本验证
            if isinstance(v, dict) and 'title' in v:
                # 基本的长度限制
                if len(v['title']) > 200:
                    v['title'] = v['title'][:200]
        return v
    
    @validator('voice_config')
    def validate_voice_config(cls, v):
        """验证语音配置"""
        try:
            from utils.validators import security_validator
            if isinstance(v, dict):
                if not security_validator.validate_voice_config(v):
                    raise ValueError('Invalid voice configuration')
        except ImportError:
            # 基本验证
            if isinstance(v, dict):
                allowed_providers = {'gtts', 'openai', 'edge'}
                if v.get('provider') not in allowed_providers:
                    raise ValueError('Invalid voice provider')
        return v
    
    @validator('export_config')
    def validate_export_config(cls, v):
        """验证导出配置"""
        if v is None:
            return v
        try:
            from utils.validators import security_validator
            config_dict = v.dict() if hasattr(v, 'dict') else v
            if not security_validator.validate_export_config(config_dict):
                raise ValueError('Invalid export configuration')
        except ImportError:
            # 基本验证
            if isinstance(v, dict):
                allowed_resolutions = {'360p', '480p', '720p', '1080p', '1440p', '4k'}
                if v.get('resolution') not in allowed_resolutions:
                    raise ValueError('Invalid resolution')
        return v

class VideoResponse(BaseModel):
    video_id: str
    status: str
    download_url: Optional[str] = None
    preview_url: Optional[str] = None

# 新增：用户和统计相关模型
class UserStats(BaseModel):
    scripts_generated: int = 0
    videos_created: int = 0
    total_duration: float = 0.0
    last_activity: Optional[datetime] = None

class UsageQuota(BaseModel):
    daily_scripts: int = 10
    daily_videos: int = 5
    monthly_scripts: int = 100
    monthly_videos: int = 50
    used_today_scripts: int = 0
    used_today_videos: int = 0
    used_month_scripts: int = 0
    used_month_videos: int = 0

class SystemStats(BaseModel):
    total_users: int = 0
    total_scripts: int = 0
    total_videos: int = 0
    total_duration: float = 0.0
    active_users_today: int = 0