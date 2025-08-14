import re
import os
from typing import Any, Dict, List

try:
    import bleach
    HAS_BLEACH = True
except ImportError:
    HAS_BLEACH = False

class SecurityValidator:
    """安全验证工具类"""
    
    # 允许的文件类型
    ALLOWED_IMAGE_TYPES = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    ALLOWED_VIDEO_TYPES = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
    ALLOWED_AUDIO_TYPES = {'.mp3', '.wav', '.aac', '.ogg', '.flac'}
    ALLOWED_DOCUMENT_TYPES = {'.pdf', '.txt', '.md'}
    
    # 危险的文件扩展名
    DANGEROUS_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', 
        '.jar', '.php', '.asp', '.aspx', '.jsp', '.py', '.rb', '.pl'
    }
    
    # HTML标签白名单
    ALLOWED_HTML_TAGS = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    ALLOWED_HTML_ATTRIBUTES = {}
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """清理HTML内容"""
        if not text:
            return text
        
        if HAS_BLEACH:
            return bleach.clean(
                text,
                tags=SecurityValidator.ALLOWED_HTML_TAGS,
                attributes=SecurityValidator.ALLOWED_HTML_ATTRIBUTES,
                strip=True
            )
        else:
            # 简单的HTML标签移除
            import re
            # 移除所有HTML标签
            clean_text = re.sub(r'<[^>]+>', '', text)
            # 移除多余的空白字符
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            return clean_text
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """验证文件名安全性"""
        if not filename:
            return False
        
        # 检查文件名长度
        if len(filename) > 255:
            return False
        
        # 检查危险字符
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in filename for char in dangerous_chars):
            return False
        
        # 检查文件扩展名
        ext = os.path.splitext(filename)[1].lower()
        if ext in SecurityValidator.DANGEROUS_EXTENSIONS:
            return False
        
        return True
    
    @staticmethod
    def validate_file_type(filename: str, allowed_types: set) -> bool:
        """验证文件类型"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in allowed_types
    
    @staticmethod
    def validate_template_id(template_id: str) -> bool:
        """验证模板ID格式"""
        if not template_id:
            return False
        
        # 只允许字母、数字、下划线和连字符
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, template_id))
    
    @staticmethod
    def validate_script_content(script: Dict) -> Dict:
        """验证和清理脚本内容"""
        if not isinstance(script, dict):
            raise ValueError("Script must be a dictionary")
        
        # 清理标题
        if 'title' in script:
            script['title'] = SecurityValidator.sanitize_html(script['title'])
            if len(script['title']) > 200:
                script['title'] = script['title'][:200]
        
        # 清理场景内容
        if 'scenes' in script and isinstance(script['scenes'], list):
            for scene in script['scenes']:
                if isinstance(scene, dict):
                    if 'text' in scene:
                        scene['text'] = SecurityValidator.sanitize_html(scene['text'])
                        if len(scene['text']) > 500:
                            scene['text'] = scene['text'][:500]
                    
                    if 'voiceover' in scene:
                        scene['voiceover'] = SecurityValidator.sanitize_html(scene['voiceover'])
                        if len(scene['voiceover']) > 1000:
                            scene['voiceover'] = scene['voiceover'][:1000]
        
        return script
    
    @staticmethod
    def validate_voice_config(voice_config: Dict) -> bool:
        """验证语音配置"""
        if not isinstance(voice_config, dict):
            return False
        
        # 验证提供商
        allowed_providers = {'gtts', 'openai', 'edge'}
        provider = voice_config.get('provider', '')
        if provider not in allowed_providers:
            return False
        
        # 验证速度范围
        speed = voice_config.get('speed', 1.0)
        if not isinstance(speed, (int, float)) or speed < 0.5 or speed > 2.0:
            return False
        
        return True
    
    @staticmethod
    def validate_export_config(export_config: Dict) -> bool:
        """验证导出配置"""
        if not isinstance(export_config, dict):
            return False
        
        # 验证分辨率
        allowed_resolutions = {'360p', '480p', '720p', '1080p', '1440p', '4k'}
        resolution = export_config.get('resolution', '')
        if resolution not in allowed_resolutions:
            return False
        
        # 验证帧率
        fps = export_config.get('fps', 30)
        if not isinstance(fps, int) or fps < 15 or fps > 60:
            return False
        
        # 验证格式
        allowed_formats = {'mp4', 'webm', 'avi', 'mov'}
        format_type = export_config.get('format', '')
        if format_type not in allowed_formats:
            return False
        
        return True

class ContentValidator:
    """内容验证工具类"""
    
    @staticmethod
    def validate_text_length(text: str, max_length: int) -> bool:
        """验证文本长度"""
        return len(text) <= max_length if text else True
    
    @staticmethod
    def validate_duration(duration: float) -> bool:
        """验证时长范围"""
        return 1.0 <= duration <= 300.0  # 1秒到5分钟
    
    @staticmethod
    def validate_file_size(file_size: int, max_size: int) -> bool:
        """验证文件大小"""
        return 0 < file_size <= max_size
    
    @staticmethod
    def detect_spam_content(text: str) -> bool:
        """检测垃圾内容"""
        if not text:
            return False
        
        # 简单的垃圾内容检测
        spam_patterns = [
            r'(免费|赚钱|点击|链接).{0,10}(http|www)',
            r'(加微信|QQ群|联系方式)',
            r'(广告|推广|营销).{0,20}(联系|咨询)',
        ]
        
        text_lower = text.lower()
        for pattern in spam_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False

# 创建验证器实例
security_validator = SecurityValidator()
content_validator = ContentValidator()