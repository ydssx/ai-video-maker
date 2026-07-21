import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.api.router import api_router
from app.core.config import settings
from app.db.session import init_db


def _ensure_dirs() -> None:
    for path in (settings.upload_dir, settings.output_dir, settings.temp_dir, "logs"):
        Path(path).mkdir(parents=True, exist_ok=True)
    # 兼容从 backend/ 启动时的上级静态目录
    for path in ("../data/output", "../data/uploads", "../assets"):
        Path(path).mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    _ensure_dirs()
    try:
        init_db()
        logger.info("数据库表已就绪")
    except Exception as exc:
        logger.error(f"数据库初始化失败（服务仍可启动）: {exc}")
    yield


app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    description="从零重写的 AI 短视频制作平台 API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

_ensure_dirs()
app.mount("/output", StaticFiles(directory=settings.output_dir), name="output")
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")


@app.get("/")
def root():
    return {"name": settings.app_name, "version": "2.0.0", "status": "ok"}


@app.get("/health")
def health():
    db_ok = False
    error = None
    try:
        from sqlalchemy import text
        from app.db.session import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as exc:
        error = str(exc)
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
        "database_type": "mysql",
        "error": error,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
