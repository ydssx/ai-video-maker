from fastapi import APIRouter, HTTPException
import requests
import os
from typing import List, Dict

router = APIRouter()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

@router.get("/images/search")
async def search_images(query: str, count: int = 5) -> Dict:
    """搜索图片素材"""
    from services.content_service import content_service
    
    try:
        images = await content_service.search_images(query, count)
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片搜索失败: {str(e)}")

@router.post("/images/smart-search")
async def smart_image_search(request: dict) -> Dict:
    """智能图片搜索"""
    from services.content_service import content_service
    
    try:
        keywords = request.get("keywords", [])
        style = request.get("style", "educational")
        template_id = request.get("template_id", "default")
        
        images = await content_service.get_smart_images(keywords, style, template_id)
        return {"images": images}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"智能图片搜索失败: {str(e)}")

@router.get("/music/library")
async def get_music_library():
    """获取音乐库"""
    # 这里可以集成免费音乐 API 或本地音乐库
    music_library = [
        {
            "id": "upbeat_1",
            "name": "轻快节拍",
            "duration": 60,
            "genre": "电子",
            "mood": "积极",
            "url": "/assets/music/upbeat_1.mp3"
        },
        {
            "id": "calm_1", 
            "name": "平静舒缓",
            "duration": 90,
            "genre": "环境音乐",
            "mood": "放松",
            "url": "/assets/music/calm_1.mp3"
        },
        {
            "id": "corporate_1",
            "name": "商务专业",
            "duration": 120,
            "genre": "企业音乐",
            "mood": "专业",
            "url": "/assets/music/corporate_1.mp3"
        }
    ]
    return {"music": music_library}

@router.post("/music/recommendations")
async def get_music_recommendations(request: dict):
    """获取音乐推荐"""
    from services.content_service import content_service
    
    try:
        style = request.get("style", "educational")
        template_id = request.get("template_id", "default")
        duration = request.get("duration", 30.0)
        
        recommendations = content_service.get_music_recommendations(style, template_id, duration)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"音乐推荐失败: {str(e)}")

@router.get("/fonts")
async def get_fonts():
    """获取字体列表"""
    fonts = [
        {
            "id": "default",
            "name": "默认字体",
            "family": "Arial",
            "supports_chinese": True
        },
        {
            "id": "modern",
            "name": "现代简约",
            "family": "Helvetica",
            "supports_chinese": False
        },
        {
            "id": "chinese",
            "name": "中文字体",
            "family": "SimHei",
            "supports_chinese": True
        }
    ]
    return {"fonts": fonts}