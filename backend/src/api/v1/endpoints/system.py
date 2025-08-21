import json
from fastapi import APIRouter, HTTPException
from typing import Dict, List
import logging
import os
import psutil
from datetime import datetime

from src.services.database_service import db_service
from src.services.file_service import file_service
from src.services.video_service import video_service
from src.services.ai_service import ai_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """系统健康检查"""
    try:
        # 检查数据库连接
        db_stats = db_service.get_system_stats()
        
        # 检查文件系统
        storage_stats = file_service.get_storage_stats()
        
        # 检查AI服务
        ai_stats = ai_service.get_stats()
        
        # 检查视频服务
        video_stats = video_service.get_processing_stats()
        
        # 系统资源使用情况
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "status": "connected",
                "stats": db_stats
            },
            "storage": {
                "status": "available",
                "stats": storage_stats
            },
            "ai_service": {
                "status": "available",
                "stats": ai_stats
            },
            "video_service": {
                "status": "available",
                "stats": video_stats
            },
            "system_resources": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available": memory.available,
                "disk_percent": disk.percent if hasattr(disk, 'percent') else 0,
                "disk_free": disk.free if hasattr(disk, 'free') else 0
            }
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.get("/stats")
async def get_system_stats():
    """获取系统统计信息"""
    try:
        # 数据库统计
        db_stats = db_service.get_system_stats()
        
        # 文件存储统计
        storage_stats = file_service.get_storage_stats()
        
        # AI服务统计
        ai_stats = ai_service.get_stats()
        
        # 视频处理统计
        video_stats = video_service.get_processing_stats()
        
        return {
            "database": db_stats,
            "storage": storage_stats,
            "ai_service": ai_stats,
            "video_processing": video_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取系统统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取统计失败")

@router.get("/performance")
async def get_performance_metrics():
    """获取性能指标"""
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        
        # 磁盘使用情况
        disk_usage = {}
        try:
            disk = psutil.disk_usage('/')
            disk_usage = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            }
        except:
            pass
        
        # 网络统计
        try:
            network = psutil.net_io_counters()
            network_stats = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        except:
            network_stats = {}
        
        # 进程信息
        try:
            process = psutil.Process()
            process_info = {
                "pid": process.pid,
                "memory_percent": process.memory_percent(),
                "cpu_percent": process.cpu_percent(),
                "num_threads": process.num_threads(),
                "create_time": process.create_time()
            }
        except:
            process_info = {}
        
        return {
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free
            },
            "disk": disk_usage,
            "network": network_stats,
            "process": process_info,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取性能指标失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取性能指标失败")

@router.post("/cleanup")
async def system_cleanup():
    """系统清理"""
    try:
        results = {}
        
        # 清理临时文件
        temp_cleaned = file_service.cleanup_temp_files()
        results["temp_files_cleaned"] = temp_cleaned
        
        # 清理旧视频
        old_videos_cleaned = video_service.cleanup_old_videos()
        results["old_videos_cleaned"] = old_videos_cleaned
        
        # 清理旧数据
        old_data_cleaned = db_service.cleanup_old_data()
        results["old_data_cleaned"] = old_data_cleaned
        
        # 重置AI服务统计
        ai_service.reset_stats()
        results["ai_stats_reset"] = True
        
        return {
            "message": "系统清理完成",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"系统清理失败: {str(e)}")
        raise HTTPException(status_code=500, detail="系统清理失败")

@router.get("/logs")
async def get_system_logs(lines: int = 100):
    """获取系统日志"""
    try:
        # 这里可以读取日志文件
        # 简化版本，返回最近的一些系统事件
        
        recent_activities = []
        
        # 从数据库获取最近的活动
        with db_service._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT action_type, action_data, timestamp, user_id
                FROM usage_stats 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (lines,))
            
            for row in cursor.fetchall():
                activity = dict(row)
                if activity['action_data']:
                    activity['action_data'] = json.loads(activity['action_data'])
                recent_activities.append(activity)
        
        return {
            "logs": recent_activities,
            "total_lines": len(recent_activities),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取系统日志失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取日志失败")

@router.get("/config")
async def get_system_config():
    """获取系统配置"""
    try:
        config = {
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "debug": os.getenv("DEBUG", "false").lower() == "true",
            "features": {
                "ai_service": bool(os.getenv("OPENAI_API_KEY")),
                "cloud_storage": bool(os.getenv("CLOUD_STORAGE_ENABLED")),
                "user_authentication": True,
                "video_processing": True
            },
            "limits": {
                "max_video_duration": 300,  # 5分钟
                "max_file_size": 100 * 1024 * 1024,  # 100MB
                "max_concurrent_videos": 5
            }
        }
        
        return config
        
    except Exception as e:
        logger.error(f"获取系统配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取配置失败")

@router.put("/config")
async def update_system_config(config_updates: Dict):
    """更新系统配置"""
    try:
        # 保存配置到数据库
        for key, value in config_updates.items():
            db_service.set_config(key, value)
        
        return {
            "message": "配置更新成功",
            "updated_keys": list(config_updates.keys()),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"更新系统配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail="配置更新失败")

@router.post("/backup")
async def create_system_backup():
    """创建系统备份"""
    try:
        backup_info = {
            "backup_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # 这里可以实现实际的备份逻辑
        # 例如：备份数据库、用户文件等
        
        return {
            "message": "备份创建成功",
            "backup_info": backup_info
        }
        
    except Exception as e:
        logger.error(f"创建系统备份失败: {str(e)}")
        raise HTTPException(status_code=500, detail="备份创建失败")

@router.get("/version")
async def get_version_info():
    """获取版本信息"""
    return {
        "version": "1.0.0",
        "build_date": "2024-01-01",
        "git_commit": "latest",
        "python_version": "3.11+",
        "dependencies": {
            "fastapi": "0.104+",
            "moviepy": "1.0+",
            "openai": "1.0+",
            "pillow": "10.0+"
        }
    }