"""
API v1 路由

包含所有API v1版本的路由
"""
from fastapi import APIRouter

from src.api.v1.endpoints import  (
    script_generator, video_maker, assets, stats, presets, 
    user_assets, audio_manager, projects, cloud_storage,
    users, system
) 
api_router = APIRouter()

# 认证路由
# api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# # 用户管理路由
# api_router.include_router(users.router, prefix="/users", tags=["用户"])

# # 项目管理路由
# api_router.include_router(projects.router, prefix="/projects", tags=["项目"])

# # 资源管理路由
# api_router.include_router(assets.router, prefix="/assets", tags=["资源"])

# # 视频管理路由
# api_router.include_router(videos.router, prefix="/videos", tags=["视频"])


api_router.include_router(script_generator.router, prefix="/api/script", tags=["script"])
api_router.include_router(video_maker.router, prefix="/api/video", tags=["video"])
api_router.include_router(assets.router, prefix="/api/assets", tags=["assets"])
api_router.include_router(stats.router, prefix="/api/stats", tags=["stats"])
api_router.include_router(presets.router, prefix="/api/presets", tags=["presets"])
api_router.include_router(user_assets.router)
api_router.include_router(audio_manager.router)
api_router.include_router(projects.router)
api_router.include_router(cloud_storage.router)
api_router.include_router(users.router, prefix="/api/users", tags=["users"])
api_router.include_router(system.router, prefix="/api/system", tags=["system"])

