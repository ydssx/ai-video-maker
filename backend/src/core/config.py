from pydantic_settings import BaseSettings
from pydantic import validator
from typing import List, Optional
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

    # 数据库配置
    database_url: str = "sqlite:///data/app.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # MySQL配置（当使用MySQL时）
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

    # JWT配置
    secret_key: str = "your-secret-key-please-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7天
    refresh_token_expire_days: int = 30  # 30天

    # AI服务配置
    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 1500
    openai_temperature: float = 0.7

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

    # 安全配置
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30

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

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """解析CORS源列表"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("openai_api_key")
    def validate_openai_key(cls, v):
        """验证OpenAI API密钥"""
        if v and v == "your_openai_api_key_here":
            return ""  # 重置为空，使用模板模式
        return v

    @validator("unsplash_access_key")
    def validate_unsplash_key(cls, v):
        """验证Unsplash API密钥"""
        if v and v == "your_unsplash_key_here":
            return ""  # 重置为空，使用模板模式
        return v

    @validator("jwt_secret")
    def validate_jwt_secret(cls, v, values):
        """验证JWT密钥"""
        environment = values.get("environment", "development")
        if v == "your-secret-key-change-in-production" and environment == "production":
            raise ValueError("JWT secret must be changed in production")
        return v

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.environment.lower() in ["development", "dev"]

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.environment.lower() in ["production", "prod"]

    @property
    def has_openai_key(self) -> bool:
        """是否配置了OpenAI密钥"""
        return bool(self.openai_api_key and self.openai_api_key.strip())

    @property
    def has_unsplash_key(self) -> bool:
        """是否配置了Unsplash密钥"""
        return bool(self.unsplash_access_key and self.unsplash_access_key.strip())
    
    @property
    def has_aliyun_oss(self) -> bool:
        """是否配置了阿里云OSS"""
        return bool(
            self.aliyun_access_key and 
            self.aliyun_secret_key and 
            self.aliyun_oss_bucket and 
            self.aliyun_oss_endpoint
        )
    
    @property
    def is_cloud_storage(self) -> bool:
        """是否使用云存储"""
        return self.storage_type != "local"

    @property
    def has_redis(self) -> bool:
        """是否配置了Redis"""
        return bool(self.redis_host)

    @property
    def get_redis_url(self) -> str:
        """构建Redis URL"""
        password_part = f":{self.redis_password}@" if self.redis_password else ""
        return f"redis://{password_part}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def get_celery_broker(self) -> str:
        """获取Celery broker URL"""
        return self.celery_broker_url or self.get_redis_url

    @property
    def get_celery_backend(self) -> str:
        """获取Celery result backend URL"""
        return self.celery_result_backend or self.get_redis_url

    def get_database_url(self) -> str:
        """获取数据库URL"""
        if self.database_url.startswith("sqlite"):
            # 确保SQLite数据库目录存在
            db_path = self.database_url.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return self.database_url

    def get_mysql_url(self) -> str:
        """构建MySQL连接URL"""
        return f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset={self.mysql_charset}"

    @property
    def is_mysql(self) -> bool:
        """是否使用MySQL数据库"""
        return self.database_url.startswith("mysql")

    def create_directories(self):
        """创建必要的目录"""
        directories = [
            self.upload_path,
            self.output_path,
            self.temp_path,
            self.cache_path,
            os.path.dirname(self.log_file),
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


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
