"""
用户素材管理 API
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
import os
import uuid
import json
from datetime import datetime
from typing import List, Optional
import shutil
from PIL import Image
import mimetypes

router = APIRouter()

# 用户素材存储目录
USER_ASSETS_DIR = "../assets/user"
ASSETS_INDEX_FILE = "../data/user_assets.json"

def ensure_assets_dir():
    """确保素材目录存在"""
    os.makedirs(USER_ASSETS_DIR, exist_ok=True)
    os.makedirs(f"{USER_ASSETS_DIR}/images", exist_ok=True)
    os.makedirs(f"{USER_ASSETS_DIR}/videos", exist_ok=True)
    os.makedirs(f"{USER_ASSETS_DIR}/audio", exist_ok=True)
    os.makedirs("../data", exist_ok=True)

def load_assets_index():
    """加载素材索引"""
    ensure_assets_dir()
    try:
        if os.path.exists(ASSETS_INDEX_FILE):
            with open(ASSETS_INDEX_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载素材索引失败: {e}")
    
    return {"assets": []}

def save_assets_index(index_data):
    """保存素材索引"""
    ensure_assets_dir()
    try:
        with open(ASSETS_INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        print(f"保存素材索引失败: {e}")

def get_file_type(filename: str) -> str:
    """根据文件名判断类型"""
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
    return 'unknown'

def create_thumbnail(file_path: str, file_type: str) -> Optional[str]:
    """创建缩略图"""
    try:
        if file_type == 'image':
            # 为图片创建缩略图
            with Image.open(file_path) as img:
                img.thumbnail((200, 150), Image.Resampling.LANCZOS)
                thumb_path = file_path.replace('.', '_thumb.')
                img.save(thumb_path, 'JPEG', quality=85)
                return thumb_path
        elif file_type == 'video':
            # 为视频创建缩略图（需要 ffmpeg）
            import subprocess
            thumb_path = file_path.replace('.', '_thumb.jpg')
            try:
                subprocess.run([
                    'ffmpeg', '-i', file_path, '-ss', '00:00:01.000',
                    '-vframes', '1', '-y', thumb_path
                ], check=True, capture_output=True)
                return thumb_path
            except subprocess.CalledProcessError:
                return None
    except Exception as e:
        print(f"创建缩略图失败: {e}")
    
    return None

@router.post("/upload")
async def upload_asset(
    file: UploadFile = File(...),
    tags: str = Form(""),
    category: str = Form("general")
):
    """上传用户素材"""
    try:
        # 验证文件类型
        file_type = get_file_type(file.filename)
        if file_type == 'unknown':
            raise HTTPException(status_code=400, detail="不支持的文件类型")
        
        # 验证文件大小（50MB 限制）
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(status_code=400, detail="文件大小不能超过 50MB")
        
        # 生成唯一文件名
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        new_filename = f"{file_id}{file_extension}"
        
        # 保存文件
        file_dir = f"{USER_ASSETS_DIR}/{file_type}s"
        file_path = os.path.join(file_dir, new_filename)
        
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # 创建缩略图
        thumb_path = create_thumbnail(file_path, file_type)
        
        # 更新索引
        index_data = load_assets_index()
        asset_info = {
            "id": file_id,
            "original_name": file.filename,
            "filename": new_filename,
            "file_path": file_path,
            "thumb_path": thumb_path,
            "type": file_type,
            "size": file_size,
            "tags": [tag.strip() for tag in tags.split(',') if tag.strip()],
            "category": category,
            "upload_time": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        index_data["assets"].append(asset_info)
        save_assets_index(index_data)
        
        return {
            "asset": asset_info,
            "message": "上传成功",
            "url": f"/api/user-assets/file/{file_id}",
            "thumb_url": f"/api/user-assets/thumb/{file_id}" if thumb_path else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@router.get("/list")
async def list_user_assets(
    asset_type: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """获取用户素材列表"""
    try:
        index_data = load_assets_index()
        assets = index_data["assets"]
        
        # 过滤
        if asset_type:
            assets = [a for a in assets if a["type"] == asset_type]
        
        if category and category != "all":
            assets = [a for a in assets if a["category"] == category]
        
        if search:
            search_lower = search.lower()
            assets = [a for a in assets if 
                     search_lower in a["original_name"].lower() or
                     any(search_lower in tag.lower() for tag in a["tags"])]
        
        # 添加访问 URL
        for asset in assets:
            asset["url"] = f"/api/user-assets/file/{asset['id']}"
            asset["thumb_url"] = f"/api/user-assets/thumb/{asset['id']}" if asset.get("thumb_path") else None
        
        return {"assets": assets}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取素材列表失败: {str(e)}")

@router.get("/file/{asset_id}")
async def get_asset_file(asset_id: str):
    """获取素材文件"""
    try:
        index_data = load_assets_index()
        asset = next((a for a in index_data["assets"] if a["id"] == asset_id), None)
        
        if not asset:
            raise HTTPException(status_code=404, detail="素材不存在")
        
        if not os.path.exists(asset["file_path"]):
            raise HTTPException(status_code=404, detail="素材文件不存在")
        
        return FileResponse(
            path=asset["file_path"],
            filename=asset["original_name"],
            media_type=f"{asset['type']}/*"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取素材文件失败: {str(e)}")

@router.get("/thumb/{asset_id}")
async def get_asset_thumbnail(asset_id: str):
    """获取素材缩略图"""
    try:
        index_data = load_assets_index()
        asset = next((a for a in index_data["assets"] if a["id"] == asset_id), None)
        
        if not asset or not asset.get("thumb_path"):
            raise HTTPException(status_code=404, detail="缩略图不存在")
        
        if not os.path.exists(asset["thumb_path"]):
            raise HTTPException(status_code=404, detail="缩略图文件不存在")
        
        return FileResponse(
            path=asset["thumb_path"],
            media_type="image/jpeg"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缩略图失败: {str(e)}")

@router.delete("/{asset_id}")
async def delete_asset(asset_id: str):
    """删除用户素材"""
    try:
        index_data = load_assets_index()
        asset = next((a for a in index_data["assets"] if a["id"] == asset_id), None)
        
        if not asset:
            raise HTTPException(status_code=404, detail="素材不存在")
        
        # 删除文件
        if os.path.exists(asset["file_path"]):
            os.remove(asset["file_path"])
        
        if asset.get("thumb_path") and os.path.exists(asset["thumb_path"]):
            os.remove(asset["thumb_path"])
        
        # 从索引中移除
        index_data["assets"] = [a for a in index_data["assets"] if a["id"] != asset_id]
        save_assets_index(index_data)
        
        return {"message": "删除成功"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除素材失败: {str(e)}")

@router.put("/{asset_id}/tags")
async def update_asset_tags(asset_id: str, tags: List[str]):
    """更新素材标签"""
    try:
        index_data = load_assets_index()
        
        for asset in index_data["assets"]:
            if asset["id"] == asset_id:
                asset["tags"] = tags
                asset["updated_at"] = datetime.now().isoformat()
                break
        else:
            raise HTTPException(status_code=404, detail="素材不存在")
        
        save_assets_index(index_data)
        return {"message": "标签更新成功"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新标签失败: {str(e)}")

@router.get("/categories")
async def get_asset_categories():
    """获取素材分类"""
    categories = [
        {"id": "all", "name": "全部分类"},
        {"id": "nature", "name": "自然风景"},
        {"id": "business", "name": "商务办公"},
        {"id": "people", "name": "人物肖像"},
        {"id": "technology", "name": "科技数码"},
        {"id": "food", "name": "美食餐饮"},
        {"id": "travel", "name": "旅游出行"},
        {"id": "lifestyle", "name": "生活方式"},
        {"id": "abstract", "name": "抽象艺术"}
    ]
    return {"categories": categories}