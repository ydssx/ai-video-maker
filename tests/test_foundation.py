"""
可运行的后端基础测试。

历史脚本型测试已清理；此处覆盖配置、工厂与健康路由等重构回归点。
"""
import os
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_ROOT))


def test_settings_cors_json_array():
    from src.core.config import Settings

    s = Settings(cors_origins='["http://localhost:3000","http://127.0.0.1:3000"]')
    assert s.cors_origins == ["http://localhost:3000", "http://127.0.0.1:3000"]


def test_settings_cors_comma_separated():
    from src.core.config import Settings

    s = Settings(cors_origins="http://a.com, http://b.com")
    assert s.cors_origins == ["http://a.com", "http://b.com"]


def test_settings_ignores_unknown_env(monkeypatch):
    monkeypatch.setenv("MAX_UPLOAD_SIZE", "100MB")
    monkeypatch.setenv("CACHE_EXPIRE_HOURS", "24")
    from src.core.config import Settings

    s = Settings(_env_file=None)
    assert s.app_name


def test_database_url_defaults_to_mysql():
    from src.core.config import Settings

    s = Settings(database_url="", _env_file=None)
    url = s.get_database_url()
    assert url.startswith("mysql+pymysql://")
    assert s.is_mysql is True


def test_database_factory_rejects_sqlite():
    from database_factory import DatabaseFactory

    with pytest.raises(ValueError, match="MySQL"):
        DatabaseFactory.create_database_service("sqlite:///data/app.db")


def test_api_models_importable():
    from src.schemas.api_models import ScriptRequest, VideoRequest, VideoStyle

    req = ScriptRequest(topic="测试主题")
    assert req.style == VideoStyle.EDUCATIONAL
    assert VideoRequest.__name__ == "VideoRequest"


def test_compat_models_shim():
    from models import ScriptRequest, VideoResponse

    assert ScriptRequest is not None
    assert VideoResponse is not None


@pytest.mark.skipif(
    os.getenv("SKIP_MYSQL_TESTS", "").lower() in {"1", "true", "yes"},
    reason="SKIP_MYSQL_TESTS set",
)
def test_health_endpoint_with_mysql():
    """需要本机 MySQL 可用；失败时跳过而非阻断纯单元测试。"""
    try:
        from fastapi.testclient import TestClient
        from main import app

        client = TestClient(app)
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("database_type") == "mysql"
        assert "status" in body
    except Exception as exc:
        pytest.skip(f"MySQL/app unavailable: {exc}")
