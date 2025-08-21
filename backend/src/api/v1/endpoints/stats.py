from fastapi import APIRouter, HTTPException
from datetime import datetime, date
from typing import Dict
import json
import os
from models import UserStats, UsageQuota, SystemStats

router = APIRouter()

# 简单的文件存储（生产环境应使用数据库），统一到根 data 目录
from src.core.config import settings
from pathlib import Path
DATA_DIR = Path(settings.output_path).parent
STATS_FILE = str(DATA_DIR / "stats.json")
QUOTA_FILE = str(DATA_DIR / "quotas.json")

def ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(str(DATA_DIR), exist_ok=True)

def load_stats() -> Dict:
    """加载统计数据"""
    ensure_data_dir()
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载统计数据失败: {e}")
    
    return {
        "user_stats": {},
        "system_stats": {
            "total_users": 0,
            "total_scripts": 0,
            "total_videos": 0,
            "total_duration": 0.0,
            "active_users_today": 0
        }
    }

def save_stats(stats: Dict):
    """保存统计数据"""
    ensure_data_dir()
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        print(f"保存统计数据失败: {e}")

def load_quotas() -> Dict:
    """加载配额数据"""
    ensure_data_dir()
    try:
        if os.path.exists(QUOTA_FILE):
            with open(QUOTA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"加载配额数据失败: {e}")
    
    return {}

def save_quotas(quotas: Dict):
    """保存配额数据"""
    ensure_data_dir()
    try:
        with open(QUOTA_FILE, 'w', encoding='utf-8') as f:
            json.dump(quotas, f, ensure_ascii=False, indent=2, default=str)
    except Exception as e:
        print(f"保存配额数据失败: {e}")

def get_user_id() -> str:
    """获取用户ID（简化版，实际应用中应该从认证系统获取）"""
    return "anonymous_user"

@router.get("/user-stats")
async def get_user_stats():
    """获取用户统计信息"""
    user_id = get_user_id()
    stats = load_stats()
    
    user_stats = stats["user_stats"].get(user_id, {
        "scripts_generated": 0,
        "videos_created": 0,
        "total_duration": 0.0,
        "last_activity": None
    })
    
    return {"stats": user_stats}

@router.get("/user-quota")
async def get_user_quota():
    """获取用户配额信息"""
    user_id = get_user_id()
    quotas = load_quotas()
    today = date.today().isoformat()
    
    user_quota = quotas.get(user_id, {})
    
    # 重置每日配额（如果是新的一天）
    if user_quota.get("last_reset_date") != today:
        user_quota.update({
            "daily_scripts": 10,
            "daily_videos": 5,
            "monthly_scripts": 100,
            "monthly_videos": 50,
            "used_today_scripts": 0,
            "used_today_videos": 0,
            "last_reset_date": today
        })
        quotas[user_id] = user_quota
        save_quotas(quotas)
    
    return {"quota": user_quota}

@router.post("/record-script")
async def record_script_generation():
    """记录脚本生成"""
    user_id = get_user_id()
    
    # 检查配额
    quotas = load_quotas()
    user_quota = quotas.get(user_id, {})
    
    if user_quota.get("used_today_scripts", 0) >= user_quota.get("daily_scripts", 10):
        raise HTTPException(status_code=429, detail="今日脚本生成次数已用完")
    
    # 更新统计
    stats = load_stats()
    
    # 更新用户统计
    if user_id not in stats["user_stats"]:
        stats["user_stats"][user_id] = {
            "scripts_generated": 0,
            "videos_created": 0,
            "total_duration": 0.0,
            "last_activity": None
        }
    
    stats["user_stats"][user_id]["scripts_generated"] += 1
    stats["user_stats"][user_id]["last_activity"] = datetime.now().isoformat()
    
    # 更新系统统计
    stats["system_stats"]["total_scripts"] += 1
    
    save_stats(stats)
    
    # 更新配额
    user_quota["used_today_scripts"] = user_quota.get("used_today_scripts", 0) + 1
    user_quota["used_month_scripts"] = user_quota.get("used_month_scripts", 0) + 1
    quotas[user_id] = user_quota
    save_quotas(quotas)
    
    return {"success": True, "remaining": user_quota.get("daily_scripts", 10) - user_quota["used_today_scripts"]}

@router.post("/record-video")
async def record_video_creation(duration: float = 30.0):
    """记录视频创建"""
    user_id = get_user_id()
    
    # 检查配额
    quotas = load_quotas()
    user_quota = quotas.get(user_id, {})
    
    if user_quota.get("used_today_videos", 0) >= user_quota.get("daily_videos", 5):
        raise HTTPException(status_code=429, detail="今日视频制作次数已用完")
    
    # 更新统计
    stats = load_stats()
    
    # 更新用户统计
    if user_id not in stats["user_stats"]:
        stats["user_stats"][user_id] = {
            "scripts_generated": 0,
            "videos_created": 0,
            "total_duration": 0.0,
            "last_activity": None
        }
    
    stats["user_stats"][user_id]["videos_created"] += 1
    stats["user_stats"][user_id]["total_duration"] += duration
    stats["user_stats"][user_id]["last_activity"] = datetime.now().isoformat()
    
    # 更新系统统计
    stats["system_stats"]["total_videos"] += 1
    stats["system_stats"]["total_duration"] += duration
    
    save_stats(stats)
    
    # 更新配额
    user_quota["used_today_videos"] = user_quota.get("used_today_videos", 0) + 1
    user_quota["used_month_videos"] = user_quota.get("used_month_videos", 0) + 1
    quotas[user_id] = user_quota
    save_quotas(quotas)
    
    return {"success": True, "remaining": user_quota.get("daily_videos", 5) - user_quota["used_today_videos"]}

@router.get("/system-stats")
async def get_system_stats():
    """获取系统统计信息（管理员功能）"""
    stats = load_stats()
    return {"stats": stats["system_stats"]}

@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/debug/files")
async def debug_files():
    """调试文件系统"""
    import os
    
    output_dir = os.path.abspath(str(DATA_DIR / "output"))
    assets_dir = os.path.abspath("../assets")
    
    result = {
        "output_dir": {
            "path": output_dir,
            "exists": os.path.exists(output_dir),
            "files": []
        },
        "assets_dir": {
            "path": assets_dir,
            "exists": os.path.exists(assets_dir),
            "files": []
        }
    }
    
    if os.path.exists(output_dir):
        try:
            result["output_dir"]["files"] = os.listdir(output_dir)
        except Exception as e:
            result["output_dir"]["error"] = str(e)
    
    if os.path.exists(assets_dir):
        try:
            result["assets_dir"]["files"] = os.listdir(assets_dir)[:10]  # 限制数量
        except Exception as e:
            result["assets_dir"]["error"] = str(e)
    
    return result