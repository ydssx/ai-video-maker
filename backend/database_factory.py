"""
数据库工厂类
根据配置自动选择SQLite或MySQL数据库服务
"""

import os
import logging
from typing import Union
from src.services.mysql_database_service import MySQLDatabaseService
from src.core.config import settings

logger = logging.getLogger(__name__)

class DatabaseFactory:
    """数据库服务工厂"""
    
    @staticmethod
    def create_database_service(database_url: str = None) -> Union[ MySQLDatabaseService]:
        """
        根据数据库URL创建相应的数据库服务
        
        Args:
            database_url: 数据库连接URL
                - SQLite: sqlite:///path/to/database.db 或 data/app.db
                - MySQL: mysql+pymysql://user:password@host:port/database
        
        Returns:
            数据库服务实例
        """
        if not database_url:
            database_url = os.getenv("DATABASE_URL", "sqlite:///data/app.db")
        
        logger.info(f"初始化数据库服务，URL: {database_url}")
        
        try:
            if database_url.startswith("mysql"):
                # MySQL数据库
                logger.info("使用MySQL数据库服务")
                return MySQLDatabaseService(database_url)
            else:
                # SQLite数据库（默认）
                logger.info("使用SQLite数据库服务")
                # 处理SQLite URL格式
                if database_url.startswith("sqlite:///"):
                    db_path = database_url.replace("sqlite:///", "")
                else:
                    db_path = database_url
                
                return DatabaseService(db_path)
                
        except Exception as e:
            logger.error(f"数据库服务初始化失败: {str(e)}")
            # 回退到SQLite
            logger.info("回退到SQLite数据库")
            return DatabaseService("data/app.db")
    
    @staticmethod
    def get_database_type(database_url: str = None) -> str:
        """
        获取数据库类型
        
        Args:
            database_url: 数据库连接URL
            
        Returns:
            数据库类型: 'mysql' 或 'sqlite'
        """
        if not database_url:
            database_url = os.getenv("DATABASE_URL", "sqlite:///data/app.db")
        
        if database_url.startswith("mysql"):
            return "mysql"
        else:
            return "sqlite"
    
    @staticmethod
    def validate_mysql_url(database_url: str) -> bool:
        """
        验证MySQL连接URL格式
        
        Args:
            database_url: MySQL连接URL
            
        Returns:
            是否有效
        """
        if not database_url.startswith("mysql+pymysql://"):
            return False
        
        try:
            # 基本格式检查
            # mysql+pymysql://username:password@host:port/database
            url_parts = database_url.replace("mysql+pymysql://", "").split("/")
            if len(url_parts) < 2:
                return False
            
            auth_host = url_parts[0]
            database = url_parts[1]
            
            if "@" not in auth_host or not database:
                return False
            
            return True
            
        except Exception:
            return False

# 创建全局数据库服务实例
db_service = DatabaseFactory.create_database_service(settings.get_mysql_url())

def get_db_service():
    """获取数据库服务实例"""
    return db_service