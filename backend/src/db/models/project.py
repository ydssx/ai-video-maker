"""
项目模型

包含视频项目相关的数据库模型。
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.models.base import BaseModel


class ProjectStatus(str, Enum):
    """项目状态枚举"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(BaseModel, BaseModel):
    """
    视频项目模型
    
    存储用户创建的视频项目信息
    """
    __tablename__ = "projects"
    
    # 基本信息
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # 项目状态
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT, nullable=False)
    
    # 项目配置
    config = Column(JSONB, default=dict, nullable=False)
    
    # 时间信息
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # 关系
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="projects")
    
    videos = relationship("Video", back_populates="project", cascade="all, delete-orphan")
    assets = relationship("ProjectAsset", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}')>"
    
    def start(self) -> None:
        """
        开始项目
        """
        if self.status == ProjectStatus.DRAFT:
            self.status = ProjectStatus.IN_PROGRESS
            self.started_at = datetime.utcnow()
    
    def complete(self) -> None:
        """
        完成项目
        """
        if self.status == ProjectStatus.IN_PROGRESS:
            self.status = ProjectStatus.COMPLETED
            self.completed_at = datetime.utcnow()
    
    def archive(self) -> None:
        """
        归档项目
        """
        self.status = ProjectStatus.ARCHIVED
    
    def add_asset(self, asset_id: int, asset_type: str, **kwargs) -> 'ProjectAsset':
        """
        添加资源到项目
        
        Args:
            asset_id: 资源ID
            asset_type: 资源类型
            **kwargs: 其他属性
            
        Returns:
            ProjectAsset: 创建的项目资源关联
        """
        from db.models import ProjectAsset
        return ProjectAsset(
            project_id=self.id,
            asset_id=asset_id,
            asset_type=asset_type,
            **kwargs
        )
