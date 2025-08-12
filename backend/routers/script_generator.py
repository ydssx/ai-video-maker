from fastapi import APIRouter, HTTPException
from openai import OpenAI
import os
import json
from models import ScriptRequest, ScriptResponse, SceneData, VideoStyle

router = APIRouter()

# 初始化 OpenAI 客户端（如果有 API 密钥的话）
openai_api_key = os.getenv("OPENAI_API_KEY")
client = None
if openai_api_key and openai_api_key != "your_openai_api_key_here":
    client = OpenAI(api_key=openai_api_key)

def generate_script_prompt(request: ScriptRequest) -> str:
    """生成脚本的提示词"""
    duration_map = {"15s": 15, "30s": 30, "60s": 60}
    total_seconds = duration_map[request.duration]
    
    style_prompts = {
        VideoStyle.EDUCATIONAL: "教育性内容，语言简洁明了，逻辑清晰",
        VideoStyle.ENTERTAINMENT: "娱乐性内容，语言生动有趣，吸引眼球",
        VideoStyle.COMMERCIAL: "商业推广内容，突出产品优势，有说服力",
        VideoStyle.NEWS: "新闻资讯内容，客观准确，信息量大"
    }
    
    prompt = f"""
请为主题"{request.topic}"生成一个{request.duration}的短视频脚本。

要求：
1. 风格：{style_prompts[request.style]}
2. 总时长：{total_seconds}秒
3. 分成3-5个场景，每个场景3-8秒
4. 每个场景需要配文字说明和相关图片关键词
5. 语言：{"中文" if request.language == "zh" else "英文"}

请以JSON格式返回，包含：
- title: 视频标题
- scenes: 场景数组，每个场景包含：
  - text: 场景文字内容
  - duration: 场景时长（秒）
  - image_keywords: 相关图片关键词数组
  - transition: 转场效果（fade/slide/zoom）

示例格式：
{{
  "title": "视频标题",
  "scenes": [
    {{
      "text": "场景文字内容",
      "duration": 5.0,
      "image_keywords": ["关键词1", "关键词2"],
      "transition": "fade"
    }}
  ]
}}
"""
    return prompt

@router.post("/generate", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest):
    """生成视频脚本"""
    try:
        # 如果有 OpenAI API 密钥，使用真实的 AI 生成
        if client:
            prompt = generate_script_prompt(request)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的短视频脚本创作者，擅长创作各种风格的短视频内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            # 解析 AI 返回的 JSON
            script_data = json.loads(response.choices[0].message.content)
        else:
            # 使用模拟数据进行演示
            script_data = generate_mock_script(request)
        
        # 计算总时长
        total_duration = sum(scene["duration"] for scene in script_data["scenes"])
        
        # 构建响应
        scenes = [SceneData(**scene) for scene in script_data["scenes"]]
        
        return ScriptResponse(
            title=script_data["title"],
            scenes=scenes,
            total_duration=total_duration,
            style=request.style
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI 返回格式错误")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"脚本生成失败: {str(e)}")

def generate_mock_script(request: ScriptRequest) -> dict:
    """生成模拟脚本数据（用于演示）"""
    duration_map = {"15s": 15, "30s": 30, "60s": 60}
    total_seconds = duration_map[request.duration]
    scene_count = 3 if total_seconds <= 15 else (4 if total_seconds <= 30 else 5)
    scene_duration = total_seconds / scene_count
    
    mock_scripts = {
        "Python 编程": {
            "title": "Python 编程快速入门",
            "scenes": [
                {
                    "text": "Python 是一门简单易学的编程语言",
                    "duration": scene_duration,
                    "image_keywords": ["python", "programming", "code"],
                    "transition": "fade"
                },
                {
                    "text": "它有着清晰的语法和强大的功能",
                    "duration": scene_duration,
                    "image_keywords": ["syntax", "clean code", "development"],
                    "transition": "slide"
                },
                {
                    "text": "让我们开始你的编程之旅吧！",
                    "duration": scene_duration,
                    "image_keywords": ["journey", "learning", "success"],
                    "transition": "zoom"
                }
            ]
        }
    }
    
    # 根据主题选择合适的模拟脚本，或生成通用脚本
    topic_key = next((key for key in mock_scripts.keys() if key in request.topic), None)
    
    if topic_key:
        return mock_scripts[topic_key]
    else:
        return {
            "title": f"关于{request.topic}的精彩内容",
            "scenes": [
                {
                    "text": f"今天我们来聊聊{request.topic}",
                    "duration": scene_duration,
                    "image_keywords": [request.topic, "introduction", "topic"],
                    "transition": "fade"
                },
                {
                    "text": f"{request.topic}有很多有趣的方面",
                    "duration": scene_duration,
                    "image_keywords": [request.topic, "interesting", "aspects"],
                    "transition": "slide"
                },
                {
                    "text": f"希望这个视频能帮助你了解{request.topic}",
                    "duration": scene_duration,
                    "image_keywords": [request.topic, "helpful", "understanding"],
                    "transition": "zoom"
                }
            ][:scene_count]
        }

@router.get("/templates")
async def get_script_templates():
    """获取脚本模板"""
    templates = [
        {
            "id": "educational",
            "name": "教育科普",
            "description": "适合知识分享、教程讲解",
            "example_topics": ["Python 编程入门", "健康饮食知识", "历史小故事"]
        },
        {
            "id": "entertainment", 
            "name": "娱乐搞笑",
            "description": "适合搞笑段子、生活趣事",
            "example_topics": ["程序员的日常", "宠物搞笑瞬间", "生活小妙招"]
        },
        {
            "id": "commercial",
            "name": "商业推广", 
            "description": "适合产品介绍、品牌宣传",
            "example_topics": ["新产品发布", "服务介绍", "品牌故事"]
        }
    ]
    return {"templates": templates}