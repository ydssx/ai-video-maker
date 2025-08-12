from fastapi import APIRouter, HTTPException, BackgroundTasks
from moviepy.editor import *
import requests
import os
import uuid
from typing import Dict
from models import VideoRequest, VideoResponse
from pydantic import BaseModel
import asyncio
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from services.ai_service import ai_service

router = APIRouter()

# 存储视频制作状态
video_status: Dict[str, str] = {}

def create_video_from_script(video_id: str, request: VideoRequest):
    """后台任务：根据脚本创建视频"""
    try:
        video_status[video_id] = "processing"
        
        clips = []
        audio_clips = []
        
        for i, scene in enumerate(request.script.scenes):
            # 下载图片
            image_url = get_scene_image(scene.image_keywords)
            image_path = f"../assets/temp/scene_{i}_{video_id}.jpg"
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
        output_path = f"../output/{video_id}.mp4"
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
    templates = {
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
    
    return templates.get(template_id, templates["default"])

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
    if video_id not in video_status:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    status = video_status[video_id]
    response_data = {
        "video_id": video_id,
        "status": status
    }
    
    if status == "completed":
        response_data["download_url"] = f"/api/video/download/{video_id}"
        response_data["preview_url"] = f"/output/{video_id}.mp4"
    
    return response_data

@router.get("/templates")
async def get_video_templates():
    """获取视频模板"""
    templates = [
        {
            "id": "default",
            "name": "默认模板",
            "description": "经典的白色文字居中显示，适合各种内容",
            "category": "通用",
            "preview": "/templates/default_preview.jpg",
            "settings": {
                "font_size": 48,
                "font_color": "white",
                "text_position": "center",
                "background_overlay": None
            }
        },
        {
            "id": "modern",
            "name": "现代简约",
            "description": "简洁现代的设计风格，适合商务和科技内容",
            "category": "商务",
            "preview": "/templates/modern_preview.jpg", 
            "settings": {
                "font_size": 42,
                "font_color": "#2D2D2D",
                "text_position": "bottom",
                "background_overlay": "rgba(255,255,255,0.4)"
            }
        },
        {
            "id": "tech",
            "name": "科技风格",
            "description": "科技感十足，适合技术和创新内容",
            "category": "科技",
            "preview": "/templates/tech_preview.jpg",
            "settings": {
                "font_size": 46,
                "font_color": "#00FFFF",
                "text_position": "center",
                "background_overlay": "rgba(0,0,0,0.5)"
            }
        },
        {
            "id": "elegant",
            "name": "优雅风格",
            "description": "优雅精致，适合生活方式和艺术内容",
            "category": "生活",
            "preview": "/templates/elegant_preview.jpg",
            "settings": {
                "font_size": 40,
                "font_color": "#8B4513",
                "text_position": "top",
                "background_overlay": "rgba(255,248,220,0.3)"
            }
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
    
    if video_id not in video_status:
        raise HTTPException(status_code=404, detail="视频不存在")
    
    if video_status[video_id] != "completed":
        raise HTTPException(status_code=400, detail="视频还未制作完成")
    
    file_path = f"../output/{video_id}.mp4"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="视频文件不存在")
    
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