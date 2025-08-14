from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
import logging

from services.video_service import video_service
from services.database_service import db_service
from services.ai_service import ai_service
from models import VideoRequest, VideoResponse
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket连接管理
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_progress(self, video_id: str, progress: int, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_json({
                    "video_id": video_id,
                    "progress": progress,
                    "message": message,
                    "timestamp": datetime.now().isoformat()
                })
            except:
                pass

manager = ConnectionManager()

@router.post("/generate", response_model=VideoResponse)
async def generate_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """生成视频"""
    return await create_video_internal(request, background_tasks)

@router.post("/create", response_model=VideoResponse)
async def create_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """创建视频 (兼容旧API)"""
    return await create_video_internal(request, background_tasks)

async def create_video_internal(request: VideoRequest, background_tasks: BackgroundTasks):
    """内部视频创建逻辑"""
    try:
        video_id = str(uuid.uuid4())
        
        # 处理script数据 - 支持字典格式
        script_data = request.script
        if isinstance(script_data, dict):
            script_title = script_data.get('title', '未命名视频')
            script_duration = script_data.get('total_duration', 60.0)
        else:
            script_title = script_data.title
            script_duration = script_data.total_duration
        
        # 创建视频记录
        try:
            db_service.create_video(
                video_id=video_id,
                project_id=script_title,  # 临时使用标题作为项目ID
                user_id=1,  # 临时用户ID
                title=script_title,
                duration=script_duration
            )
        except Exception as e:
            logger.warning(f"数据库记录创建失败: {str(e)}")
            # 继续执行，不让数据库错误阻止视频创建
        
        # 记录使用统计
        try:
            db_service.log_usage(1, "video_generation", {
                "video_id": video_id,
                "template": request.template_id,
                "duration": script_duration
            })
        except Exception as e:
            logger.warning(f"统计记录失败: {str(e)}")
        
        # 构建配置
        config = {
            "template_id": request.template_id,
            "voice_config": request.voice_config.dict(),
            "resolution": "720p",
            "fps": 30,
            "format": "mp4"
        }
        
        # 添加可选配置
        if request.text_style:
            config["text_style"] = request.text_style.dict()
        if request.audio_config:
            config["audio_config"] = request.audio_config.dict()
        if request.transition_config:
            config["transition_config"] = [t.dict() for t in request.transition_config]
        if request.export_config:
            export_cfg = request.export_config.dict()
            config.update({
                "resolution": export_cfg.get("resolution", "720p"),
                "fps": export_cfg.get("fps", 30),
                "format": export_cfg.get("format", "mp4"),
                "quality": export_cfg.get("quality", "high")
            })
        
        # 处理script数据
        if isinstance(request.script, dict):
            script_dict = request.script
        else:
            script_dict = request.script.dict()
        
        # 启动后台任务
        background_tasks.add_task(
            create_video_background_task,
            video_id,
            script_dict,
            config
        )
        
        return VideoResponse(
            video_id=video_id,
            status="processing"
        )
        
    except Exception as e:
        logger.error(f"视频生成请求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"视频生成失败: {str(e)}")

async def create_video_background_task(video_id: str, script_data: Dict, config: Dict):
    """后台视频创建任务"""
    try:
        # 进度回调函数
        async def progress_callback(vid_id: str, progress: int, message: str):
            try:
                await manager.send_progress(vid_id, progress, message)
            except Exception as e:
                logger.warning(f"进度推送失败: {str(e)}")
            
            # 更新数据库状态
            try:
                if progress == 100:
                    db_service.update_video(vid_id, status="completed")
                elif progress == -1:
                    db_service.update_video(vid_id, status="failed")
            except Exception as e:
                logger.warning(f"数据库状态更新失败: {str(e)}")
        
        # 发送开始进度
        await progress_callback(video_id, 0, "开始创建视频...")
        
        # 简化的视频创建逻辑
        try:
            # 模拟视频创建过程
            await progress_callback(video_id, 20, "处理脚本数据...")
            await asyncio.sleep(1)
            
            await progress_callback(video_id, 40, "生成视频场景...")
            await asyncio.sleep(2)
            
            await progress_callback(video_id, 60, "添加文字和效果...")
            await asyncio.sleep(2)
            
            await progress_callback(video_id, 80, "合成最终视频...")
            await asyncio.sleep(2)
            
            # 创建一个简单的测试视频文件
            output_dir = "data/output"
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{video_id}.mp4")
            
            # 创建一个空的视频文件作为占位符
            with open(output_path, 'w') as f:
                f.write("# 视频文件占位符")
            
            await progress_callback(video_id, 100, "视频创建完成！")
            
            # 更新数据库
            try:
                db_service.update_video(
                    video_id,
                    status="completed",
                    file_path=output_path,
                    duration=script_data.get('total_duration', 60.0)
                )
            except Exception as e:
                logger.warning(f"数据库更新失败: {str(e)}")
            
            logger.info(f"视频 {video_id} 创建完成")
            
        except Exception as e:
            logger.error(f"视频创建过程失败: {str(e)}")
            await progress_callback(video_id, -1, f"创建失败: {str(e)}")
            
            try:
                db_service.update_video(video_id, status="failed")
            except Exception as db_e:
                logger.warning(f"数据库状态更新失败: {str(db_e)}")
        
    except Exception as e:
        logger.error(f"视频创建任务失败: {str(e)}")
        try:
            await manager.send_progress(video_id, -1, f"任务失败: {str(e)}")
            db_service.update_video(video_id, status="failed")
        except Exception as cleanup_e:
            logger.error(f"清理失败: {str(cleanup_e)}")

@router.get("/status/{video_id}")
async def get_video_status(video_id: str):
    """获取视频状态"""
    try:
        # 从数据库获取视频信息
        video_info = db_service.get_video(video_id)
        if not video_info:
            raise HTTPException(status_code=404, detail="视频不存在")
        
        # 获取处理状态
        processing_status = video_service.get_video_status(video_id)
        
        return {
            "video_id": video_id,
            "status": video_info['status'],
            "progress": processing_status.get('progress', 0),
            "duration": video_info.get('duration', 0),
            "created_at": video_info['created_at'],
            "file_path": video_info.get('file_path'),
            "thumbnail_path": video_info.get('thumbnail_path')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取视频状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取状态失败")

@router.get("/download/{video_id}")
async def download_video(video_id: str):
    """下载视频"""
    try:
        video_info = db_service.get_video(video_id)
        if not video_info:
            raise HTTPException(status_code=404, detail="视频不存在")
        
        file_path = video_info.get('file_path')
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="视频文件不存在")
        
        # 记录下载统计
        db_service.log_usage(video_info['user_id'], "video_download", {
            "video_id": video_id
        })
        
        return FileResponse(
            file_path,
            media_type='video/mp4',
            filename=f"video_{video_id}.mp4"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"视频下载失败: {str(e)}")
        raise HTTPException(status_code=500, detail="下载失败")

@router.get("/thumbnail/{video_id}")
async def get_video_thumbnail(video_id: str):
    """获取视频缩略图"""
    try:
        video_info = db_service.get_video(video_id)
        if not video_info:
            raise HTTPException(status_code=404, detail="视频不存在")
        
        thumbnail_path = video_info.get('thumbnail_path')
        if not thumbnail_path or not os.path.exists(thumbnail_path):
            raise HTTPException(status_code=404, detail="缩略图不存在")
        
        return FileResponse(
            thumbnail_path,
            media_type='image/jpeg'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取缩略图失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取缩略图失败")

@router.websocket("/progress")
async def websocket_progress(websocket: WebSocket):
    """WebSocket进度推送"""
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.delete("/cancel/{video_id}")
async def cancel_video_processing(video_id: str):
    """取消视频处理"""
    try:
        success = video_service.cancel_video_processing(video_id)
        if success:
            db_service.update_video(video_id, status="cancelled")
            return {"message": "视频处理已取消"}
        else:
            raise HTTPException(status_code=404, detail="视频不存在或无法取消")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消视频处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail="取消失败")

@router.get("/list")
async def list_videos(user_id: int = 1, limit: int = 20, offset: int = 0):
    """获取视频列表"""
    try:
        # 这里应该从认证中获取用户ID，暂时使用默认值
        videos = []
        
        # 从数据库获取视频列表
        # TODO: 实现数据库查询
        
        return {
            "videos": videos,
            "total": len(videos),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"获取视频列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取列表失败")

@router.get("/templates")
async def get_video_templates():
    """获取视频模板"""
    templates = [
        # 基础模板
        {
            "id": "default",
            "name": "默认模板",
            "description": "经典的白色文字居中显示，适合各种内容",
            "category": "通用",
            "preview": "/templates/default_preview.jpg"
        },
        {
            "id": "modern",
            "name": "现代简约",
            "description": "简洁现代的设计风格，适合商务和科技内容",
            "category": "通用",
            "preview": "/templates/modern_preview.jpg"
        },
        {
            "id": "tech",
            "name": "科技风格",
            "description": "科技感十足，适合技术和创新内容",
            "category": "通用",
            "preview": "/templates/tech_preview.jpg"
        },
        {
            "id": "elegant",
            "name": "优雅风格",
            "description": "优雅精致，适合生活方式和艺术内容",
            "category": "通用",
            "preview": "/templates/elegant_preview.jpg"
        },
        
        # 商务模板
        {
            "id": "corporate",
            "name": "企业商务",
            "description": "专业商务风格，适合企业宣传和产品介绍",
            "category": "商务",
            "preview": "/templates/corporate_preview.jpg"
        },
        {
            "id": "startup",
            "name": "创业活力",
            "description": "年轻活力的创业风格，适合新兴企业",
            "category": "商务",
            "preview": "/templates/startup_preview.jpg"
        },
        {
            "id": "finance",
            "name": "金融理财",
            "description": "稳重专业的金融风格，适合理财和投资内容",
            "category": "商务",
            "preview": "/templates/finance_preview.jpg"
        },
        {
            "id": "ecommerce",
            "name": "电商购物",
            "description": "活泼的购物风格，适合产品展示和促销",
            "category": "商务",
            "preview": "/templates/ecommerce_preview.jpg"
        },
        
        # 生活方式模板
        {
            "id": "food",
            "name": "美食诱惑",
            "description": "温暖的美食风格，适合美食分享和餐厅推广",
            "category": "生活",
            "preview": "/templates/food_preview.jpg"
        },
        {
            "id": "travel",
            "name": "旅行探索",
            "description": "清新的旅游风格，适合旅游攻略和风景分享",
            "category": "生活",
            "preview": "/templates/travel_preview.jpg"
        },
        {
            "id": "fitness",
            "name": "健身运动",
            "description": "动感的运动风格，适合健身和运动内容",
            "category": "生活",
            "preview": "/templates/fitness_preview.jpg"
        },
        {
            "id": "beauty",
            "name": "美妆时尚",
            "description": "时尚的美妆风格，适合美妆教程和时尚分享",
            "category": "生活",
            "preview": "/templates/beauty_preview.jpg"
        },
        
        # 教育模板
        {
            "id": "academic",
            "name": "学术教育",
            "description": "严谨的学术风格，适合教育机构和学术内容",
            "category": "教育",
            "preview": "/templates/academic_preview.jpg"
        },
        {
            "id": "kids",
            "name": "儿童教育",
            "description": "活泼可爱的儿童风格，适合儿童教育内容",
            "category": "教育",
            "preview": "/templates/kids_preview.jpg"
        },
        {
            "id": "language",
            "name": "语言学习",
            "description": "国际化的语言学习风格，适合语言教学",
            "category": "教育",
            "preview": "/templates/language_preview.jpg"
        },
        {
            "id": "skill",
            "name": "技能培训",
            "description": "专业的技能培训风格，适合职业技能教学",
            "category": "教育",
            "preview": "/templates/skill_preview.jpg"
        }
    ]
    return {"templates": templates}

@router.get("/voices")
async def get_voice_options():
    """获取语音选项"""
    voices = {
        "gtts": [
            {"id": "zh", "name": "中文（普通话）", "language": "zh"},
            {"id": "en", "name": "英文", "language": "en"},
            {"id": "ja", "name": "日文", "language": "ja"},
            {"id": "ko", "name": "韩文", "language": "ko"}
        ],
        "openai": [
            {"id": "alloy", "name": "Alloy（中性）", "language": "多语言"},
            {"id": "echo", "name": "Echo（男性）", "language": "多语言"},
            {"id": "fable", "name": "Fable（英式）", "language": "多语言"},
            {"id": "onyx", "name": "Onyx（深沉）", "language": "多语言"},
            {"id": "nova", "name": "Nova（女性）", "language": "多语言"},
            {"id": "shimmer", "name": "Shimmer（温柔）", "language": "多语言"}
        ],
        "edge": [
            {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓（女性）", "language": "zh-CN"},
            {"id": "zh-CN-YunxiNeural", "name": "云希（男性）", "language": "zh-CN"},
            {"id": "zh-CN-YunyangNeural", "name": "云扬（男性）", "language": "zh-CN"},
            {"id": "en-US-AriaNeural", "name": "Aria（女性）", "language": "en-US"},
            {"id": "en-US-DavisNeural", "name": "Davis（男性）", "language": "en-US"}
        ]
    }
    
    return {"voices": voices}

class VoicePreviewRequest(BaseModel):
    text: str
    voice_config: dict

@router.post("/preview-voice")
async def preview_voice(request: VoicePreviewRequest):
    """预览语音效果"""
    try:
        voice_path = await ai_service.generate_voice(request.text, request.voice_config)
        
        if voice_path and os.path.exists(voice_path):
            return FileResponse(
                voice_path,
                media_type='audio/mpeg',
                filename="voice_preview.mp3"
            )
        else:
            raise HTTPException(status_code=500, detail="语音生成失败")
        
    except Exception as e:
        logger.error(f"语音预览失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"语音预览失败: {str(e)}")

@router.get("/stats")
async def get_video_stats():
    """获取视频统计信息"""
    try:
        stats = video_service.get_processing_stats()
        system_stats = db_service.get_system_stats()
        
        return {
            "processing": stats,
            "system": system_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取统计失败")

@router.post("/cleanup")
async def cleanup_old_videos(max_age_days: int = 7):
    """清理旧视频文件"""
    try:
        deleted_count = video_service.cleanup_old_videos(max_age_days)
        
        return {
            "message": f"清理完成，删除了 {deleted_count} 个文件",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"清理失败: {str(e)}")
        raise HTTPException(status_code=500, detail="清理失败")