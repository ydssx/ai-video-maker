from fastapi import APIRouter

from app.api.routes import auth, projects, script, video

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(script.router)
api_router.include_router(video.router)
api_router.include_router(projects.router)
