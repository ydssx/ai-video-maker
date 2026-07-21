import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND))


@pytest.fixture()
def client(monkeypatch):
    # 单元测试不依赖真实 MySQL：跳过 lifespan 建表失败即可
    from main import app

    return TestClient(app)


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["version"] == "2.0.0"


def test_health_shape(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["database_type"] == "mysql"
    assert "status" in body


def test_script_mock_without_auth_rejected(client):
    resp = client.post("/api/script/generate", json={"topic": "咖啡"})
    assert resp.status_code in (401, 403)


def test_generate_script_service():
    from app.schemas import ScriptRequest
    from app.services.script_service import generate_script

    result = generate_script(ScriptRequest(topic="周末徒步", style="educational", duration="30s"))
    assert result.title
    assert len(result.scenes) >= 3
    assert result.source == "mock"


def test_settings_mysql_url():
    from app.core.config import Settings

    s = Settings(_env_file=None)
    assert s.database_url.startswith("mysql+pymysql://")
