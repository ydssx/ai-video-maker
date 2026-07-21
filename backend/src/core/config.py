from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
from typing import List, Optional, Any, Union
import json
import os


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    app_name: str = "AI Video Maker API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # 数据库配置（产品以 MySQL 为准；空字符串表示使用 MYSQL_* 构建）
    database_url: str = ""
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # MySQL配置
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "123456"
    mysql_database: str = "ai_video_maker"
    mysql_charset: str = "utf8mb4"

    # Redis配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    # Celery 配置
    celery_enabled: bool = True
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None

    # JWT配置（统一使用 secret_key / algorithm）
    secret_key: str = "your-secret-key-please-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7天
    refresh_token_expire_days: int = 30  # 30天

    # AI服务配置
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 1500
    openai_temperature: float = 0.7

    # Gemini API配置
    gemini_api_key: str = ""

    # Unsplash配置
    unsplash_access_key: str = ""

    # 文件存储配置
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    upload_path: str = "data/uploads"
    output_path: str = "data/output"
    temp_path: str = "data/temp"
    cache_path: str = "cache"

    # 云存储配置
    storage_type: str = "local"  # local, aliyun_oss, aws_s3, tencent_cos, qiniu

    # 阿里云OSS配置
    aliyun_access_key: str = ""
    aliyun_secret_key: str = ""
    aliyun_oss_bucket: str = ""
    aliyun_oss_endpoint: str = ""
    aliyun_oss_region: str = "oss-cn-hangzhou"

    # CORS配置
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    # 限流配置
    rate_limit_enabled: bool = True
    default_rate_limit: int = 100  # 每分钟请求数
    video_create_rate_limit: int = 5
    script_generate_rate_limit: int = 10
    file_upload_rate_limit: int = 20

    # 日志配置
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    log_max_size: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5

    # 视频处理配置
    max_video_duration: int = 300  # 5分钟
    default_video_resolution: str = "720p"
    default_video_fps: int = 30
    default_video_format: str = "mp4"

    # 监控配置
    metrics_enabled: bool = True
    health_check_enabled: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """解析CORS源列表：支持 JSON 数组、逗号分隔字符串"""
        if v is None:
            return ["http://localhost:3000"]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            text = v.strip()
            if not text:
                return ["http://localhost:3000"]
            if text.startswith("["):
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, list):
                        return [str(origin).strip() for origin in parsed]
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in text.split(",") if origin.strip()]
        return v

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v: str) -> str:
        if v and v == "your_openai_api_key_here":
            return ""
        return v

    @field_validator("unsplash_access_key")
    @classmethod
    def validate_unsplash_key(cls, v: str) -> str:
        if v and v == "your_unsplash_key_here":
            return ""
        return v

    @model_validator(mode="after")
    def validate_production_secret(self) -> "Settings":
        if (
            self.environment.lower() in {"production", "prod"}
            and self.secret_key
            in {
                "your-secret-key-please-change-this-in-production",
                "your-secret-key-change-in-production",
                "your_secret_key_here",
            }
        ):
            raise ValueError("SECRET_KEY must be changed in production")
        return self

    @property
    def is_development(self) -> bool:
        return self.environment.lower() in ["development", "dev"]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in ["production", "prod"]

    @property
    def has_openai_key(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key.strip())

    @property
    def has_unsplash_key(self) -> bool:
        return bool(self.unsplash_access_key and self.unsplash_access_key.strip())

    @property
    def has_aliyun_oss(self) -> bool:
        return bool(
            self.aliyun_access_key
            and self.aliyun_secret_key
            and self.aliyun_oss_bucket
            and self.aliyun_oss_endpoint
        )

    @property
    def is_cloud_storage(self) -> bool:
        return self.storage_type != "local"

    @property
    def has_redis(self) -> bool:
        return bool(self.redis_host)

    @property
    def get_redis_url(self) -> str:
        password_part = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{password_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def get_celery_broker(self) -> str:
        return self.celery_broker_url or self.get_redis_url

    @property
    def get_celery_backend(self) -> str:
        return self.celery_result_backend or self.get_redis_url

    def get_mysql_url(self) -> str:
        """构建MySQL连接URL"""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            f"?charset={self.mysql_charset}"
        )

    def get_database_url(self) -> str:
        """获取数据库URL（始终返回 MySQL）"""
        if self.database_url and self.database_url.startswith("mysql"):
            return self.database_url
        return self.get_mysql_url()

    @property
    def is_mysql(self) -> bool:
        return True

    def create_directories(self):
        """创建必要的目录"""
        directories = [
            self.upload_path,
            self.output_path,
            self.temp_path,
            self.cache_path,
            os.path.dirname(self.log_file) if self.log_file else "logs",
        ]

        for directory in directories:
            if directory:
                os.makedirs(directory, exist_ok=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# 创建全局配置实例
settings = Settings()

# 创建必要的目录
settings.create_directories()

# 导出常用配置
DATABASE_URL = settings.get_database_url()
UPLOAD_PATH = settings.upload_path
OUTPUT_PATH = settings.output_path
TEMP_PATH = settings.temp_path
MAX_FILE_SIZE = settings.max_file_size
