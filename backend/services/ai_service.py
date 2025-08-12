from openai import OpenAI
import os
from typing import Dict, List
from gtts import gTTS
import io
from pydub import AudioSegment
import tempfile

class AIService:
    def __init__(self):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if openai_api_key and openai_api_key != "your_openai_api_key_here":
            self.client = OpenAI(api_key=openai_api_key)
    
    async def generate_script(self, topic: str, style: str, duration: str) -> Dict:
        """生成视频脚本"""
        # 这里可以添加更复杂的脚本生成逻辑
        pass
    
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
    
    async def optimize_content(self, content: str) -> str:
        """优化内容"""
        # 可以用于内容润色、SEO 优化等
        pass

# 全局 AI 服务实例
ai_service = AIService()