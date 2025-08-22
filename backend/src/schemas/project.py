"""
项目模型

包含与项目相关的Pydantic模型。
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

from src.db.models.project import ProjectStatus


class ProjectBase(BaseModel):
    """项目基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    status: ProjectStatus = Field(ProjectStatus.DRAFT, description="项目状态")
    config: Dict[str, Any] = Field(default_factory=dict, description="项目配置")
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "name": "我的第一个视频项目",
                "description": "这是一个示例项目",
                "status": "draft",
                "config": {
                    "theme": "modern",
                    "resolution": "1920x1080"
                }
            }
        }


class ProjectCreate(ProjectBase):
    """创建项目模型"""
    pass


class ProjectUpdate(BaseModel):
    """更新项目模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    status: Optional[ProjectStatus] = Field(None, description="项目状态")
    config: Optional[Dict[str, Any]] = Field(None, description="项目配置")
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "name": "更新后的项目名称",
                "description": "更新后的项目描述",
                "status": "in_progress",
                "config": {
                    "theme": "updated_theme",
                    "resolution": "1280x720"
                }
            }
        }


class ProjectInDBBase(ProjectBase):
    """数据库项目基础模型"""
    id: int = Field(..., description="项目ID")
    owner_id: int = Field(..., description="所有者ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config(ProjectBase.Config):
        orm_mode = True
        schema_extra = {
            **ProjectBase.Config.schema_extra["example"],
            "id": 1,
            "owner_id": 1,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }


class Project(ProjectInDBBase):
    """项目模型（API响应）"""
    pass


class ProjectInDB(ProjectInDBBase):
    """数据库项目模型"""
    pass


class ProjectWithAssets(Project):
    """包含资源的项目模型"""
    assets: List[Dict[str, Any]] = Field(default_factory=list, description="项目资源列表")
    
    class Config(Project.Config):
        schema_extra = {
            **Project.Config.schema_extra,
            "assets": [
                {
                    "id": 1,
                    "name": "background.jpg",
                    "type": "image",
                    "url": "/assets/1/background.jpg"
                }
            ]
        }


class ProjectListResponse(BaseModel):
    """项目列表响应模型"""
    items: List[Project] = Field(..., description="项目列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页记录数")
    total_pages: int = Field(..., description="总页数")
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "id": 1,
                        "name": "项目1",
                        "description": "第一个项目",
                        "status": "draft",
                        "config": {},
                        "owner_id": 1,
                        "created_at": "2023-01-01T00:00:00",
                        "updated_at": "2023-01-01T00:00:00"
                    }
                ],
                "total": 1,
                "page": 1,
                "size": 10,
                "total_pages": 1
            }
        }
