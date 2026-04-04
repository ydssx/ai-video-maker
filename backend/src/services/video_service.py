import os
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable, Union
import logging
from datetime import datetime
import json
import uuid
from concurrent.futures import ThreadPoolExecutor
import subprocess

import numpy as np

# MoviePy imports
from moviepy.editor import (
    VideoFileClip, ImageClip, TextClip, CompositeVideoClip,
    AudioFileClip, concatenate_videoclips, ColorClip,
)
from moviepy.video.fx import resize, fadein, fadeout
from moviepy.video.compositing.transitions import (
    crossfadein,
    crossfadeout,
    slide_in,
    slide_out,
)

logger = logging.getLogger(__name__)


def _parse_css_color(value: Union[str, tuple, list]) -> Tuple[int, int, int]:
    """将模板中的颜色转为 RGB 元组（0–255）。"""
    if isinstance(value, str) and value.startswith("#") and len(value) == 7:
        return (
            int(value[1:3], 16),
            int(value[3:5], 16),
            int(value[5:7], 16),
        )
    if isinstance(value, (list, tuple)) and len(value) == 3:
        return (int(value[0]), int(value[1]), int(value[2]))
    if isinstance(value, str):
        # 常见命名色兜底
        named = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
        }
        if value.lower() in named:
            return named[value.lower()]
    return (30, 58, 138)


def _linear_gradient_rgb_array(
    width: int, height: int, top_rgb: Tuple[int, int, int], bottom_rgb: Tuple[int, int, int]
) -> np.ndarray:
    """竖直线性渐变，形状 (height, width, 3) uint8。"""
    c0 = np.array(top_rgb, dtype=np.float32).reshape(1, 1, 3)
    c1 = np.array(bottom_rgb, dtype=np.float32).reshape(1, 1, 3)
    if height <= 1:
        t = np.zeros((1, width, 1), dtype=np.float32)
    else:
        t = np.linspace(0.0, 1.0, height, dtype=np.float32).reshape(height, 1, 1)
        t = np.broadcast_to(t, (height, width, 1))
    blended = (1.0 - t) * c0 + t * c1
    return np.clip(blended, 0, 255).astype(np.uint8)


