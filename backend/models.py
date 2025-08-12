from pydantic import BaseModel
from typing import List, Optional
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

class VideoRequest(BaseModel):
    script: ScriptResponse
    template_id: str = "default"
    voice_config: VoiceConfig = VoiceConfig()

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