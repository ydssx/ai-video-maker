"""
内容和素材服务
"""

import requests
import os
from typing import List, Dict
import random

class ContentService:
    def __init__(self):
        self.unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
        
    async def get_smart_images(self, keywords: List[str], style: str, template_id: str) -> List[Dict]:
        """智能图片推荐"""
        # 根据模板和风格调整搜索关键词
        enhanced_keywords = self.enhance_keywords(keywords, style, template_id)
        
        images = []
        for keyword in enhanced_keywords[:3]:  # 限制搜索数量
            keyword_images = await self.search_images(keyword, count=2)
            images.extend(keyword_images)
        
        # 去重并限制数量
        unique_images = self.deduplicate_images(images)
        return unique_images[:5]
    
    def enhance_keywords(self, keywords: List[str], style: str, template_id: str) -> List[str]:
        """根据风格和模板增强关键词"""
        enhanced = keywords.copy()
        
        # 根据风格添加修饰词
        style_modifiers = {
            "educational": ["professional", "clean", "modern"],
            "entertainment": ["colorful", "fun", "vibrant"],
            "commercial": ["business", "corporate", "sleek"],
            "news": ["serious", "formal", "documentary"]
        }
        
        # 根据模板添加修饰词
        template_modifiers = {
            "corporate": ["business", "office", "professional"],
            "startup": ["innovation", "technology", "modern"],
            "food": ["delicious", "fresh", "appetizing"],
            "travel": ["scenic", "adventure", "beautiful"],
            "fitness": ["active", "healthy", "energetic"],
            "beauty": ["elegant", "stylish", "glamorous"],
            "kids": ["colorful", "playful", "bright"],
            "academic": ["books", "study", "learning"]
        }
        
        # 添加风格修饰词
        if style in style_modifiers:
            for keyword in keywords:
                for modifier in style_modifiers[style]:
                    enhanced.append(f"{modifier} {keyword}")
        
        # 添加模板修饰词
        if template_id in template_modifiers:
            for keyword in keywords:
                for modifier in template_modifiers[template_id]:
                    enhanced.append(f"{modifier} {keyword}")
        
        return enhanced
    
    async def search_images(self, query: str, count: int = 5) -> List[Dict]:
        """搜索图片"""
        try:
            if self.unsplash_key and self.unsplash_key != "your_unsplash_key_here":
                return await self.search_unsplash(query, count)
            else:
                return self.get_placeholder_images(query, count)
        except Exception as e:
            print(f"图片搜索失败: {e}")
            return self.get_placeholder_images(query, count)
    
    async def search_unsplash(self, query: str, count: int) -> List[Dict]:
        """使用 Unsplash API 搜索"""
        url = "https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {self.unsplash_key}"}
        params = {
            "query": query,
            "per_page": count,
            "orientation": "landscape",
            "order_by": "relevant"
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            images = []
            for photo in data["results"]:
                images.append({
                    "id": photo["id"],
                    "url": photo["urls"]["regular"],
                    "thumb": photo["urls"]["thumb"],
                    "description": photo["description"] or photo["alt_description"] or query,
                    "author": photo["user"]["name"],
                    "download_url": photo["urls"]["regular"],
                    "source": "unsplash"
                })
            return images
        
        return self.get_placeholder_images(query, count)
    
    def get_placeholder_images(self, query: str, count: int) -> List[Dict]:
        """获取占位图片"""
        images = []
        for i in range(count):
            seed = hash(query + str(i)) % 1000
            images.append({
                "id": f"placeholder_{seed}",
                "url": f"https://picsum.photos/800/600?random={seed}",
                "thumb": f"https://picsum.photos/200/150?random={seed}",
                "description": f"占位图片 - {query}",
                "author": "Picsum",
                "download_url": f"https://picsum.photos/800/600?random={seed}",
                "source": "picsum"
            })
        return images
    
    def deduplicate_images(self, images: List[Dict]) -> List[Dict]:
        """去重图片"""
        seen_ids = set()
        unique_images = []
        
        for image in images:
            if image["id"] not in seen_ids:
                seen_ids.add(image["id"])
                unique_images.append(image)
        
        return unique_images
    
    def get_music_recommendations(self, style: str, template_id: str, duration: float) -> List[Dict]:
        """音乐推荐"""
        # 基础音乐库
        music_library = {
            "upbeat": {
                "name": "轻快节拍",
                "mood": "积极",
                "genres": ["pop", "electronic"],
                "suitable_for": ["commercial", "startup", "fitness"]
            },
            "calm": {
                "name": "平静舒缓",
                "mood": "放松",
                "genres": ["ambient", "classical"],
                "suitable_for": ["educational", "academic", "elegant"]
            },
            "corporate": {
                "name": "商务专业",
                "mood": "专业",
                "genres": ["corporate", "ambient"],
                "suitable_for": ["corporate", "finance", "business"]
            },
            "inspiring": {
                "name": "励志激昂",
                "mood": "激励",
                "genres": ["orchestral", "rock"],
                "suitable_for": ["startup", "fitness", "skill"]
            },
            "playful": {
                "name": "活泼可爱",
                "mood": "欢快",
                "genres": ["pop", "children"],
                "suitable_for": ["kids", "entertainment", "beauty"]
            }
        }
        
        # 根据模板和风格推荐音乐
        recommendations = []
        for music_id, music_info in music_library.items():
            if template_id in music_info["suitable_for"] or style in music_info["suitable_for"]:
                recommendations.append({
                    "id": music_id,
                    "name": music_info["name"],
                    "mood": music_info["mood"],
                    "duration": min(duration, 120),  # 最长2分钟
                    "url": f"/assets/music/{music_id}.mp3",
                    "preview_url": f"/assets/music/{music_id}_preview.mp3"
                })
        
        # 如果没有匹配的，返回默认推荐
        if not recommendations:
            recommendations.append({
                "id": "default",
                "name": "默认背景音乐",
                "mood": "中性",
                "duration": duration,
                "url": "/assets/music/default.mp3",
                "preview_url": "/assets/music/default_preview.mp3"
            })
        
        return recommendations[:3]  # 最多返回3个推荐

# 全局内容服务实例
content_service = ContentService()