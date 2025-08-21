from fastapi import APIRouter, HTTPException
from typing import Optional
import os
from pathlib import Path
import uuid
from datetime import datetime

from src.services.cloud_storage import cloud_storage

router = APIRouter(prefix="/api/cloud-storage", tags=["cloud-storage"])

async def upload_video_to_cloud(local_path: str, video_id: str) -> dict:
    """内部函数：上传视频到云存储"""
    if not cloud_storage.is_enabled():
        return {'success': False, 'error': 'Cloud storage not enabled'}
    
    try:
        # 准备元数据
        metadata = {
            'video_id': video_id,
            'upload_time': datetime.now().isoformat(),
            'file_type': 'video',
            'source': 'ai_video_maker'
        }
        
        # 生成远程路径
        provider_instance = cloud_storage.get_provider()
        if not provider_instance:
            return {'success': False, 'error': 'No cloud storage provider available'}
        
        remote_path = provider_instance.generate_remote_path(f"{video_id}.mp4", "videos")
        
        # 上传到云存储
        result = await cloud_storage.upload_file(local_path, remote_path, None, metadata)
        
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}

@router.get("/download/{video_id}")
async def get_video_download_url(video_id: str, expires_in: int = 3600):
    """获取视频下载URL"""
    
    if not cloud_storage.is_enabled():
        # 如果云存储未启用，返回本地文件URL
        local_path = f"/output/{video_id}.mp4"
        return {
            "success": True,
            "url": local_path,
            "storage_type": "local",
            "expires_in": None
        }
    
    try:
        # 生成云存储中的文件路径
        provider_instance = cloud_storage.get_provider()
        if not provider_instance:
            raise HTTPException(status_code=500, detail="云存储提供商不可用")
        
        remote_path = provider_instance.generate_remote_path(f"{video_id}.mp4", "videos")
        
        # 获取下载URL
        url = await cloud_storage.get_file_url(remote_path, expires_in)
        if url:
            return {
                "success": True,
                "url": url,
                "storage_type": "cloud",
                "expires_in": expires_in
            }
        else:
            # 如果云存储中没有文件，尝试返回本地文件
            local_path = f"/output/{video_id}.mp4"
            return {
                "success": True,
                "url": local_path,
                "storage_type": "local",
                "expires_in": None
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取下载链接失败: {str(e)}")

async def cleanup_local_video(video_id: str):
    """清理本地视频文件（上传到云存储后）"""
    try:
        from config import settings
        local_path = Path(settings.output_path) / f"{video_id}.mp4"
        if local_path.exists():
            local_path.unlink()
            return True
    except Exception as e:
        print(f"清理本地文件失败: {e}")
    return False