class VideoService:
    def __init__(self):
        from src.core.config import settings
        self.output_dir = Path(settings.output_path)
        self.temp_dir = Path(settings.temp_path)
        # 资源目录仍在项目根目录的 assets 下
        self.assets_dir = Path("../assets")
        
        # 创建必要目录
        for directory in [self.output_dir, self.temp_dir, self.assets_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 线程池用于并行处理
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # 视频处理状态
        self.processing_videos = {}
        
        # 支持的输出格式
        self.output_formats = {
            'mp4': {'codec': 'libx264', 'audio_codec': 'aac'},
            'webm': {'codec': 'libvpx-vp9', 'audio_codec': 'libvorbis'},
            'avi': {'codec': 'libxvid', 'audio_codec': 'mp3'},
            'mov': {'codec': 'libx264', 'audio_codec': 'aac'}
        }
        
        # 分辨率预设
        self.resolution_presets = {
            '360p': (640, 360),
            '480p': (854, 480),
            '720p': (1280, 720),
            '1080p': (1920, 1080),
            '1440p': (2560, 1440),
            '4k': (3840, 2160)
        }
        
    async def create_video(self, video_id: str, script_data: Dict, 
                          config: Dict, progress_callback: Optional[Callable] = None) -> Dict:
        """创建视频"""
        try:
            # 更新处理状态
            self.processing_videos[video_id] = {
                'status': 'processing',
                'progress': 0,
                'start_time': datetime.now()
            }
            
            if progress_callback:
                await progress_callback(video_id, 0, "开始处理...")
            
            # 解析配置
            template_id = config.get('template_id', 'default')
            resolution = config.get('resolution', '720p')
            fps = config.get('fps', 30)
            output_format = config.get('format', 'mp4')
            
            # 创建视频片段
            clips = []
            total_scenes = len(script_data['scenes'])
            
            for i, scene in enumerate(script_data['scenes']):
                if progress_callback:
                    progress = int((i / total_scenes) * 80)  # 80% for scene processing
                    await progress_callback(video_id, progress, f"处理场景 {i+1}/{total_scenes}")
                
                clip = await self._create_scene_clip(scene, template_id, resolution)
                clips.append(clip)
            
            # 应用转场效果
            if progress_callback:
                await progress_callback(video_id, 85, "应用转场效果...")
            
            final_clips = await self._apply_transitions(clips, script_data['scenes'])
            
            # 合并视频
            if progress_callback:
                await progress_callback(video_id, 90, "合并视频片段...")
            
            overlap = 0.5 if len(final_clips) > 1 else 0
            final_video = concatenate_videoclips(
                final_clips, method="compose", padding=-overlap
            )
            
            # 添加音频
            if config.get('voice_config', {}).get('enabled', False):
                if progress_callback:
                    await progress_callback(video_id, 95, "添加音频...")
                
                final_video = await self._add_audio(final_video, script_data, config['voice_config'])
            
            # 导出视频
            if progress_callback:
                await progress_callback(video_id, 98, "导出视频...")
            
            output_path = await self._export_video(
                final_video, video_id, resolution, fps, output_format
            )
            
            # 生成缩略图
            thumbnail_path = await self._generate_thumbnail(final_video, video_id)
            
            # 清理资源
            final_video.close()
            for clip in clips:
                clip.close()
            
            # 更新状态
            self.processing_videos[video_id] = {
                'status': 'completed',
                'progress': 100,
                'output_path': output_path,
                'thumbnail_path': thumbnail_path,
                'duration': final_video.duration,
                'completed_time': datetime.now()
            }
            
            if progress_callback:
                await progress_callback(video_id, 100, "视频创建完成!")
            
            return {
                'video_id': video_id,
                'status': 'completed',
                'output_path': output_path,
                'thumbnail_path': thumbnail_path,
                'duration': final_video.duration
            }
            
        except Exception as e:
            logger.error(f"视频创建失败: {str(e)}")
            self.processing_videos[video_id] = {
                'status': 'failed',
                'error': str(e),
                'failed_time': datetime.now()
            }
            
            if progress_callback:
                await progress_callback(video_id, -1, f"创建失败: {str(e)}")
            
            raise
    
    async def _create_scene_clip(self, scene: Dict, template_id: str, resolution: str) -> VideoFileClip:
        """创建场景片段"""
        duration = scene.get('duration', 5.0)
        text = scene.get('text', '')
        
        # 获取分辨率
        width, height = self.resolution_presets[resolution]
        
        # 创建背景
        background = await self._create_background(scene, template_id, width, height, duration)
        
        # 创建文字
        text_clip = await self._create_text_clip(text, template_id, width, height, duration)
        
        # 合成场景
        scene_clip = CompositeVideoClip([background, text_clip], size=(width, height))
        scene_clip = scene_clip.set_duration(duration)
        
        return scene_clip
    
    async def _create_background(self, scene: Dict, template_id: str, 
                                width: int, height: int, duration: float) -> VideoFileClip:
        """创建背景"""
        # 获取模板样式
        template_style = self._get_template_style(template_id)
        
        # 检查是否有指定的背景图片
        background_image = scene.get('background_image')
        if background_image and os.path.exists(background_image):
            # 使用指定图片作为背景
            background = ImageClip(background_image)
            background = background.resize((width, height))
        else:
            # 使用纯色或渐变背景
            background_color = template_style.get('background_color', '#1e3a8a')
            
            if isinstance(background_color, list) and len(background_color) == 2:
                c_top = _parse_css_color(background_color[0])
                c_bot = _parse_css_color(background_color[1])
                frame = _linear_gradient_rgb_array(width, height, c_top, c_bot)
                background = ImageClip(frame).set_duration(duration)
            else:
                # 纯色背景
                background = ColorClip(size=(width, height), color=background_color)
        
        background = background.set_duration(duration)
        return background
    
    async def _create_text_clip(self, text: str, template_id: str, 
                               width: int, height: int, duration: float) -> TextClip:
        """创建文字片段"""
        if not text.strip():
            # 返回透明片段
            return ColorClip(size=(width, height), color=(0,0,0,0)).set_duration(duration)
        
        # 获取模板样式
        template_style = self._get_template_style(template_id)
        
        # 文字样式
        font_size = template_style.get('font_size', 48)
        font_color = template_style.get('font_color', 'white')
        font_family = template_style.get('font_family', 'Arial')
        
        # 创建文字片段
        text_clip = TextClip(
            text,
            fontsize=font_size,
            color=font_color,
            font=font_family,
            size=(width * 0.8, None),  # 限制宽度
            method='caption'
        )
        
        # 设置位置
        position = template_style.get('text_position', 'center')
        if position == 'center':
            text_clip = text_clip.set_position('center')
        elif position == 'bottom':
            text_clip = text_clip.set_position(('center', height * 0.8))
        elif position == 'top':
            text_clip = text_clip.set_position(('center', height * 0.1))
        
        text_clip = text_clip.set_duration(duration)
        
        # 添加文字效果
        text_effects = template_style.get('text_effects', {})
        if text_effects.get('fade_in'):
            text_clip = text_clip.fadein(0.5)
        if text_effects.get('fade_out'):
            text_clip = text_clip.fadeout(0.5)
        
        return text_clip
    
    def _get_template_style(self, template_id: str) -> Dict:
        """获取模板样式"""
        templates = {
            'default': {
                'background_color': '#1e3a8a',
                'font_size': 48,
                'font_color': 'white',
                'font_family': 'Arial',
                'text_position': 'center',
                'text_effects': {'fade_in': True, 'fade_out': True}
            },
            'modern': {
                'background_color': ['#667eea', '#764ba2'],
                'font_size': 52,
                'font_color': 'white',
                'font_family': 'Arial-Bold',
                'text_position': 'center',
                'text_effects': {'fade_in': True}
            },
            'elegant': {
                'background_color': '#ffecd2',
                'font_size': 44,
                'font_color': '#8B4513',
                'font_family': 'Times-Roman',
                'text_position': 'center',
                'text_effects': {}
            }
        }
        
        return templates.get(template_id, templates['default'])
    
    async def _apply_transitions(self, clips: List[VideoFileClip], scenes: List[Dict]) -> List[VideoFileClip]:
        """应用转场效果（在拼接时使用负 padding 实现重叠交叉）。"""
        if len(clips) <= 1:
            return clips

        final_clips: List[VideoFileClip] = [clips[0]]
        transition_duration = 0.5

        for i in range(1, len(clips)):
            transition_type = scenes[i].get("transition", "fade")
            prev_clip = final_clips[-1]
            curr_clip = clips[i]

            if transition_type == "fade":
                prev_clip = crossfadeout(prev_clip, transition_duration)
                curr_clip = crossfadein(curr_clip, transition_duration)
            elif transition_type in (
                "slide_left",
                "slide_right",
                "slide_up",
                "slide_down",
            ):
                side_map = {
                    "slide_left": ("right", "left"),
                    "slide_right": ("left", "right"),
                    "slide_up": ("bottom", "top"),
                    "slide_down": ("top", "bottom"),
                }
                out_side, in_side = side_map[transition_type]
                prev_clip = slide_out(prev_clip, transition_duration, out_side)
                curr_clip = slide_in(curr_clip, transition_duration, in_side)
            elif transition_type == "zoom_in":
                def _scale_in(t: float) -> float:
                    if t >= transition_duration:
                        return 1.0
                    return max(0.01, t / transition_duration)

                curr_clip = curr_clip.fx(resize, lambda t: _scale_in(t)).fx(
                    crossfadein, transition_duration
                )
                prev_clip = crossfadeout(prev_clip, transition_duration)
            elif transition_type == "zoom_out":
                def _scale_out(t: float) -> float:
                    d = prev_clip.duration
                    if t <= d - transition_duration:
                        return 1.0
                    u = (t - (d - transition_duration)) / transition_duration
                    return max(0.01, 1.0 - u)

                prev_clip = prev_clip.fx(resize, lambda t: _scale_out(t)).fx(
                    crossfadeout, transition_duration
                )
                curr_clip = crossfadein(curr_clip, transition_duration)
            elif transition_type == "dissolve":
                prev_clip = crossfadeout(prev_clip, transition_duration)
                curr_clip = crossfadein(curr_clip, transition_duration)
            else:
                prev_clip = prev_clip.fadeout(transition_duration)
                curr_clip = curr_clip.fadein(transition_duration)

            final_clips[-1] = prev_clip
            final_clips.append(curr_clip)

        return final_clips
    
    async def _add_audio(self, video: VideoFileClip, script_data: Dict, voice_config: Dict) -> VideoFileClip:
        """添加音频"""
        try:
            from .ai_service import ai_service
            
            # 生成完整的旁白文本
            full_text = " ".join([scene.get('voiceover', scene.get('text', '')) 
                                for scene in script_data['scenes']])
            
            if not full_text.strip():
                return video
            
            # 生成语音
            audio_path = await ai_service.generate_voice(full_text, voice_config)
            
            if audio_path and os.path.exists(audio_path):
                # 加载音频
                audio_clip = AudioFileClip(audio_path)
                
                # 调整音频长度以匹配视频
                if audio_clip.duration > video.duration:
                    audio_clip = audio_clip.subclip(0, video.duration)
                elif audio_clip.duration < video.duration:
                    # 如果音频较短，可以选择循环或静音填充
                    pass
                
                # 合成音频
                video = video.set_audio(audio_clip)
                
                # 清理临时音频文件
                try:
                    os.unlink(audio_path)
                except:
                    pass
            
            return video
            
        except Exception as e:
            logger.error(f"添加音频失败: {str(e)}")
            return video
    
    async def _export_video(self, video: VideoFileClip, video_id: str, 
                           resolution: str, fps: int, output_format: str) -> str:
        """导出视频"""
        output_filename = f"{video_id}.{output_format}"
        output_path = self.output_dir / output_filename
        
        # 获取编码器设置
        codec_settings = self.output_formats.get(output_format, self.output_formats['mp4'])
        
        # 导出视频
        video.write_videofile(
            str(output_path),
            fps=fps,
            codec=codec_settings['codec'],
            audio_codec=codec_settings['audio_codec'],
            temp_audiofile=str(self.temp_dir / f"{video_id}_temp_audio.m4a"),
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        return str(output_path)
    
    async def _generate_thumbnail(self, video: VideoFileClip, video_id: str) -> str:
        """生成视频缩略图"""
        try:
            thumbnail_path = self.output_dir / f"{video_id}_thumbnail.jpg"
            
            # 获取视频中间帧
            frame_time = video.duration / 2
            frame = video.get_frame(frame_time)
            
            # 保存缩略图
            from PIL import Image
            img = Image.fromarray(frame)
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            img.save(thumbnail_path, 'JPEG', quality=85)
            
            return str(thumbnail_path)
            
        except Exception as e:
            logger.error(f"生成缩略图失败: {str(e)}")
            return None
    
    def get_video_status(self, video_id: str) -> Dict:
        """获取视频处理状态"""
        return self.processing_videos.get(video_id, {'status': 'not_found'})
    
    def cancel_video_processing(self, video_id: str) -> bool:
        """取消视频处理"""
        if video_id in self.processing_videos:
            self.processing_videos[video_id]['status'] = 'cancelled'
            return True
        return False
    
    def cleanup_old_videos(self, max_age_days: int = 7) -> int:
        """清理旧视频文件"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            deleted_count = 0
            
            for file_path in self.output_dir.iterdir():
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
            
            logger.info(f"清理了 {deleted_count} 个旧视频文件")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理旧视频失败: {str(e)}")
            return 0
    
    def get_processing_stats(self) -> Dict:
        """获取处理统计信息"""
        stats = {
            'total_videos': len(self.processing_videos),
            'processing': 0,
            'completed': 0,
            'failed': 0,
            'cancelled': 0
        }
        
        for video_info in self.processing_videos.values():
            status = video_info.get('status', 'unknown')
            if status in stats:
                stats[status] += 1
        
        return stats

# 全局视频服务实例
video_service = VideoService()