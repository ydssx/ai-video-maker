from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
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
    try:
        video_id = str(uuid.uuid4())
        
        # 创建视频记录
        db_service.create_video(
            video_id=video_id,
            project_id=request.script.title,  # 临时使用标题作为项目ID
            user_id=1,  # 临时用户ID
            title=request.script.title,
            duration=request.script.total_duration
        )
        
        # 记录使用统计
        db_service.log_usage(1, "video_generation", {
            "video_id": video_id,
            "template": request.template_id,
            "duration": request.script.total_duration
        })
        
        # 启动后台任务
        background_tasks.add_task(
            create_video_background_task,
            video_id,
            request.script.dict(),
            {
                "template_id": request.template_id,
                "voice_config": request.voice_config.dict(),
                "resolution": "720p",
                "fps": 30,
                "format": "mp4"
            }
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
            await manager.send_progress(vid_id, progress, message)
            
            # 更新数据库状态
            if progress == 100:
                db_service.update_video(vid_id, status="completed")
            elif progress == -1:
                db_service.update_video(vid_id, status="failed")
        
        # 创建视频
        result = await video_service.create_video(
            video_id, script_data, config, progress_callback
        )
        
        # 更新数据库
        db_service.update_video(
            video_id,
            status="completed",
            file_path=result['output_path'],
            thumbnail_path=result.get('thumbnail_path'),
            duration=result.get('duration', 0)
        )
        
        logger.info(f"视频 {video_id} 创建完成")
        
    except Exception as e:
        logger.error(f"视频创建失败: {str(e)}")
        db_service.update_video(video_id, status="failed")
        await manager.send_progress(video_id, -1, f"创建失败: {str(e)}")

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
            raise HTTPException(status_code=404, 存在")
        
        return FileRsponse(
            thumbnail_path,
            
        )
        
    except HTTPException:
        raise
    except Exception
        logger.error(f"获取缩略图失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取缩略图失

@router.websocket("/progress")
async def we
    """WebSocket进度推送"""
    await manager.connect(websocket)
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except WebSocketect:
        manager.disconnect(websocket)

@router.delete("/canco_id}")
async def cancel_vid:
    """取消视频处理"""
    try:
        success = video_service.cancel_video_proceeo_id)
        if success:
            db_service.update_vi")
            return {
        else:
            raise HTTPException(status_code=40
            
    except HTTPException:
        raise
    exce:
        logger.e)}")
        raise HTTPException(status_code=500, detail="取消失败")

@router.get("/list"
async def list_videos(user_id: int = 1, limit: int = 20,t = 0):
    """获取视频列表"""
    try:
        # 这里应该从认证中获取用户ID，暂时使用默认值
        videos = []
        
        
        # TODO: 实现数据库查询
        
        return {
            "videos": videos,
            "total": len(videos),
        ,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"获取视频列表失败: {str(e)}")
        raise HTTPExceptio")l="获取列表失败=500, detaius_coden(stat limitt":    "limi据库获取视频列表# 从数et: in offs): {str(e"取消视频处理失败or(frrption as ept Exce无法取消")ail="视频不存在或4, det处理已取消"}视频": "ssageme"ledcanceltatus=" s(video_id,deossing(vido_id: str)videing(eo_processl/{videeisconnDbSocket):ket: Wess(websocgreet_proockbs败")as e: mage/jpeg''imedia_type=etail="缩略图不de
            download_image(image_url, image_path)
            
            # 获取模板样式
            template_style = get_template_style(request.template_id)
            
            # 使用 Pillow 在图片上添加文字
            text_image_path = f"../assets/temp/scene_text_{i}_{video_id}.jpg"
            create_text_image(image_path, scene.text, text_image_path, template_style)
            
            # 创建图片剪辑
            img_clip = ImageClip(text_image_path, duration=scene.duration)
            img_clip = img_clip.resize(height=720)  # 标准化高度
            
            clips.append(img_clip)
            
            # 生成语音（如果启用）
            if request.voice_config.enabled:
                try:
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    voice_path = loop.run_until_complete(
                        ai_service.generate_voice(scene.text, request.voice_config.dict())
                    )
                    
                    # 创建音频剪辑
                    audio_clip = AudioFileClip(voice_path).subclip(0, scene.duration)
                    audio_clips.append(audio_clip)
                    
                    loop.close()
                    
                except Exception as e:
                    print(f"语音生成失败: {str(e)}")
                    # 如果语音生成失败，添加静音
                    silence = AudioClip(lambda t: 0, duration=scene.duration)
                    audio_clips.append(silence)
        
        # 合并所有场景
        final_video = concatenate_videoclips(clips, method="compose")
        
        # 添加音频（如果有）
        if audio_clips and request.voice_config.enabled:
            try:
                final_audio = concatenate_audioclips(audio_clips)
                final_video = final_video.set_audio(final_audio)
            except Exception as e:
                print(f"音频合并失败: {str(e)}")
        
        # 导出视频
        import os
        from config import settings
        output_dir = os.path.abspath(str(settings.output_path))
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{video_id}.mp4")
        
        final_video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac' if request.voice_config.enabled else None,
            verbose=False,
            logger=None
        )
        
        # 清理临时文件
        cleanup_temp_files(video_id, len(request.script.scenes), audio_clips)
        
        video_status[video_id] = "completed"
        
    except Exception as e:
        print(f"视频制作失败: {str(e)}")
        video_status[video_id] = "failed"

def cleanup_temp_files(video_id: str, scene_count: int, audio_clips: list):
    """清理临时文件"""
    for i in range(scene_count):
        temp_paths = [
            f"../assets/temp/scene_{i}_{video_id}.jpg",
            f"../assets/temp/scene_text_{i}_{video_id}.jpg"
        ]
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)
    
    # 清理音频文件
    for audio_clip in audio_clips:
        try:
            if hasattr(audio_clip, 'filename') and os.path.exists(audio_clip.filename):
                os.remove(audio_clip.filename)
        except:
            pass

def create_text_image(image_path: str, text: str, output_path: str, template_style: dict = None):
    """使用 Pillow 在图片上添加文字"""
    try:
        # 默认样式
        default_style = {
            "font_size": 48,
            "font_color": (255, 255, 255),
            "font_shadow": (0, 0, 0),
            "text_position": "center",
            "background_overlay": None
        }
        
        # 合并样式
        style = {**default_style, **(template_style or {})}
        
        # 打开原图片
        img = Image.open(image_path)
        img = img.convert('RGBA')
        
        # 调整图片大小
        img = img.resize((1280, 720), Image.Resampling.LANCZOS)
        
        # 添加背景遮罩（如果有）
        if style.get("background_overlay"):
            overlay = Image.new('RGBA', img.size, style["background_overlay"])
            img = Image.alpha_composite(img, overlay)
        
        # 创建绘图对象
        draw = ImageDraw.Draw(img)
        
        # 尝试使用系统字体
        try:
            # Windows 系统字体
            font = ImageFont.truetype("arial.ttf", style["font_size"])
        except:
            try:
                # 备用字体
                font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", style["font_size"])
            except:
                # 使用默认字体
                font = ImageFont.load_default()
        
        # 文字换行处理
        lines = wrap_text(text, font, img.width - 100)
        
        # 计算文字总高度
        line_height = int(style["font_size"] * 1.2)
        total_height = len(lines) * line_height
        
        # 根据位置计算起始坐标
        if style["text_position"] == "top":
            y_start = 50
        elif style["text_position"] == "bottom":
            y_start = img.height - total_height - 50
        else:  # center
            y_start = (img.height - total_height) // 2
        
        # 绘制文字（带阴影效果）
        for i, line in enumerate(lines):
            # 计算文字宽度以居中
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (img.width - text_width) // 2
            y = y_start + i * line_height
            
            # 绘制阴影
            shadow_color = style["font_shadow"] + (128,) if len(style["font_shadow"]) == 3 else style["font_shadow"]
            draw.text((x + 2, y + 2), line, font=font, fill=shadow_color)
            
            # 绘制文字
            text_color = style["font_color"] + (255,) if len(style["font_color"]) == 3 else style["font_color"]
            draw.text((x, y), line, font=font, fill=text_color)
        
        # 转换回 RGB 并保存
        img = img.convert('RGB')
        img.save(output_path, 'JPEG', quality=95)
        
    except Exception as e:
        print(f"创建文字图片失败: {str(e)}")
        # 如果失败，直接复制原图片
        import shutil
        shutil.copy2(image_path, output_path)

def wrap_text(text: str, font, max_width: int) -> list:
    """文字换行处理"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                lines.append(word)
    
    if current_line:
        lines.append(current_line)
    
    return lines

def get_template_style(template_id: str) -> dict:
    """获取模板样式"""
    # 导入模板模块
    from templates import business, lifestyle, education
    
    # 基础模板
    base_templates = {
        "default": {
            "font_size": 48,
            "font_color": (255, 255, 255),
            "font_shadow": (0, 0, 0),
            "text_position": "center",
            "background_overlay": None
        },
        "modern": {
            "font_size": 42,
            "font_color": (45, 45, 45),
            "font_shadow": (200, 200, 200),
            "text_position": "bottom",
            "background_overlay": (255, 255, 255, 100)
        },
        "tech": {
            "font_size": 46,
            "font_color": (0, 255, 255),
            "font_shadow": (0, 0, 0),
            "text_position": "center",
            "background_overlay": (0, 0, 0, 120)
        },
        "elegant": {
            "font_size": 40,
            "font_color": (139, 69, 19),
            "font_shadow": (255, 248, 220),
            "text_position": "top",
            "background_overlay": (255, 248, 220, 80)
        }
    }
    
    # 商务模板
    business_templates = {
        "corporate": business.get_corporate_style(),
        "startup": business.get_startup_style(),
        "finance": business.get_finance_style(),
        "ecommerce": business.get_ecommerce_style()
    }
    
    # 生活方式模板
    lifestyle_templates = {
        "food": lifestyle.get_food_style(),
        "travel": lifestyle.get_travel_style(),
        "fitness": lifestyle.get_fitness_style(),
        "beauty": lifestyle.get_beauty_style()
    }
    
    # 教育模板
    education_templates = {
        "academic": education.get_academic_style(),
        "kids": education.get_kids_style(),
        "language": education.get_language_style(),
        "skill": education.get_skill_style()
    }
    
    # 合并所有模板
    all_templates = {
        **base_templates,
        **business_templates,
        **lifestyle_templates,
        **education_templates
    }
    
    return all_templates.get(template_id, base_templates["default"])

def get_scene_image(keywords: list) -> str:
    """获取场景图片URL"""
    # 简化版：使用第一个关键词搜索图片
    keyword = keywords[0] if keywords else "abstract"
    # 使用 Picsum 作为默认图片源
    return f"https://picsum.photos/1280/720?random={hash(keyword) % 1000}"

def download_image(url: str, path: str):
    """下载图片到本地"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    response = requests.get(url)
    with open(path, 'wb') as f:
        f.write(response.content)

@router.post("/create", response_model=VideoResponse)
async def create_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """创建视频"""
    try:
        video_id = str(uuid.uuid4())
        
        # 启动后台任务
        background_tasks.add_task(create_video_from_script, video_id, request)
        
        return VideoResponse(
            video_id=video_id,
            status="processing"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视频创建失败: {str(e)}")

@router.get("/status/{video_id}")
async def get_video_status(video_id: str):
    """获取视频制作状态"""
    import os
    
    # 检查文件是否存在
    from config import settings
    output_dir = os.path.abspath(str(settings.output_path))
    file_path = os.path.join(output_dir, f"{video_id}.mp4")
    
    if os.path.exists(file_path):
        # 文件存在，视频已完成
        response_data = {
            "video_id": video_id,
            "status": "completed",
            "download_url": f"/api/video/download/{video_id}",
            "preview_url": f"/output/{video_id}.mp4"
        }
        return response_data
    
    # 检查内存状态
    if video_id in video_status:
        status = video_status[video_id]
        response_data = {
            "video_id": video_id,
            "status": status
        }
        
        if status == "completed":
            response_data["download_url"] = f"/api/video/download/{video_id}"
            response_data["preview_url"] = f"/output/{video_id}.mp4"
        
        return response_data
    
    # 视频不存在
    raise HTTPException(status_code=404, detail="视频不存在")

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
        ]
    }
    
    return {"voices": voices}

@router.get("/download/{video_id}")
async def download_video(video_id: str):
    """下载视频文件"""
    from fastapi.responses import FileResponse
    import os
    
    # 直接检查文件是否存在，不依赖内存状态
    from config import settings
    output_dir = os.path.abspath(str(settings.output_path))
    file_path = os.path.join(output_dir, f"{video_id}.mp4")
    
    if not os.path.exists(file_path):
        # 调试信息
        print(f"查找视频文件: {file_path}")
        print(f"输出目录存在: {os.path.exists(output_dir)}")
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            print(f"输出目录中的文件: {files}")
        raise HTTPException(status_code=404, detail=f"视频文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=f"ai_video_{video_id}.mp4",
        media_type="video/mp4",
        headers={
            "Content-Disposition": f"attachment; filename=ai_video_{video_id}.mp4",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "*"
        }
    )

@router.post("/create-test-video")
async def create_test_video():
    """创建测试视频"""
    import uuid
    import os
    from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
    
    try:
        video_id = str(uuid.uuid4())
        
        # 创建简单的测试视频
        background = ColorClip(size=(1280, 720), color=(0, 100, 200), duration=3)
        
        try:
            text = TextClip("测试视频", fontsize=50, color='white', font='Arial')
            text = text.set_position('center').set_duration(3)
            video = CompositeVideoClip([background, text])
        except:
            # 如果文字创建失败，只使用背景
            video = background
        
        # 确保输出目录存在
        from config import settings
        output_dir = os.path.abspath(str(settings.output_path))
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{video_id}.mp4")
        
        # 导出视频
        video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            verbose=False,
            logger=None
        )
        
        # 更新状态
        video_status[video_id] = "completed"
        
        return {
            "video_id": video_id,
            "status": "completed",
            "file_path": output_path,
            "file_exists": os.path.exists(output_path)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }

class VoicePreviewRequest(BaseModel):
    text: str
    voice_config: dict

@router.post("/preview-voice")
async def preview_voice(request: VoicePreviewRequest):
    """预览语音效果"""
    try:
        voice_path = await ai_service.generate_voice(request.text, request.voice_config)
        
        # 返回音频文件路径（相对路径）
        relative_path = voice_path.replace("../", "/")
        return {"audio_url": relative_path}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音预览失败: {str(e)}")