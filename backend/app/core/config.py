from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AI Video Maker"
    environment: str = "development"
    debug: bool = True
    secret_key: str = "dev-secret-change-me"
    access_token_expire_minutes: int = 60 * 24 * 7
    algorithm: str = "HS256"

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "123456"
    mysql_database: str = "ai_video_maker"

    cors_origins: List[str] = ["http://localhost:3000"]

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    upload_dir: str = "data/uploads"
    output_dir: str = "data/output"
    temp_dir: str = "data/temp"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, value):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            text = value.strip()
            if text.startswith("["):
                import json

                return json.loads(text)
            return [part.strip() for part in text.split(",") if part.strip()]
        return value

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            "?charset=utf8mb4"
        )

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key and self.openai_api_key not in {
            "your_openai_api_key_here",
            "",
        })


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
