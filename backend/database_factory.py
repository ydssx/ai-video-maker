"""
数据库工厂

本产品仅支持 MySQL。历史 SQLite 回退路径已移除（DatabaseService 不存在）。
"""

import logging
from typing import Optional

from src.services.mysql_database_service import MySQLDatabaseService
from src.core.config import settings

logger = logging.getLogger(__name__)

_db_service: Optional[MySQLDatabaseService] = None


class DatabaseFactory:
    """数据库服务工厂（MySQL only）"""

    @staticmethod
    def create_database_service(database_url: str = None) -> MySQLDatabaseService:
        """
        创建 MySQL 数据库服务

        Args:
            database_url: MySQL 连接 URL；为空时使用 settings.get_database_url()

        Returns:
            MySQLDatabaseService

        Raises:
            ValueError: URL 不是 mysql 连接
        """
        if not database_url:
            database_url = settings.get_database_url()

        logger.info("初始化数据库服务，URL: %s", _mask_url(database_url))

        if not database_url.startswith("mysql"):
            raise ValueError(
                "本应用需要 MySQL。请配置 MYSQL_* 或 DATABASE_URL="
                "mysql+pymysql://user:pass@host:port/db"
            )

        return MySQLDatabaseService(database_url)

    @staticmethod
    def get_database_type(database_url: str = None) -> str:
        return "mysql"

    @staticmethod
    def validate_mysql_url(database_url: str) -> bool:
        if not database_url or not database_url.startswith("mysql+pymysql://"):
            return False
        try:
            url_parts = database_url.replace("mysql+pymysql://", "").split("/")
            if len(url_parts) < 2:
                return False
            auth_host = url_parts[0]
            database = url_parts[1].split("?")[0]
            return "@" in auth_host and bool(database)
        except Exception:
            return False


def _mask_url(url: str) -> str:
    """日志中隐藏密码"""
    try:
        if "://" not in url or "@" not in url:
            return url
        scheme, rest = url.split("://", 1)
        creds, hostpart = rest.split("@", 1)
        if ":" in creds:
            user = creds.split(":", 1)[0]
            return f"{scheme}://{user}:***@{hostpart}"
        return url
    except Exception:
        return "***"


def get_db_service() -> MySQLDatabaseService:
    """获取数据库服务实例（惰性初始化）"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseFactory.create_database_service(settings.get_database_url())
    return _db_service


def reset_db_service() -> None:
    """重置单例（测试用）"""
    global _db_service
    _db_service = None
