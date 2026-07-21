import json
import re
from typing import Any

from loguru import logger

from app.core.config import settings
from app.schemas import ScriptRequest, ScriptResponse, SceneIn


DURATION_MAP = {
    "15s": 15,
    "30s": 30,
    "60s": 60,
}


def _mock_script(req: ScriptRequest) -> ScriptResponse:
    total = DURATION_MAP.get(req.duration, 30)
    scene_count = 3 if total <= 15 else 4 if total <= 30 else 5
    per = round(total / scene_count, 1)
    hooks = [
        f"今天聊聊：{req.topic}",
        f"关于「{req.topic}」，先抓住一个关键点",
        f"大多数人忽略的细节：{req.topic}",
        f"把它拆成三步，马上能用",
        f"记住：{req.topic}，从现在开始行动",
    ]
    scenes = [
        SceneIn(
            text=hooks[i % len(hooks)],
            duration=per,
            image_keywords=[req.topic, req.style],
            transition="fade",
        )
        for i in range(scene_count)
    ]
    return ScriptResponse(
        title=f"{req.topic} · 短视频脚本",
        scenes=scenes,
        total_duration=float(total),
        style=req.style,
        source="mock",
    )


def _openai_script(req: ScriptRequest) -> ScriptResponse | None:
    if not settings.has_openai:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        total = DURATION_MAP.get(req.duration, 30)
        prompt = (
            f"为主题「{req.topic}」写一个{req.style}风格短视频脚本，总时长约{total}秒，"
            f"语言={req.language}。只返回 JSON："
            '{"title":"...","scenes":[{"text":"...","duration":3.0,"image_keywords":["..."],"transition":"fade"}]}'
        )
        resp = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "你是短视频编剧，只输出合法 JSON。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        content = resp.choices[0].message.content or ""
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            return None
        data: dict[str, Any] = json.loads(match.group(0))
        scenes = [SceneIn(**scene) for scene in data.get("scenes", [])]
        if not scenes:
            return None
        return ScriptResponse(
            title=data.get("title") or f"{req.topic} · 短视频脚本",
            scenes=scenes,
            total_duration=sum(s.duration for s in scenes),
            style=req.style,
            source="openai",
        )
    except Exception as exc:
        logger.warning(f"OpenAI 脚本生成失败，回退 mock: {exc}")
        return None


def generate_script(req: ScriptRequest) -> ScriptResponse:
    ai = _openai_script(req)
    return ai or _mock_script(req)
