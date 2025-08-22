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
from src.core.config import settings

from src.api.v1 import api_router

# 预加载 Celery 配置（若启用）
try:
    from src.services.task_queue import is_celery_enabled
    if is_celery_enabled():
        # 导入任务模块以确保 worker 能发现
        import src.services.tasks.video_tasks  # noqa: F401
except Exception:
    # 在无 Celery/Redis 环境下忽略
    pass

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
app.mount("/output", StaticFiles(directory="../data/output"), name="output")
app.mount("/uploads", StaticFiles(directory="../data/uploads"), name="uploads")

app.include_router(api_router)
# 路由
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