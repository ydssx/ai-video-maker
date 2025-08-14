from openai import OpenAI
import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Optional, Union
from gtts import gTTS
import io
from pydub import AudioSegment
import tempfile
import logging
from datetime import datetime
import hashlib
import pickle

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if openai_api_key and openai_api_key != "your_openai_api_key_here":
            self.client = OpenAI(api_key=openai_api_key)
        
        # 缓存配置
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 支持的TTS引擎
        self.tts_engines = {
            "gtts": self._gtts_generate,
            "openai": self._openai_tts_generate,
            "edge": self._edge_tts_generate
        }
        
        # 统计信息
        self.stats = {
            "scripts_generated": 0,
            "voices_generated": 0,
            "cache_hits": 0,
            "api_calls": 0
        }
    
    async def generate_script(self, topic: str, style: str, duration: str) -> Dict:
        """生成视频脚本"""
        try:
            # 根据时长计算场景数量
            duration_minutes = self._parse_duration(duration)
            scene_count = max(3, min(8, int(duration_minutes * 2)))
            
            # 构建提示词
            prompt = self._build_script_prompt(topic, style, duration, scene_count)
            
            if self.client:
                # 使用 OpenAI 生成脚本
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个专业的视频脚本创作者，擅长创作各种风格的短视频脚本。"},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                
                script_content = response.choices[0].message.content
                return self._parse_script_response(script_content, scene_count)
            else:
                # 使用模板生成脚本
                return self._generate_template_script(topic, style, scene_count)
                
        except Exception as e:
            print(f"脚本生成失败: {str(e)}")
            # 返回默认脚本
            return self._generate_fallback_script(topic, style)
    
    async def generate_voice_openai(self, text: str, voice: str = "alloy") -> bytes:
        """使用 OpenAI TTS 生成语音"""
        if not self.client:
            raise Exception("OpenAI API 密钥未配置")
        
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            return response.content
        except Exception as e:
            raise Exception(f"OpenAI TTS 生成失败: {str(e)}")
    
    async def generate_voice_gtts(self, text: str, lang: str = "zh") -> bytes:
        """使用 Google TTS 生成语音"""
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # 使用内存缓冲区
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.getvalue()
        except Exception as e:
            raise Exception(f"Google TTS 生成失败: {str(e)}")
    
    async def generate_voice(self, text: str, voice_config: Dict = None) -> str:
        """生成语音并保存到文件"""
        config = voice_config or {"provider": "gtts", "voice": "zh", "speed": 1.0}
        
        try:
            # 根据配置选择 TTS 服务
            if config.get("provider") == "openai" and self.client:
                audio_data = await self.generate_voice_openai(text, config.get("voice", "alloy"))
            else:
                audio_data = await self.generate_voice_gtts(text, config.get("voice", "zh"))
            
            # 保存到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # 如果需要调整语速
            if config.get("speed", 1.0) != 1.0:
                temp_path = self.adjust_audio_speed(temp_path, config["speed"])
            
            return temp_path
            
        except Exception as e:
            raise Exception(f"语音生成失败: {str(e)}")
    
    def adjust_audio_speed(self, audio_path: str, speed: float) -> str:
        """调整音频播放速度"""
        try:
            audio = AudioSegment.from_mp3(audio_path)
            
            # 调整速度（不改变音调）
            if speed != 1.0:
                # 使用 pydub 的 speedup 方法
                new_sample_rate = int(audio.frame_rate * speed)
                audio = audio._spawn(audio.raw_data, overrides={"frame_rate": new_sample_rate})
                audio = audio.set_frame_rate(audio.frame_rate)
            
            # 保存调整后的音频
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                audio.export(temp_file.name, format="mp3")
                return temp_file.name
                
        except Exception as e:
            print(f"调整音频速度失败: {str(e)}")
            return audio_path
    
    def _parse_duration(self, duration: str) -> float:
        """解析时长字符串"""
        try:
            if "分钟" in duration:
                return float(duration.replace("分钟", ""))
            elif "秒" in duration:
                return float(duration.replace("秒", "")) / 60
            else:
                return float(duration)
        except:
            return 1.0  # 默认1分钟
    
    def _build_script_prompt(self, topic: str, style: str, duration: str, scene_count: int) -> str:
        """构建脚本生成提示词"""
        style_descriptions = {
            "教育": "教育性强，逻辑清晰，适合知识传播",
            "营销": "吸引眼球，突出卖点，具有说服力",
            "娱乐": "轻松幽默，富有趣味性，容易传播",
            "新闻": "客观准确，信息丰富，结构严谨",
            "故事": "情节生动，引人入胜，有情感共鸣"
        }
        
        style_desc = style_descriptions.get(style, "通用风格")
        
        return f"""
请为主题"{topic}"创作一个{duration}的{style}风格短视频脚本。

要求：
1. 脚本应该分为{scene_count}个场景
2. 风格特点：{style_desc}
3. 每个场景包含：场景描述、画面内容、文字内容
4. 总时长控制在{duration}左右
5. 内容要有吸引力，适合短视频传播

请按以下JSON格式返回：
{{
    "title": "视频标题",
    "description": "视频描述",
    "scenes": [
        {{
            "id": 1,
            "duration": 场景时长(秒),
            "description": "场景描述",
            "text": "画面文字内容",
            "voiceover": "旁白内容",
            "background": "背景描述"
        }}
    ]
}}
"""
    
    def _parse_script_response(self, response: str, scene_count: int) -> Dict:
        """解析AI返回的脚本内容"""
        try:
            import json
            import re
            
            # 尝试提取JSON内容
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                script_data = json.loads(json_match.group())
                return script_data
            else:
                # 如果没有找到JSON，使用文本解析
                return self._parse_text_script(response, scene_count)
                
        except Exception as e:
            print(f"解析脚本响应失败: {str(e)}")
            return self._generate_fallback_script("默认主题", "通用")
    
    def _parse_text_script(self, text: str, scene_count: int) -> Dict:
        """解析文本格式的脚本"""
        lines = text.strip().split('\n')
        scenes = []
        
        current_scene = None
        scene_id = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if '场景' in line or '第' in line:
                if current_scene:
                    scenes.append(current_scene)
                current_scene = {
                    "id": scene_id,
                    "duration": 15,
                    "description": line,
                    "text": "",
                    "voiceover": "",
                    "background": "默认背景"
                }
                scene_id += 1
            elif current_scene:
                if len(current_scene["voiceover"]) < 100:
                    current_scene["voiceover"] += line + " "
                if len(current_scene["text"]) < 50:
                    current_scene["text"] = line[:50]
        
        if current_scene:
            scenes.append(current_scene)
        
        return {
            "title": "AI生成视频",
            "description": "基于AI生成的视频脚本",
            "scenes": scenes[:scene_count]
        }
    
    def _generate_template_script(self, topic: str, style: str, scene_count: int) -> Dict:
        """生成模板脚本"""
        templates = {
            "教育": {
                "scenes": [
                    {"text": f"什么是{topic}？", "voiceover": f"今天我们来了解一下{topic}的基本概念"},
                    {"text": f"{topic}的重要性", "voiceover": f"{topic}在我们生活中扮演着重要角色"},
                    {"text": f"{topic}的应用", "voiceover": f"让我们看看{topic}的实际应用场景"},
                    {"text": "总结", "voiceover": f"通过今天的学习，我们对{topic}有了更深入的了解"}
                ]
            },
            "营销": {
                "scenes": [
                    {"text": "你还在为...烦恼吗？", "voiceover": f"你是否还在为{topic}相关的问题而困扰？"},
                    {"text": f"发现{topic}的秘密", "voiceover": f"今天为你揭秘{topic}的核心价值"},
                    {"text": "立即行动", "voiceover": "不要再等待，现在就开始改变"},
                    {"text": "成功就在眼前", "voiceover": "选择我们，选择成功"}
                ]
            }
        }
        
        template = templates.get(style, templates["教育"])
        scenes = []
        
        for i, scene_template in enumerate(template["scenes"][:scene_count]):
            scenes.append({
                "id": i + 1,
                "duration": 15,
                "description": f"场景 {i + 1}",
                "text": scene_template["text"],
                "voiceover": scene_template["voiceover"],
                "background": "默认背景"
            })
        
        return {
            "title": f"{topic} - {style}视频",
            "description": f"关于{topic}的{style}风格视频",
            "scenes": scenes
        }
    
    def _generate_fallback_script(self, topic: str, style: str) -> Dict:
        """生成备用脚本"""
        return {
            "title": f"{topic}视频",
            "description": f"关于{topic}的视频内容",
            "scenes": [
                {
                    "id": 1,
                    "duration": 20,
                    "description": "开场介绍",
                    "text": f"关于{topic}",
                    "voiceover": f"欢迎观看本期关于{topic}的视频内容",
                    "background": "默认背景"
                },
                {
                    "id": 2,
                    "duration": 25,
                    "description": "主要内容",
                    "text": f"{topic}详解",
                    "voiceover": f"接下来我们详细了解一下{topic}的相关知识",
                    "background": "默认背景"
                },
                {
                    "id": 3,
                    "duration": 15,
                    "description": "总结",
                    "text": "感谢观看",
                    "voiceover": "感谢大家的观看，我们下期再见",
                    "background": "默认背景"
                }
            ]
        }
    
    async def optimize_content(self, content: str, optimization_type: str = "general") -> str:
        """优化内容"""
        if not self.client:
            return content
        
        try:
            optimization_prompts = {
                "general": "请优化以下内容，使其更加吸引人和易于理解",
                "seo": "请优化以下内容，提高SEO友好度，增加关键词密度",
                "engagement": "请优化以下内容，提高用户参与度和互动性",
                "clarity": "请优化以下内容，使表达更加清晰简洁",
                "emotional": "请优化以下内容，增强情感共鸣和感染力"
            }
            
            prompt = optimization_prompts.get(optimization_type, optimization_prompts["general"])
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个内容优化专家，擅长改进文本内容的表达和吸引力。"},
                    {"role": "user", "content": f"{prompt}：\n\n{content}"}
                ],
                temperature=0.5,
                max_tokens=500
            )
            
            self.stats["api_calls"] += 1
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"内容优化失败: {str(e)}")
            return content
    
    async def generate_keywords(self, topic: str, count: int = 10) -> List[str]:
        """生成关键词"""
        if not self.client:
            return self._generate_default_keywords(topic, count)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个关键词生成专家，擅长为主题生成相关的关键词。"},
                    {"role": "user", "content": f"为主题'{topic}'生成{count}个相关关键词，用逗号分隔"}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            keywords_text = response.choices[0].message.content.strip()
            keywords = [kw.strip() for kw in keywords_text.split(',')]
            
            self.stats["api_calls"] += 1
            return keywords[:count]
        except Exception as e:
            logger.error(f"关键词生成失败: {str(e)}")
            return self._generate_default_keywords(topic, count)
    
    def _generate_default_keywords(self, topic: str, count: int) -> List[str]:
        """生成默认关键词"""
        base_keywords = [topic, "视频", "内容", "分享", "学习", "教程", "介绍", "精彩", "有趣", "实用"]
        return base_keywords[:count]
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Union[str, float]]:
        """分析文本情感"""
        if not self.client:
            return {"sentiment": "neutral", "confidence": 0.5, "emotions": []}
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个情感分析专家，分析文本的情感倾向。"},
                    {"role": "user", "content": f"分析以下文本的情感，返回JSON格式：{{'sentiment': '正面/负面/中性', 'confidence': 0.0-1.0, 'emotions': ['情感标签']}}：\n\n{text}"}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            self.stats["api_calls"] += 1
            return result
        except Exception as e:
            logger.error(f"情感分析失败: {str(e)}")
            return {"sentiment": "neutral", "confidence": 0.5, "emotions": []}
    
    async def generate_title_suggestions(self, content: str, count: int = 5) -> List[str]:
        """生成标题建议"""
        if not self.client:
            return [f"关于{content[:20]}的视频" for _ in range(count)]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个标题创作专家，擅长创作吸引人的视频标题。"},
                    {"role": "user", "content": f"为以下内容生成{count}个吸引人的视频标题：\n\n{content}"}
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            titles_text = response.choices[0].message.content.strip()
            titles = [title.strip().lstrip('1234567890.-') for title in titles_text.split('\n') if title.strip()]
            
            self.stats["api_calls"] += 1
            return titles[:count]
        except Exception as e:
            logger.error(f"标题生成失败: {str(e)}")
            return [f"精彩内容第{i+1}期" for i in range(count)]
    
    def _get_cache_key(self, data: str) -> str:
        """生成缓存键"""
        return hashlib.md5(data.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[any]:
        """从缓存获取数据"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    # 检查缓存是否过期（24小时）
                    if (datetime.now() - data['timestamp']).seconds < 86400:
                        self.stats["cache_hits"] += 1
                        return data['content']
            except Exception as e:
                logger.error(f"缓存读取失败: {str(e)}")
        return None
    
    def _save_to_cache(self, cache_key: str, content: any):
        """保存到缓存"""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump({
                    'content': content,
                    'timestamp': datetime.now()
                }, f)
        except Exception as e:
            logger.error(f"缓存保存失败: {str(e)}")
    
    async def _edge_tts_generate(self, text: str, voice: str = "zh-CN-XiaoxiaoNeural") -> bytes:
        """使用Edge TTS生成语音"""
        try:
            import edge_tts
            
            communicate = edge_tts.Communicate(text, voice)
            audio_data = b""
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            return audio_data
        except ImportError:
            logger.warning("Edge TTS未安装，回退到Google TTS")
            return await self._gtts_generate(text, "zh")
        except Exception as e:
            logger.error(f"Edge TTS生成失败: {str(e)}")
            return await self._gtts_generate(text, "zh")
    
    async def _gtts_generate(self, text: str, lang: str = "zh") -> bytes:
        """使用Google TTS生成语音"""
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer.getvalue()
        except Exception as e:
            logger.error(f"Google TTS生成失败: {str(e)}")
            raise
    
    async def _openai_tts_generate(self, text: str, voice: str = "alloy") -> bytes:
        """使用OpenAI TTS生成语音"""
        if not self.client:
            raise Exception("OpenAI客户端未初始化")
        
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text
            )
            self.stats["api_calls"] += 1
            return response.content
        except Exception as e:
            logger.error(f"OpenAI TTS生成失败: {str(e)}")
            raise
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            "scripts_generated": 0,
            "voices_generated": 0,
            "cache_hits": 0,
            "api_calls": 0
        }

# 全局 AI 服务实例
ai_service = AIService()