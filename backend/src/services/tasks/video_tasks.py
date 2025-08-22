from typing import Dict

from src.services.task_queue import celery_app
from database_factory import get_db_service
from src.services.video_service import video_service
# 注意：当前任务实现未直接使用 video_service；后续迭代可切换到真实渲染


db_service = get_db_service()

@celery_app.task(name="video.create", bind=True)
def create_video_task(self, video_id: str, script_data: Dict, config: Dict) -> Dict:
    """Celery 任务：创建视频。

    注意：Celery 任务函数是同步的；内部如需调用异步逻辑，
    应在服务层提供同步包装或在任务中显式运行事件循环。
    这里调用 video_service 的同步导出路径（其内部已包含并发控制）。
    """
    import asyncio

    async def run_create():
        async def progress_cb(vid: str, progress: int, message: str):
            # 将进度同步到 Celery 任务状态
            try:
                self.update_state(state="PROGRESS", meta={"progress": progress, "message": message})
            except Exception:
                pass

        result = await video_service.create_video(
            video_id=video_id,
            script_data=script_data,
            config=config,
            progress_callback=progress_cb,
        )
        return result

    # 执行异步视频创建
    result = asyncio.run(run_create())

    # 更新数据库记录
    try:
        db_service.update_video(
            video_id,
            status="completed",
            file_path=result.get("output_path"),
            duration=result.get("duration", script_data.get("total_duration", 60.0)),
        )
    except Exception:
        # 数据库不可用时忽略更新，任务仍视为成功
        pass

    return {
        "video_id": video_id,
        "status": result.get("status", "completed"),
        "file_path": result.get("output_path"),
        "thumbnail_path": result.get("thumbnail_path"),
        "duration": result.get("duration"),
    }


