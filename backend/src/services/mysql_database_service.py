"""
MySQL数据库服务
使用SQLAlchemy ORM提供MySQL支持
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, ForeignKey, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.mysql import LONGTEXT
import pymysql

logger = logging.getLogger(__name__)

# 创建自定义metadata实例
custom_metadata = MetaData()

# 数据库模型基类
Base = declarative_base(metadata=custom_metadata)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    settings = Column(LONGTEXT, default='{}')
    quota_data = Column(LONGTEXT, default='{}')
    
    # 关系
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    videos = relationship("Video", back_populates="user", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="user", cascade="all, delete-orphan")
    usage_stats = relationship("UsageStat", back_populates="user", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(String(50), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    script_data = Column(LONGTEXT)
    config_data = Column(LONGTEXT)
    status = Column(String(20), default='draft')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="projects")
    videos = relationship("Video", back_populates="project", cascade="all, delete-orphan")

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(String(50), primary_key=True)
    project_id = Column(String(50), ForeignKey('projects.id'))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200))
    duration = Column(Float, default=0)
    file_path = Column(String(500))
    thumbnail_path = Column(String(500))
    status = Column(String(20), default='processing')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="videos")
    project = relationship("Project", back_populates="videos")

class Asset(Base):
    __tablename__ = 'assets'
    
    id = Column(String(50), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)
    thumbnail_path = Column(String(500))
    asset_metadata = Column(LONGTEXT, default='{}')  # 重命名为 asset_metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="assets")

class UsageStat(Base):
    __tablename__ = 'usage_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action_type = Column(String(50))
    action_data = Column(LONGTEXT)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    user = relationship("User", back_populates="usage_stats")

class SystemConfig(Base):
    __tablename__ = 'system_config'
    
    key = Column(String(100), primary_key=True)
    value = Column(LONGTEXT)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MySQLDatabaseService:
    """MySQL数据库服务"""
    
    def __init__(self, database_url: str):
        """
        初始化MySQL数据库服务
        
        Args:
            database_url: MySQL连接URL，格式如：
                mysql+pymysql://username:password@host:port/database
        """
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        
        try:
            # 创建数据库引擎
            self.engine = create_engine(
                database_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False  # 设置为True可以看到SQL语句
            )
            
            # 创建会话工厂
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # 创建所有表
            self._init_database()
            
            logger.info("MySQL数据库连接成功")
            
        except Exception as e:
            logger.error(f"MySQL数据库连接失败: {str(e)}")
            raise
    
    def _init_database(self):
        """初始化数据库表"""
        try:
            # 创建所有表
            Base.metadata.create_all(bind=self.engine)
            logger.info("MySQL数据库表初始化完成")
        except Exception as e:
            logger.error(f"数据库表初始化失败: {str(e)}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """获取数据库会话"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库操作失败: {str(e)}")
            raise
        finally:
            session.close()
    
    # 用户管理
    def create_user(self, username: str, email: str = None) -> int:
        """创建用户"""
        with self.get_session() as session:
            user = User(username=username, email=email)
            session.add(user)
            session.flush()  # 获取ID
            return user.id
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """获取用户信息"""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'created_at': user.created_at,
                    'last_login': user.last_login,
                    'settings': json.loads(user.settings) if user.settings else {},
                    'quota_data': json.loads(user.quota_data) if user.quota_data else {}
                }
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """根据用户名获取用户信息"""
        with self.get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'created_at': user.created_at,
                    'last_login': user.last_login,
                    'settings': json.loads(user.settings) if user.settings else {},
                    'quota_data': json.loads(user.quota_data) if user.quota_data else {}
                }
            return None
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """更新用户信息"""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    if key in ['settings', 'quota_data'] and isinstance(value, dict):
                        value = json.dumps(value)
                    setattr(user, key, value)
            
            return True
    
    def update_user_login_time(self, user_id: int):
        """更新用户最后登录时间"""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.last_login = datetime.utcnow()
    
    def get_user_settings(self, user_id: int) -> Dict:
        """获取用户设置"""
        user = self.get_user(user_id)
        if user and user.get('settings'):
            return user['settings']
        return {}
    
    def get_user_quota(self, user_id: int) -> Optional[Dict]:
        """获取用户配额"""
        user = self.get_user(user_id)
        if user and user.get('quota_data'):
            return user['quota_data']
        return None
    
    def update_user_quota(self, user_id: int, quota_data: Dict):
        """更新用户配额"""
        return self.update_user(user_id, quota_data=quota_data)
    
    def get_user_usage_history(self, user_id: int, days: int = 30) -> List[Dict]:
        """获取用户使用历史"""
        with self.get_session() as session:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            stats = session.query(UsageStat).filter(
                UsageStat.user_id == user_id,
                UsageStat.timestamp >= since_date
            ).order_by(UsageStat.timestamp.desc()).all()
            
            history = []
            for stat in stats:
                record = {
                    'action_type': stat.action_type,
                    'action_data': json.loads(stat.action_data) if stat.action_data else {},
                    'timestamp': stat.timestamp
                }
                history.append(record)
            
            return history
    
    def delete_user_data(self, user_id: int) -> bool:
        """删除用户相关数据"""
        with self.get_session() as session:
            try:
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    session.delete(user)  # 级联删除相关数据
                    return True
                return False
            except Exception as e:
                logger.error(f"删除用户数据失败: {str(e)}")
                return False
    
    def update_user_settings(self, user_id: int, settings: Dict):
        """更新用户设置"""
        return self.update_user(user_id, settings=settings)
    
    # 项目管理
    def create_project(self, project_id: str, user_id: int, name: str, 
                      description: str = None, script_data: Dict = None) -> bool:
        """创建项目"""
        with self.get_session() as session:
            try:
                project = Project(
                    id=project_id,
                    user_id=user_id,
                    name=name,
                    description=description,
                    script_data=json.dumps(script_data) if script_data else None
                )
                session.add(project)
                return True
            except Exception as e:
                logger.error(f"创建项目失败: {str(e)}")
                return False
    
    def get_project(self, project_id: str) -> Optional[Dict]:
        """获取项目"""
        with self.get_session() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            if project:
                return {
                    'id': project.id,
                    'user_id': project.user_id,
                    'name': project.name,
                    'description': project.description,
                    'script_data': json.loads(project.script_data) if project.script_data else None,
                    'config_data': json.loads(project.config_data) if project.config_data else None,
                    'status': project.status,
                    'created_at': project.created_at,
                    'updated_at': project.updated_at
                }
            return None
    
    def update_project(self, project_id: str, **kwargs) -> bool:
        """更新项目"""
        with self.get_session() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return False
            
            for key, value in kwargs.items():
                if hasattr(project, key):
                    if key in ['script_data', 'config_data'] and isinstance(value, dict):
                        value = json.dumps(value)
                    setattr(project, key, value)
            
            project.updated_at = datetime.utcnow()
            return True
    
    def get_user_projects(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """获取用户项目列表"""
        with self.get_session() as session:
            projects = session.query(Project).filter(
                Project.user_id == user_id
            ).order_by(Project.updated_at.desc()).limit(limit).offset(offset).all()
            
            result = []
            for project in projects:
                result.append({
                    'id': project.id,
                    'user_id': project.user_id,
                    'name': project.name,
                    'description': project.description,
                    'script_data': json.loads(project.script_data) if project.script_data else None,
                    'config_data': json.loads(project.config_data) if project.config_data else None,
                    'status': project.status,
                    'created_at': project.created_at,
                    'updated_at': project.updated_at
                })
            
            return result
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        with self.get_session() as session:
            project = session.query(Project).filter(Project.id == project_id).first()
            if project:
                session.delete(project)
                return True
            return False
    
    # 视频管理
    def create_video(self, video_id: str, project_id: str, user_id: int, 
                    title: str, duration: float = 0) -> bool:
        """创建视频记录"""
        with self.get_session() as session:
            try:
                video = Video(
                    id=video_id,
                    project_id=project_id,
                    user_id=user_id,
                    title=title,
                    duration=duration
                )
                session.add(video)
                return True
            except Exception as e:
                logger.error(f"创建视频记录失败: {str(e)}")
                return False
    
    def update_video(self, video_id: str, **kwargs) -> bool:
        """更新视频信息"""
        with self.get_session() as session:
            video = session.query(Video).filter(Video.id == video_id).first()
            if not video:
                return False
            
            for key, value in kwargs.items():
                if hasattr(video, key):
                    setattr(video, key, value)
            
            return True
    
    def get_video(self, video_id: str) -> Optional[Dict]:
        """获取视频信息"""
        with self.get_session() as session:
            video = session.query(Video).filter(Video.id == video_id).first()
            if video:
                return {
                    'id': video.id,
                    'project_id': video.project_id,
                    'user_id': video.user_id,
                    'title': video.title,
                    'duration': video.duration,
                    'file_path': video.file_path,
                    'thumbnail_path': video.thumbnail_path,
                    'status': video.status,
                    'created_at': video.created_at
                }
            return None
    
    # 素材管理
    def create_asset(self, asset_id: str, user_id: int, filename: str, 
                    file_path: str, file_type: str, file_size: int,
                    metadata: Dict = None) -> bool:
        """创建素材记录"""
        with self.get_session() as session:
            try:
                asset = Asset(
                    id=asset_id,
                    user_id=user_id,
                    filename=filename,
                    file_path=file_path,
                    file_type=file_type,
                    file_size=file_size,
                    asset_metadata=json.dumps(metadata) if metadata else '{}'  # 使用新的字段名
                )
                session.add(asset)
                return True
            except Exception as e:
                logger.error(f"创建素材记录失败: {str(e)}")
                return False
    
    def get_user_assets(self, user_id: int, file_type: str = None, 
                       limit: int = 50, offset: int = 0) -> List[Dict]:
        """获取用户素材列表"""
        with self.get_session() as session:
            query = session.query(Asset).filter(Asset.user_id == user_id)
            
            if file_type:
                query = query.filter(Asset.file_type == file_type)
            
            assets = query.order_by(Asset.created_at.desc()).limit(limit).offset(offset).all()
            
            result = []
            for asset in assets:
                result.append({
                    'id': asset.id,
                    'user_id': asset.user_id,
                    'filename': asset.filename,
                    'file_path': asset.file_path,
                    'file_type': asset.file_type,
                    'file_size': asset.file_size,
                    'thumbnail_path': asset.thumbnail_path,
                    'metadata': json.loads(asset.asset_metadata) if asset.asset_metadata else {},  # 使用新的字段名
                    'created_at': asset.created_at
                })
            
            return result
    
    def delete_asset(self, asset_id: str) -> bool:
        """删除素材"""
        with self.get_session() as session:
            asset = session.query(Asset).filter(Asset.id == asset_id).first()
            if asset:
                session.delete(asset)
                return True
            return False
    
    # 统计功能
    def log_usage(self, user_id: int, action_type: str, action_data: Dict = None):
        """记录使用统计"""
        with self.get_session() as session:
            stat = UsageStat(
                user_id=user_id,
                action_type=action_type,
                action_data=json.dumps(action_data) if action_data else None
            )
            session.add(stat)
    
    def get_user_stats(self, user_id: int, days: int = 30) -> Dict:
        """获取用户统计信息"""
        with self.get_session() as session:
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # 使用原生SQL进行分组统计
            result = session.execute(text("""
                SELECT action_type, COUNT(*) as count
                FROM usage_stats 
                WHERE user_id = :user_id AND timestamp >= :since_date
                GROUP BY action_type
            """), {'user_id': user_id, 'since_date': since_date})
            
            stats = {}
            for row in result:
                stats[row.action_type] = row.count
            
            return stats
    
    def get_system_stats(self) -> Dict:
        """获取系统统计信息"""
        with self.get_session() as session:
            stats = {}
            
            # 总用户数
            stats['total_users'] = session.query(User).count()
            
            # 总项目数
            stats['total_projects'] = session.query(Project).count()
            
            # 总视频数
            stats['total_videos'] = session.query(Video).count()
            
            # 今日活跃用户
            today = datetime.utcnow().date()
            result = session.execute(text("""
                SELECT COUNT(DISTINCT user_id) as count 
                FROM usage_stats 
                WHERE DATE(timestamp) = :today
            """), {'today': today})
            
            stats['active_users_today'] = result.scalar() or 0
            
            return stats
    
    # 系统配置
    def set_config(self, key: str, value: Any):
        """设置系统配置"""
        with self.get_session() as session:
            config = session.query(SystemConfig).filter(SystemConfig.key == key).first()
            
            if config:
                config.value = json.dumps(value) if not isinstance(value, str) else value
                config.updated_at = datetime.utcnow()
            else:
                config = SystemConfig(
                    key=key,
                    value=json.dumps(value) if not isinstance(value, str) else value
                )
                session.add(config)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取系统配置"""
        with self.get_session() as session:
            config = session.query(SystemConfig).filter(SystemConfig.key == key).first()
            if config:
                try:
                    return json.loads(config.value)
                except json.JSONDecodeError:
                    return config.value
            return default
    
    def cleanup_old_data(self, days: int = 90):
        """清理旧数据"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with self.get_session() as session:
            # 清理旧的使用统计
            deleted_count = session.query(UsageStat).filter(
                UsageStat.timestamp < cutoff_date
            ).delete()
            
            logger.info(f"清理了 {deleted_count} 条旧统计数据")
            return deleted_count
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
            return False