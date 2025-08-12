from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from routers import script_generator, video_maker, assets, stats, presets, user_assets, audio_manager, projects, cloud_storage

load_dotenv()

app = FastAPI(title="AI Video Maker API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

@app.get("/")
async def root():
    return {"message": "AI Video Maker API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)