"""
数据库会话管理

提供SQLAlchemy会话工厂和数据库连接管理。
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import settings

# 创建SQLAlchemy引擎
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,  # 在连接前检查连接是否有效
    pool_recycle=3600,   # 连接在连接池中的最大空闲时间（秒）
)

# 会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 声明性基类
Base = declarative_base()

def get_db():
    """
    获取数据库会话
    
    Yields:
        Session: SQLAlchemy数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    初始化数据库
    
    创建所有表结构
    """
    from . import models  # noqa: F401
    
    Base.metadata.create_all(bind=engine)
    
    # 可以在这里添加初始化数据
    # db = SessionLocal()
    # try:
    #     # 初始化数据逻辑
    #     pass
    # finally:
    #     db.close()
