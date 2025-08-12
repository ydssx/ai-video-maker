from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
import os
import shutil
import uuid
from pathlib import Path
import mimetypes
from typing import List, Optional
import json
from datetime import datetime
import mutagen
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.wave import WAVE
from mutagen.flac import FLAC

router = APIRouter(prefix="/api/audio", tags=["audio"])

# 音频文件存储目录
AUDIO_UPLOAD_DIR = Path("uploads/audio")
AUDIO_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 音频元数据存储文件
AUDIO_METADATA_FILE = AUDIO_UPLOAD_DIR / "metadata.json"

# 支持的音频格式
SUPPORTED_AUDIO_FORMATS = {
    'audio/mpeg': ['.mp3'],
    'audio/wav': ['.wav'],
    'audio/x-wav': ['.wav'],
    'audio/mp4': ['.m4a', '.mp4'],
    'audio/aac': ['.aac'],
    'audio/ogg': ['.ogg'],
    'audio/flac': ['.flac'],
    'audio/webm': ['.webm']
}

def load_audio_metadata():
    """加载音频元数据"""
    if AUDIO_METADATA_FILE.exists():
        try:
            with open(AUDIO_METADATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_audio_metadata(metadata):
    """保存音频元数据"""
    with open(AUDIO_METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

def get_audio_info(file_path):
    """获取音频文件信息"""
    try:
        audio_file = mutagen.File(file_path)
        if audio_file is None:
            return None
        
        info = {
            'duration': getattr(audio_file.info, 'length', 0),
            'bitrate': getattr(audio_file.info, 'bitrate', 0),
            'sample_rate': getattr(audio_file.info, 'sample_rate', 0),
            'channels': getattr(audio_file.info, 'channels', 0)
        }
        
        # 获取标签信息
        if audio_file.tags:
            info.update({
                'title': audio_file.tags.get('TIT2', [None])[0] if 'TIT2' in audio_file.tags else None,
                'artist': audio_file.tags.get('TPE1', [None])[0] if 'TPE1' in audio_file.tags else None,
                'album': audio_file.tags.get('TALB', [None])[0] if 'TALB' in audio_file.tags else None
            })
        
        return info
    except Exception as e:
        print(f"获取音频信息失败: {e}")
        return None

@router.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    category: str = "music",
    description: Optional[str] = None
):
    """上传音频文件"""
    
    # 检查文件类型
    if file.content_type not in SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的音频格式: {file.content_type}"
        )
    
    # 生成唯一文件名
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in SUPPORTED_AUDIO_FORMATS.get(file.content_type, []):
        # 根据MIME类型确定扩展名
        file_extension = SUPPORTED_AUDIO_FORMATS[file.content_type][0]
    
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = AUDIO_UPLOAD_DIR / unique_filename
    
    try:
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 获取音频信息
        audio_info = get_audio_info(file_path)
        
        # 创建音频记录
        audio_record = {
            'id': str(uuid.uuid4()),
            'filename': unique_filename,
            'original_name': file.filename,
            'category': category,
            'description': description or "",
            'file_size': file_path.stat().st_size,
            'content_type': file.content_type,
            'upload_time': datetime.now().isoformat(),
            'url': f"/api/audio/file/{unique_filename}",
            'audio_info': audio_info or {}
        }
        
        # 保存到元数据
        metadata = load_audio_metadata()
        metadata[audio_record['id']] = audio_record
        save_audio_metadata(metadata)
        
        return {
            "success": True,
            "message": "音频文件上传成功",
            "audio": audio_record
        }
        
    except Exception as e:
        # 清理失败的文件
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"文件上传失败: {str(e)}")

