import os
from typing import Dict, Any

from celery import Celery
from celery.result import AsyncResult

from src.core.config import settings


def create_celery_app() -> Celery:
    broker_url = settings.get_celery_broker
    backend_url = settings.get_celery_backend

    app = Celery(
        "ai_video_maker",
        broker=broker_url,
        backend=backend_url,
        include=["services.tasks.video_tasks"],
    )

    app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="Asia/Shanghai",
        enable_utc=True,
        task_track_started=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_time_limit=60 * 60,  # 60min
    )

    return app


# 单例 Celery 实例
celery_app = create_celery_app() if settings.celery_enabled else None


def is_celery_enabled() -> bool:
    return bool(settings.celery_enabled and celery_app is not None)


def get_async_result(task_id: str) -> AsyncResult:
    if not is_celery_enabled():
        raise RuntimeError("Celery is not enabled")
    return AsyncResult(task_id, app=celery_app)


def get_task_progress(task_id: str) -> Dict[str, Any]:
    """获取任务状态与进度信息。
    返回: { state: str, progress: int, message: str }
    """
    try:
        result = get_async_result(task_id)
        state = result.state or "PENDING"
        info = result.info or {}

        # Celery 自定义进度: state='PROGRESS', meta=info
        progress = 0
        message = ""
        if isinstance(info, dict):
            progress = int(info.get("progress", 0))
            message = str(info.get("message", ""))

        if state == "SUCCESS":
            progress = max(progress, 100)
            if not message:
                message = "任务完成"

        return {"state": state, "progress": progress, "message": message}
    except Exception:
        return {"state": "UNKNOWN", "progress": 0, "message": ""}


