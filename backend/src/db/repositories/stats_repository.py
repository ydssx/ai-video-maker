"""
Statistics Repository

Handles all database operations for statistics
"""
from datetime import date, datetime
from typing import Any, Dict, Optional, Type, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, or_

from src.db.models import UserStats, UserQuota, SystemStats, User
from src.db.repositories.base import CRUDBase

# 创建模型类型变量
UserStatsModel = TypeVar("UserStatsModel", bound=UserStats)
UserQuotaModel = TypeVar("UserQuotaModel", bound=UserQuota)
SystemStatsModel = TypeVar("SystemStatsModel", bound=SystemStats)

# 创建模式类型变量
class UserStatsBase(BaseModel):
    user_id: int
    date: date
    scripts_generated: int = 0
    videos_created: int = 0
    total_duration: float = 0.0
    last_activity: Optional[Dict[str, Any]] = None

class UserStatsCreate(UserStatsBase):
    pass

class UserStatsUpdate(BaseModel):
    scripts_generated: Optional[int] = None
    videos_created: Optional[int] = None
    total_duration: Optional[float] = None
    last_activity: Optional[Dict[str, Any]] = None

class UserStatsRepository(CRUDBase[UserStatsModel, UserStatsCreate, UserStatsUpdate]):
    """Repository for handling user statistics data operations"""
    
    def __init__(self, model: Type[UserStatsModel] = UserStats):
        super().__init__(model)
    
    def get_by_user_and_date(self, db: Session, user_id: int, target_date: Optional[date] = None) -> Optional[UserStats]:
        """Get user stats by user ID and date"""
        if target_date is None:
            target_date = date.today()
            
        return db.query(self.model).filter(
            self.model.user_id == user_id,
            self.model.date == target_date
        ).first()
    
    def get_or_create(self, db: Session, user_id: int, current_date: Optional[date] = None) -> UserStats:
        """Get or create user stats for the current date"""
        if current_date is None:
            current_date = date.today()
            
        stats = self.get_by_user_and_date(db, user_id, current_date)
        
        if not stats:
            stats_data = UserStatsCreate(
                user_id=user_id,
                date=current_date
            )
            stats = self.create(db, obj_in=stats_data)
            
        return stats
    
    def update_user_stats(
        self, 
        db: Session, 
        user_id: int, 
        scripts_generated: int = 0, 
        videos_created: int = 0, 
        duration: float = 0.0,
        last_activity: Optional[Dict] = None
    ) -> UserStats:
        """Update user statistics"""
        stats = self.get_or_create(db, user_id)
        
        update_data = {}
        if scripts_generated != 0:
            update_data["scripts_generated"] = stats.scripts_generated + scripts_generated
        if videos_created != 0:
            update_data["videos_created"] = stats.videos_created + videos_created
        if duration != 0.0:
            update_data["total_duration"] = stats.total_duration + duration
        if last_activity is not None:
            update_data["last_activity"] = last_activity
            
        return self.update(db, db_obj=stats, obj_in=update_data)
    
