from moviepy.editor import *
import os
from typing import List, Dict

class VideoProcessor:
    def __init__(self):
        self.temp_dir = "../assets/temp"
        self.output_dir = "../output"
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_text_clip(self, text: str, duration: float, style: Dict = None) -> TextClip:
        """创建文字剪辑"""
        default_style = {
            "fontsize": 50,
            "color": "white",
            "font": "Arial",
            "stroke_color": "black",
            "stroke_width": 2
        }
        
        if style:
            default_style.update(style)
        
        return TextClip(
            text,
            duration=duration,
            **default_style
        ).set_position('center')
    
    def create_image_clip(self, image_path: str, duration: float, size: tuple = (1280, 720)) -> ImageClip:
        """创建图片剪辑"""
        clip = ImageClip(image_path, duration=duration)
        return clip.resize(size)
    
    def add_transitions(self, clips: List[VideoClip], transition_type: str = "fade") -> VideoClip:
        """添加转场效果"""
        if transition_type == "fade":
            # 添加淡入淡出效果
            for i, clip in enumerate(clips):
                if i > 0:
                    clips[i] = clip.fadein(0.5)
                if i < len(clips) - 1:
                    clips[i] = clip.fadeout(0.5)
        
        return concatenate_videoclips(clips, method="compose")
    
    def add_background_music(self, video: VideoClip, music_path: str, volume: float = 0.3) -> VideoClip:
        """添加背景音乐"""
        if os.path.exists(music_path):
            audio = AudioFileClip(music_path).subclip(0, video.duration)
            audio = audio.volumex(volume)
            return video.set_audio(audio)
        return video
    
    def export_video(self, video: VideoClip, output_path: str, quality: str = "medium") -> str:
        """导出视频"""
        quality_settings = {
            "low": {"fps": 24, "bitrate": "500k"},
            "medium": {"fps": 24, "bitrate": "1000k"}, 
            "high": {"fps": 30, "bitrate": "2000k"}
        }
        
        settings = quality_settings.get(quality, quality_settings["medium"])
        
        video.write_videofile(
            output_path,
            fps=settings["fps"],
            codec='libx264',
            audio_codec='aac',
            bitrate=settings["bitrate"]
        )
        
        return output_path