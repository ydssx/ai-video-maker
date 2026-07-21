from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models import User
from app.schemas import ScriptRequest, ScriptResponse
from app.services.script_service import generate_script

router = APIRouter(prefix="/api/script", tags=["script"])


@router.post("/generate", response_model=ScriptResponse)
def generate(payload: ScriptRequest, _: User = Depends(get_current_user)):
    return generate_script(payload)


@router.get("/templates")
def templates(_: User = Depends(get_current_user)):
    return {
        "styles": [
            {"id": "educational", "name": "知识讲解"},
            {"id": "entertainment", "name": "轻松娱乐"},
            {"id": "commercial", "name": "种草带货"},
            {"id": "news", "name": "资讯快报"},
        ],
        "durations": ["15s", "30s", "60s"],
    }
