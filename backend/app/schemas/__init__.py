from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=100)
    email: Optional[EmailStr] = None


class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SceneIn(BaseModel):
    text: str
    duration: float = 3.0
    image_keywords: List[str] = Field(default_factory=list)
    transition: str = "fade"


class ScriptRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=200)
    style: str = "educational"
    duration: str = "30s"
    language: str = "zh"


class ScriptResponse(BaseModel):
    title: str
    scenes: List[SceneIn]
    total_duration: float
    style: str
    source: str = "mock"


class VoiceConfig(BaseModel):
    enabled: bool = False
    provider: str = "gtts"
    voice: str = "zh"
    speed: float = 1.0


class ExportConfig(BaseModel):
    resolution: str = "720p"
    fps: int = 24
    format: str = "mp4"


class VideoCreateRequest(BaseModel):
    script: ScriptResponse | Dict[str, Any]
    project_id: Optional[int] = None
    voice_config: VoiceConfig = Field(default_factory=VoiceConfig)
    export_config: ExportConfig = Field(default_factory=ExportConfig)
    background_color: str = "#0F1C2E"


class VideoOut(BaseModel):
    id: str
    title: str
    status: str
    progress: int
    message: str
    download_url: Optional[str] = None
    duration: float = 0
    error: Optional[str] = None

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    script: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    script: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    script: Dict[str, Any]
    config: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
