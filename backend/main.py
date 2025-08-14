from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

# 导入中间件
from middleware.rate_limiter import rate_limit_middleware
from middleware.error_handler import error_handling_middleware
from middleware.logging import logging_middleware, setup_logging

# 导入配置
from config import settings

from routers import (
    script_generator, video_maker, assets, stats, presets, 
    user_assets, audio_manager, projects, cloud_storage,
    users, system
)

# 导入数据库工厂
from database_factory import get_db_service

load_dotenv()

# 设置日志
setup_logging()

app = FastAPI(
    title="AI Video Maker API", 
    version="1.0.0",
    description="AI-powered video creation platform with advanced editing capabilities",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加中间件（注意顺序很重要）
app.middleware("http")(error_handling_middleware)
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(logging_middleware)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/assets", StaticFiles(directory="../assets"), name="assets")
app.mount("/output", StaticFiles(directory="../output"), name="output")

# 测试页面（仅开发环境）
import os
if os.getenv("ENVIRONMENT") != "production":
    from fastapi.responses import FileResponse
    
    @app.get("/test-download")
    async def test_download_page():
        return FileResponse("../test-download.html")

# 路由
app.include_router(script_generator.router, prefix="/api/script", tags=["script"])
app.include_router(video_maker.router, prefix="/api/video", tags=["video"])
app.include_router(assets.router, prefix="/api/assets", tags=["assets"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(presets.router, prefix="/api/presets", tags=["presets"])
app.include_router(user_assets.router)
app.include_router(audio_manager.router)
app.include_router(projects.router)
app.include_router(cloud_storage.router)
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(system.router, prefix="/api/system", tags=["system"])

@app.get("/")
async def root():
    return {"message": "AI Video Maker API"}

@app.get("/health")
async def health_check():
    """健康检查，包含数据库连接状态"""
    try:
        db_service = get_db_service()
        
        # 测试数据库连接
        if hasattr(db_service, 'test_connection'):
            db_status = db_service.test_connection()
        else:
            # SQLite数据库服务的简单测试
            try:
                db_service.get_system_stats()
                db_status = True
            except:
                db_status = False
        
        return {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "database_type": "mysql" if hasattr(db_service, 'engine') else "sqlite"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)