class UserQuotaRepository(CRUDBase[UserQuotaModel, Any, Any]):
    """Repository for handling user quota data operations"""
    
    def __init__(self, model: Type[UserQuotaModel] = UserQuota):
        super().__init__(model)
    
    def get_by_user(self, db: Session, user_id: int) -> Optional[UserQuota]:
        """Get user quota by user ID"""
        return db.query(self.model).filter(self.model.user_id == user_id).first()
    
    def get_or_create(self, db: Session, user_id: int) -> UserQuota:
        """Get or create user quota"""
        quota = self.get_by_user(db, user_id)
        
        if not quota:
            quota_data = {
                "user_id": user_id,
                "daily_script_limit": 10,
                "daily_video_limit": 5,
                "total_storage_mb": 1024,
                "scripts_used_today": 0,
                "videos_used_today": 0,
                "storage_used_mb": 0.0,
                "last_reset_date": date.today()
            }
            quota = self.create(db, obj_in=quota_data)
        
        return quota
    
    def update_quota_usage(
        self, 
        db: Session,
        user_id: int, 
        scripts_used: int = 0, 
        videos_used: int = 0, 
        storage_used_mb: float = 0.0
    ) -> UserQuota:
        """Update user quota usage"""
        quota = self.get_or_create(db, user_id)
        today = date.today()
        
        update_data = {}
        
        # Reset daily counters if it's a new day
        if quota.last_reset_date < today:
            update_data.update({
                "scripts_used_today": 0,
                "videos_used_today": 0,
                "last_reset_date": today
            })
        
        # Update usage
        if scripts_used != 0:
            scripts_used_today = update_data.get("scripts_used_today", quota.scripts_used_today) + scripts_used
            update_data["scripts_used_today"] = scripts_used_today
            
        if videos_used != 0:
            videos_used_today = update_data.get("videos_used_today", quota.videos_used_today) + videos_used
            update_data["videos_used_today"] = videos_used_today
            
        if storage_used_mb != 0.0:
            update_data["storage_used_mb"] = quota.storage_used_mb + storage_used_mb
        
        return self.update(db, db_obj=quota, obj_in=update_data)
    
class SystemStatsRepository(CRUDBase[SystemStatsModel, Any, Any]):
    """Repository for handling system statistics data operations"""
    
    def __init__(self, model: Type[SystemStatsModel] = SystemStats):
        super().__init__(model)
    
    def get_by_date(self, db: Session, target_date: Optional[date] = None) -> Optional[SystemStats]:
        """Get system stats by date"""
        if target_date is None:
            target_date = date.today()
            
        return db.query(self.model).filter(self.model.date == target_date).first()
    
    def get_or_create(self, db: Session, current_date: Optional[date] = None) -> SystemStats:
        """Get or create system stats for the current date"""
        if current_date is None:
            current_date = date.today()
            
        stats = self.get_by_date(db, current_date)
        
        if not stats:
            # Get previous day's stats if available
            prev_stats = db.query(self.model).order_by(self.model.date.desc()).first()
            
            stats_data = {
                "date": current_date,
                "total_users": prev_stats.total_users if prev_stats else 0,
                "active_users_today": 0,
                "total_scripts_generated": prev_stats.total_scripts_generated if prev_stats else 0,
                "total_videos_created": prev_stats.total_videos_created if prev_stats else 0,
                "total_video_duration": prev_stats.total_video_duration if prev_stats else 0.0,
                "total_storage_used_mb": prev_stats.total_storage_used_mb if prev_stats else 0.0
            }
            stats = self.create(db, obj_in=stats_data)
        
        return stats
    
    def update_system_stats(
        self,
        db: Session,
        scripts_generated: int = 0,
        videos_created: int = 0,
        video_duration: float = 0.0,
        storage_used_mb: float = 0.0
    ) -> SystemStats:
        """Update system statistics"""
        stats = self.get_or_create(db)
        
        update_data = {}
        
        if scripts_generated != 0:
            update_data["total_scripts_generated"] = stats.total_scripts_generated + scripts_generated
            
        if videos_created != 0:
            update_data["total_videos_created"] = stats.total_videos_created + videos_created
            
        if video_duration != 0.0:
            update_data["total_video_duration"] = stats.total_video_duration + video_duration
            
        if storage_used_mb != 0.0:
            update_data["total_storage_used_mb"] = stats.total_storage_used_mb + storage_used_mb
        
        # Update active users count
        today = date.today()
        active_users = db.query(
            func.count(distinct(UserStats.user_id))
        ).filter(
            UserStats.date == today,
            or_(
                UserStats.scripts_generated > 0,
                UserStats.videos_created > 0
            )
        ).scalar() or 1  # At least the current user is active
        
        update_data["active_users_today"] = active_users
        
        return self.update(db, db_obj=stats, obj_in=update_data)
    
