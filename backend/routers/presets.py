"""
视频预设管理
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import os
from datetime import datetime

router = APIRouter()

# 预设存储文件
PRESETS_FILE = "../data/presets.json"

class VideoPreset(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    template_id: str
    voice_config: Dict
    style: str
    duration: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    usage_count: int = 0

def ensure_presets_file():
    """确保预设文件存在"""
    os.makedirs("../data", exist_ok=True)
    if not os.path.exists(PRESETS_FILE):
        with open(PRESETS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"presets": []}, f, ensure_ascii=False, indent=2)

def load_presets() -> List[Dict]:
    """加载预设"""
    ensure_presets_file()
    try:
        with open(PRESETS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("presets", [])
    except Exception as e:
        print(f"加载预设失败: {e}")
        return []

def save_presets(presets: List[Dict]):
    """保存预设"""
    ensure_presets_file()
    try:
        with open(PRESETS_FILE, 'w', encoding='utf-8') as f:
            json.dump({"presets": presets}, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        print(f"保存预设失败: {e}")

@router.get("/")
async def get_presets():
    """获取所有预设"""
    presets = load_presets()
    return {"presets": presets}

@router.post("/")
async def create_preset(preset: VideoPreset):
    """创建新预设"""
    import uuid
    
    presets = load_presets()
    
    # 生成ID和时间戳
    preset_dict = preset.dict()
    preset_dict["id"] = str(uuid.uuid4())
    preset_dict["created_at"] = datetime.now().isoformat()
    preset_dict["updated_at"] = datetime.now().isoformat()
    preset_dict["usage_count"] = 0
    
    presets.append(preset_dict)
    save_presets(presets)
    
    return {"preset": preset_dict, "message": "预设创建成功"}

@router.get("/{preset_id}")
async def get_preset(preset_id: str):
    """获取特定预设"""
    presets = load_presets()
    
    for preset in presets:
        if preset["id"] == preset_id:
            return {"preset": preset}
    
    raise HTTPException(status_code=404, detail="预设不存在")

@router.put("/{preset_id}")
async def update_preset(preset_id: str, preset: VideoPreset):
    """更新预设"""
    presets = load_presets()
    
    for i, existing_preset in enumerate(presets):
        if existing_preset["id"] == preset_id:
            preset_dict = preset.dict()
            preset_dict["id"] = preset_id
            preset_dict["created_at"] = existing_preset["created_at"]
            preset_dict["updated_at"] = datetime.now().isoformat()
            preset_dict["usage_count"] = existing_preset.get("usage_count", 0)
            
            presets[i] = preset_dict
            save_presets(presets)
            
            return {"preset": preset_dict, "message": "预设更新成功"}
    
    raise HTTPException(status_code=404, detail="预设不存在")

@router.delete("/{preset_id}")
async def delete_preset(preset_id: str):
    """删除预设"""
    presets = load_presets()
    
    for i, preset in enumerate(presets):
        if preset["id"] == preset_id:
            deleted_preset = presets.pop(i)
            save_presets(presets)
            return {"message": "预设删除成功", "deleted_preset": deleted_preset}
    
    raise HTTPException(status_code=404, detail="预设不存在")

@router.post("/{preset_id}/use")
async def use_preset(preset_id: str):
    """使用预设（增加使用计数）"""
    presets = load_presets()
    
    for i, preset in enumerate(presets):
        if preset["id"] == preset_id:
            presets[i]["usage_count"] = preset.get("usage_count", 0) + 1
            presets[i]["updated_at"] = datetime.now().isoformat()
            save_presets(presets)
            
            return {"preset": presets[i], "message": "预设使用成功"}
    
    raise HTTPException(status_code=404, detail="预设不存在")

@router.get("/popular/top")
async def get_popular_presets(limit: int = 10):
    """获取热门预设"""
    presets = load_presets()
    
    # 按使用次数排序
    popular_presets = sorted(presets, key=lambda x: x.get("usage_count", 0), reverse=True)
    
    return {"presets": popular_presets[:limit]}

@router.post("/default/create")
async def create_default_presets():
    """创建默认预设"""
    default_presets = [
        {
            "name": "商务演示",
            "description": "适合商务演示和企业宣传的专业风格",
            "template_id": "corporate",
            "voice_config": {
                "provider": "gtts",
                "voice": "zh",
                "speed": 1.0,
                "enabled": True
            },
            "style": "commercial",
            "duration": "30s"
        },
        {
            "name": "教育科普",
            "description": "适合知识分享和教学内容的清晰风格",
            "template_id": "academic",
            "voice_config": {
                "provider": "gtts",
                "voice": "zh",
                "speed": 0.9,
                "enabled": True
            },
            "style": "educational",
            "duration": "60s"
        },
        {
            "name": "生活分享",
            "description": "适合生活方式和个人分享的温馨风格",
            "template_id": "elegant",
            "voice_config": {
                "provider": "gtts",
                "voice": "zh",
                "speed": 1.1,
                "enabled": True
            },
            "style": "entertainment",
            "duration": "30s"
        },
        {
            "name": "科技创新",
            "description": "适合科技产品和创新内容的现代风格",
            "template_id": "tech",
            "voice_config": {
                "provider": "gtts",
                "voice": "zh",
                "speed": 1.0,
                "enabled": True
            },
            "style": "commercial",
            "duration": "30s"
        }
    ]
    
    created_presets = []
    for preset_data in default_presets:
        preset = VideoPreset(**preset_data)
        
        # 检查是否已存在同名预设
        existing_presets = load_presets()
        if not any(p["name"] == preset.name for p in existing_presets):
            response = await create_preset(preset)
            created_presets.append(response["preset"])
    
    return {
        "message": f"创建了 {len(created_presets)} 个默认预设",
        "presets": created_presets
    }