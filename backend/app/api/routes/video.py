import os
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import SessionLocal, get_db
from app.models import User, Video
from app.schemas import VideoCreateRequest, VideoOut
from app.services import video_service

router = APIRouter(prefix="/api/video", tags=["video"])


def _to_out(video: Video) -> VideoOut:
    return VideoOut(
        id=video.id,
        title=video.title,
        status=video.status,
        progress=video.progress,
        message=video.message,
        download_url=video_service.public_download_url(video),
        duration=video.duration,
        error=video.error,
    )


def _render_job(video_id: str, script: dict, background_color: str, export_config: dict) -> None:
    db = SessionLocal()
    try:
        video_service.render_video(
            db,
            video_id,
            script,
            background_color=background_color,
            export_config=export_config,
        )
    finally:
        db.close()


@router.post("/create", response_model=VideoOut)
def create_video(
    payload: VideoCreateRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    script = payload.script if isinstance(payload.script, dict) else payload.script.model_dump()
    title = script.get("title") or "未命名视频"
    video = video_service.create_video_record(
        db,
        owner_id=current_user.id,
        title=title,
        project_id=payload.project_id,
    )
    background.add_task(
        _render_job,
        video.id,
        script,
        payload.background_color,
        payload.export_config.model_dump(),
    )
    return _to_out(video)


@router.get("/{video_id}", response_model=VideoOut)
def get_video(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    video = (
        db.query(Video)
        .filter(Video.id == video_id, Video.owner_id == current_user.id)
        .first()
    )
    if not video:
        raise HTTPException(status_code=404, detail="视频不存在")
    return _to_out(video)


@router.get("/", response_model=List[VideoOut])
def list_videos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    videos = (
        db.query(Video)
        .filter(Video.owner_id == current_user.id)
        .order_by(Video.created_at.desc())
        .limit(50)
        .all()
    )
    return [_to_out(v) for v in videos]


@router.get("/{video_id}/download")
def download_video(
    video_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    video = (
        db.query(Video)
        .filter(Video.id == video_id, Video.owner_id == current_user.id)
        .first()
    )
    if not video or video.status != "completed" or not video.file_path:
        raise HTTPException(status_code=404, detail="视频尚未就绪")
    if not os.path.exists(video.file_path):
        raise HTTPException(status_code=404, detail="文件丢失")
    return FileResponse(
        video.file_path,
        media_type="video/mp4",
        filename=f"{video.title or video.id}.mp4",
    )
