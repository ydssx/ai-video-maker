import os
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from loguru import logger
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Video


ProgressCallback = Callable[[str, int, str], None]


def _resolution(name: str) -> tuple[int, int]:
    mapping = {
        "360p": (640, 360),
        "480p": (854, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
    }
    return mapping.get(name, (1280, 720))


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    if len(color) != 6:
        return (15, 28, 46)
    return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def create_video_record(
    db: Session,
    *,
    owner_id: int,
    title: str,
    project_id: Optional[int] = None,
) -> Video:
    video = Video(
        id=uuid.uuid4().hex,
        owner_id=owner_id,
        project_id=project_id,
        title=title,
        status="queued",
        progress=0,
        message="等待渲染",
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


def update_video(
    db: Session,
    video_id: str,
    **fields: Any,
) -> Optional[Video]:
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        return None
    for key, value in fields.items():
        if hasattr(video, key):
            setattr(video, key, value)
    db.commit()
    db.refresh(video)
    return video


def render_video(
    db: Session,
    video_id: str,
    script_data: Dict[str, Any],
    *,
    background_color: str = "#0F1C2E",
    export_config: Optional[Dict[str, Any]] = None,
    progress_cb: Optional[ProgressCallback] = None,
) -> Video:
    """用 MoviePy 把脚本场景渲染成简单字幕短视频。"""
    export_config = export_config or {}
    width, height = _resolution(export_config.get("resolution", "720p"))
    fps = int(export_config.get("fps", 24))

    def report(progress: int, message: str) -> None:
        update_video(db, video_id, status="processing", progress=progress, message=message)
        if progress_cb:
            progress_cb(video_id, progress, message)

    try:
        report(5, "准备素材")
        from moviepy.editor import ColorClip, TextClip, CompositeVideoClip, concatenate_videoclips

        scenes = script_data.get("scenes") or []
        if not scenes:
            raise ValueError("脚本没有场景")

        clips = []
        rgb = _hex_to_rgb(background_color)
        for index, scene in enumerate(scenes):
            duration = float(scene.get("duration") or 3)
            text = str(scene.get("text") or "").strip() or f"场景 {index + 1}"
            bg = ColorClip(size=(width, height), color=rgb, duration=duration)
            try:
                txt = TextClip(
                    text,
                    fontsize=max(36, height // 18),
                    color="white",
                    method="caption",
                    size=(int(width * 0.8), None),
                    font="DejaVu-Sans",
                ).set_duration(duration).set_position("center")
                clip = CompositeVideoClip([bg, txt])
            except Exception:
                # 无字体/ImageMagick 时退回纯色镜头
                logger.warning("TextClip 不可用，使用纯色镜头")
                clip = bg
            clips.append(clip)
            report(10 + int(70 * (index + 1) / len(scenes)), f"渲染场景 {index + 1}/{len(scenes)}")

        report(85, "合成导出")
        final = concatenate_videoclips(clips, method="compose")
        out_dir = Path(settings.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{video_id}.mp4"
        final.write_videofile(
            str(out_path),
            fps=fps,
            codec="libx264",
            audio=False,
            verbose=False,
            logger=None,
        )
        for clip in clips:
            clip.close()
        final.close()

        video = update_video(
            db,
            video_id,
            status="completed",
            progress=100,
            message="完成",
            file_path=str(out_path),
            duration=float(script_data.get("total_duration") or sum(
                float(s.get("duration") or 0) for s in scenes
            )),
            error=None,
        )
        assert video is not None
        return video
    except Exception as exc:
        logger.exception("视频渲染失败")
        video = update_video(
            db,
            video_id,
            status="failed",
            progress=100,
            message="失败",
            error=str(exc),
        )
        assert video is not None
        return video


def public_download_url(video: Video) -> Optional[str]:
    if video.status != "completed" or not video.file_path:
        return None
    name = os.path.basename(video.file_path)
    return f"/output/{name}"
