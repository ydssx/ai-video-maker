"""
统计信息模型

包含用户统计和系统统计的数据库模型。
"""
from datetime import date
from sqlalchemy import Column, Integer, Float, ForeignKey, Date, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel


class UserStats(BaseModel):
    """
    用户统计信息
    
    记录每个用户的使用统计
    """
    __tablename__ = "user_stats"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, default=date.today, nullable=False, index=True)
    
    # 使用统计
    scripts_generated = Column(Integer, default=0, nullable=False)
    videos_created = Column(Integer, default=0, nullable=False)
    total_duration = Column(Float, default=0.0, nullable=False)  # 总视频时长（秒）
    last_activity = Column(JSON, nullable=True)  # 记录最后活动信息
    
    # 关系
    user = relationship("User", back_populates="stats")
    
    __table_args__ = ({
        'comment': '用户每日使用统计',
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
    })


class UserQuota(BaseModel):
    """
    用户配额信息
    
    记录每个用户的使用配额
    """
    __tablename__ = "user_quotas"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # 配额设置
    daily_script_limit = Column(Integer, default=10, nullable=False)  # 每日脚本生成限制
    daily_video_limit = Column(Integer, default=5, nullable=False)    # 每日视频生成限制
    total_storage_mb = Column(Integer, default=1024, nullable=False)  # 存储空间限制(MB)
    
    # 使用情况
    scripts_used_today = Column(Integer, default=0, nullable=False)
    videos_used_today = Column(Integer, default=0, nullable=False)
    storage_used_mb = Column(Float, default=0.0, nullable=False)
    last_reset_date = Column(Date, default=date.today, nullable=False)
    
    # 关系
    user = relationship("User", back_populates="quota")
    
    __table_args__ = ({
        'comment': '用户配额和使用情况',
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
    })


class SystemStats(BaseModel):
    """
    系统统计信息
    
    记录系统整体使用情况
    """
    __tablename__ = "system_stats"
    
    date = Column(Date, default=date.today, nullable=False, index=True, unique=True)
    
    # 系统统计
    total_users = Column(Integer, default=0, nullable=False)
    active_users_today = Column(Integer, default=0, nullable=False)
    total_scripts_generated = Column(Integer, default=0, nullable=False)
    total_videos_created = Column(Integer, default=0, nullable=False)
    total_video_duration = Column(Float, default=0.0, nullable=False)  # 总视频时长（秒）
    
    # 资源使用
    total_storage_used_mb = Column(Float, default=0.0, nullable=False)
    
    __table_args__ = ({
        'comment': '系统每日统计',
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4',
    })