@router.get("/list")
async def list_audio_files(
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """获取音频文件列表"""
    
    metadata = load_audio_metadata()
    audio_list = list(metadata.values())
    
    # 按类别筛选
    if category:
        audio_list = [audio for audio in audio_list if audio.get('category') == category]
    
    # 按上传时间排序
    audio_list.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
    
    # 分页
    total = len(audio_list)
    audio_list = audio_list[offset:offset + limit]
    
    return {
        "success": True,
        "audio_files": audio_list,
        "total": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/file/{filename}")
async def get_audio_file(filename: str):
    """获取音频文件"""
    
    file_path = AUDIO_UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    # 确定MIME类型
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type:
        mime_type = "audio/mpeg"
    
    return FileResponse(
        path=str(file_path),
        media_type=mime_type,
        filename=filename
    )

@router.get("/{audio_id}")
async def get_audio_info_by_id(audio_id: str):
    """根据ID获取音频信息"""
    
    metadata = load_audio_metadata()
    if audio_id not in metadata:
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    return {
        "success": True,
        "audio": metadata[audio_id]
    }

@router.put("/{audio_id}")
async def update_audio_info(
    audio_id: str,
    category: Optional[str] = None,
    description: Optional[str] = None
):
    """更新音频信息"""
    
    metadata = load_audio_metadata()
    if audio_id not in metadata:
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    audio_record = metadata[audio_id]
    
    if category is not None:
        audio_record['category'] = category
    if description is not None:
        audio_record['description'] = description
    
    audio_record['updated_time'] = datetime.now().isoformat()
    
    save_audio_metadata(metadata)
    
    return {
        "success": True,
        "message": "音频信息更新成功",
        "audio": audio_record
    }

@router.delete("/{audio_id}")
async def delete_audio(audio_id: str):
    """删除音频文件"""
    
    metadata = load_audio_metadata()
    if audio_id not in metadata:
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    audio_record = metadata[audio_id]
    file_path = AUDIO_UPLOAD_DIR / audio_record['filename']
    
    try:
        # 删除文件
        if file_path.exists():
            file_path.unlink()
        
        # 从元数据中删除
        del metadata[audio_id]
        save_audio_metadata(metadata)
        
        return {
            "success": True,
            "message": "音频文件删除成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@router.get("/categories/list")
async def list_audio_categories():
    """获取音频分类列表"""
    
    metadata = load_audio_metadata()
    categories = set()
    
    for audio in metadata.values():
        if audio.get('category'):
            categories.add(audio['category'])
    
    return {
        "success": True,
        "categories": sorted(list(categories))
    }

@router.post("/analyze/{audio_id}")
async def analyze_audio(audio_id: str):
    """分析音频文件（获取详细信息）"""
    
    metadata = load_audio_metadata()
    if audio_id not in metadata:
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    audio_record = metadata[audio_id]
    file_path = AUDIO_UPLOAD_DIR / audio_record['filename']
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="音频文件不存在")
    
    # 重新分析音频信息
    audio_info = get_audio_info(file_path)
    
    if audio_info:
        audio_record['audio_info'] = audio_info
        audio_record['analyzed_time'] = datetime.now().isoformat()
        save_audio_metadata(metadata)
    
    return {
        "success": True,
        "message": "音频分析完成",
        "audio_info": audio_info
    }

@router.post("/batch-upload")
async def batch_upload_audio(
    files: List[UploadFile] = File(...),
    category: str = "music"
):
    """批量上传音频文件"""
    
    results = []
    
    for file in files:
        try:
            # 检查文件类型
            if file.content_type not in SUPPORTED_AUDIO_FORMATS:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"不支持的音频格式: {file.content_type}"
                })
                continue
            
            # 生成唯一文件名
            file_extension = Path(file.filename).suffix.lower()
            if file_extension not in SUPPORTED_AUDIO_FORMATS.get(file.content_type, []):
                file_extension = SUPPORTED_AUDIO_FORMATS[file.content_type][0]
            
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = AUDIO_UPLOAD_DIR / unique_filename
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 获取音频信息
            audio_info = get_audio_info(file_path)
            
            # 创建音频记录
            audio_record = {
                'id': str(uuid.uuid4()),
                'filename': unique_filename,
                'original_name': file.filename,
                'category': category,
                'description': "",
                'file_size': file_path.stat().st_size,
                'content_type': file.content_type,
                'upload_time': datetime.now().isoformat(),
                'url': f"/api/audio/file/{unique_filename}",
                'audio_info': audio_info or {}
            }
            
            # 保存到元数据
            metadata = load_audio_metadata()
            metadata[audio_record['id']] = audio_record
            save_audio_metadata(metadata)
            
            results.append({
                "filename": file.filename,
                "success": True,
                "audio": audio_record
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    success_count = sum(1 for r in results if r['success'])
    
    return {
        "success": True,
        "message": f"批量上传完成，成功: {success_count}/{len(files)}",
        "results": results
    }