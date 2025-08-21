"""
项目资源关联模型

管理项目和资源之间的多对多关系。
"""
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.models.base import BaseModel


class ProjectAsset(BaseModel, BaseModel):
    """
    项目资源关联模型
    
    关联项目和资源，并存储关联的元数据
    """
    __tablename__ = "project_assets"
    
    # 外键
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    
    # 关联类型和元数据
    role = Column(String(50), nullable=True)  # 例如: 'thumbnail', 'background', 'audio_track'
    metadata_ = Column("metadata", JSONB, default=dict, nullable=False)
    
    # 关系
    project = relationship("Project", back_populates="assets")
    asset = relationship("Asset", back_populates="project_assets")
    
    def __repr__(self) -> str:
        return f"<ProjectAsset(project_id={self.project_id}, asset_id={self.asset_id}, role='{self.role}')>"
    
    def update_metadata(self, **kwargs) -> None:
        """
        更新关联元数据
        
        Args:
            **kwargs: 要更新的元数据键值对
        """
        if not self.metadata_:
            self.metadata_ = {}
        self.metadata_.update(kwargs)
