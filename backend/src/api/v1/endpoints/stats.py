from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.db.repositories.stats_repository import stats_service
from src.db.models import User
from src.schemas.user import UserInDB
from src.api.deps import get_current_user

router = APIRouter()

@router.get("/user-stats")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    获取用户统计信息
    
    返回当前用户的统计信息，包括今日使用情况和总量统计
    """
    try:
        stats = stats_service.get_user_stats_summary(db, current_user.id)
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户统计信息失败: {str(e)}"
        )

@router.get("/user-quota")
async def get_user_quota(
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    获取用户配额信息
    
    返回当前用户的配额使用情况
    """
    try:
        stats = stats_service.get_user_stats_summary(db, current_user.id)
        return {
            "status": "success",
            "data": stats["quota"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户配额信息失败: {str(e)}"
        )

@router.post("/record-script")
async def record_script_generation(
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    记录脚本生成
    
    记录用户生成脚本的活动，并更新相关统计信息
    """
    try:
        result = stats_service.record_user_activity(db, current_user.id, 'script')
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"记录脚本生成失败: {str(e)}"
        )

@router.post("/record-video")
async def record_video_creation(
    duration: float = 30.0,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    记录视频创建
    
    记录用户创建视频的活动，并更新相关统计信息
    
    Args:
        duration: 视频时长（秒）
    """
    try:
        result = stats_service.record_user_activity(db, current_user
        .id, 'video', duration)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"记录视频创建失败: {str(e)}"
        )

@router.get("/system")
async def get_system_stats(
    db: Session = Depends(get_db)
):
    """
    获取系统统计信息
    
    返回系统的总体统计信息，包括用户数、活跃用户、生成的脚本和视频数量等
    """
    try:
        stats = stats_service.get_system_stats_summary(db)
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统统计信息失败: {str(e)}"
        )