class StatsService:
    """Service for handling statistics operations"""
    
    def __init__(
        self,
        user_stats_repo: UserStatsRepository = UserStatsRepository(),
        user_quota_repo: UserQuotaRepository = UserQuotaRepository(),
        system_stats_repo: SystemStatsRepository = SystemStatsRepository()
    ):
        self.user_stats_repo = user_stats_repo
        self.user_quota_repo = user_quota_repo
        self.system_stats_repo = system_stats_repo
    
    def record_user_activity(
        self,
        db: Session,
        user_id: int,
        activity_type: str,
        duration: float = 0.0
    ) -> Dict[str, str]:
        """Record user activity and update all related statistics"""
        try:
            # Update user stats
            if activity_type == 'script':
                self.user_stats_repo.update_user_stats(
                    db=db,
                    user_id=user_id,
                    scripts_generated=1,
                    last_activity={"type": "script_generated", "timestamp": datetime.utcnow().isoformat()}
                )
                self.user_quota_repo.update_quota_usage(db, user_id, scripts_used=1)
                self.system_stats_repo.update_system_stats(db, scripts_generated=1)
                
            elif activity_type == 'video':
                self.user_stats_repo.update_user_stats(
                    db=db,
                    user_id=user_id,
                    videos_created=1,
                    duration=duration,
                    last_activity={"type": "video_created", "duration": duration, "timestamp": datetime.utcnow().isoformat()}
                )
                self.user_quota_repo.update_quota_usage(
                    db, 
                    user_id, 
                    videos_used=1, 
                    storage_used_mb=duration * 0.1  # Example: 0.1MB per second
                )
                self.system_stats_repo.update_system_stats(
                    db,
                    videos_created=1, 
                    video_duration=duration, 
                    storage_used_mb=duration * 0.1
                )
            
            return {"status": "success", "message": f"{activity_type} activity recorded"}
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to record {activity_type} activity: {str(e)}"
            )
    
    def get_user_stats_summary(self, db: Session, user_id: int) -> Dict:
        """Get summary of user statistics and quota"""
        # Get today's stats
        today_stats = self.user_stats_repo.get_or_create(db, user_id)
        
        # Get total stats
        total_stats = db.query(
            func.sum(UserStats.scripts_generated).label("total_scripts"),
            func.sum(UserStats.videos_created).label("total_videos"),
            func.sum(UserStats.total_duration).label("total_duration")
        ).filter(UserStats.user_id == user_id).first()
        
        # Get quota
        quota = self.user_quota_repo.get_or_create(db, user_id)
        
        return {
            "today": {
                "scripts_generated": today_stats.scripts_generated,
                "videos_created": today_stats.videos_created,
                "duration": today_stats.total_duration,
                "last_activity": today_stats.last_activity
            },
            "total": {
                "scripts_generated": total_stats.total_scripts or 0,
                "videos_created": total_stats.total_videos or 0,
                "duration": total_stats.total_duration or 0.0
            },
            "quota": {
                "daily_script_limit": quota.daily_script_limit,
                "daily_video_limit": quota.daily_video_limit,
                "total_storage_mb": quota.total_storage_mb,
                "scripts_used_today": quota.scripts_used_today,
                "videos_used_today": quota.videos_used_today,
                "storage_used_mb": quota.storage_used_mb,
                "last_reset_date": quota.last_reset_date.isoformat()
            }
        }
    
    def get_system_stats_summary(self, db: Session) -> Dict:
        """Get summary of system statistics"""
        stats = self.system_stats_repo.get_or_create(db)
        
        # Update total users count
        total_users = db.query(func.count(User.id)).scalar() or 0
        if stats.total_users != total_users:
            self.system_stats_repo.update(
                db,
                db_obj=stats,
                obj_in={"total_users": total_users}
            )
        
        return {
            "total_users": total_users,
            "active_users_today": stats.active_users_today,
            "total_scripts_generated": stats.total_scripts_generated,
            "total_videos_created": stats.total_videos_created,
            "total_video_duration": stats.total_video_duration,
            "total_storage_used_mb": stats.total_storage_used_mb
        }

stats_service = StatsService()