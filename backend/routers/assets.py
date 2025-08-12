from fastapi import APIRouter, HTTPException
import requests
import os
from typing import List, Dict

router = APIRouter()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

@router.get("/images/search")
async def search_images(query: str, count: int = 5) -> Dict:
    """搜索图片素材"""
    try:
        # 使用 Unsplash API 搜索图片
        if UNSPLASH_ACCESS_KEY:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
            params = {
                "query": query,
                "per_page": count,
                "orientation": "landscape"
            }
            
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                images = []
                for photo in data["results"]:
                    images.append({
                        "id": photo["id"],
                        "url": photo["urls"]["regular"],
                        "thumb": photo["urls"]["thumb"],
                        "description": photo["description"] or photo["alt_description"],
                        "author": photo["user"]["name"],
                        "download_url": photo["links"]["download"]
                    })
                return {"images": images}
        
        # 如果没有配置 Unsplash，返回默认图片
        default_images = []
        for i in range(count):
            default_images.append({
                "id": f"default_{i}",
                "url": f"https://picsum.photos/800/600?random={hash(query + str(i)) % 1000}",
                "thumb": f"https://picsum.photos/200/150?random={hash(query + str(i)) % 1000}",
                "description": f"默认图片 - {query}",
                "author": "Picsum",
                "download_url": f"https://picsum.photos/800/600?random={hash(query + str(i)) % 1000}"
            })
        
        return {"images": default_images}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图片搜索失败: {str(e)}")

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