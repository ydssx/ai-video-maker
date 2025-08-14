import os
import shutil
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Tuple, BinaryIO
import logging
from PIL import Image, ImageOps
import tempfile
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.uploads_dir = self.base_dir / "uploads"
        self.thumbnails_dir = self.base_dir / "thumbnails"
        self.temp_dir = self.base_dir / "temp"
        self.output_dir = self.base_dir / "output"
        
        # 创建必要的目录
        for directory in [self.uploads_dir, self.thumbnails_dir, self.temp_dir, self.output_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # 支持的文件类型
        self.supported_image_types = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        self.supported_video_types = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
        self.supported_audio_types = {'.mp3', '.wav', '.aac', '.ogg', '.flac', '.m4a'}
        self.supported_document_types = {'.pdf', '.doc', '.docx', '.txt', '.md'}
        
        # 文件大小限制 (字节)
        self.max_file_sizes = {
            'image': 10 * 1024 * 1024,  # 10MB
            'video': 100 * 1024 * 1024,  # 100MB
            'audio': 50 * 1024 * 1024,   # 50MB
            'document': 20 * 1024 * 1024  # 20MB
        }
    
    def get_file_type(self, filename: str) -> str:
        """获取文件类型"""
        ext = Path(filename).suffix.lower()
        
        if ext in self.supported_image_types:
            return 'image'
        elif ext in self.supported_video_types:
            return 'video'
        elif ext in self.supported_audio_types:
            return 'audio'
        elif ext in self.supported_document_types:
            return 'document'
        else:
            return 'other'
    
    def is_supported_file(self, filename: str) -> bool:
        """检查文件是否支持"""
        file_type = self.get_file_type(filename)
        return file_type != 'other'
    
    def validate_file_size(self, file_size: int, file_type: str) -> bool:
        """验证文件大小"""
        max_size = self.max_file_sizes.get(file_type, 10 * 1024 * 1024)
        return file_size <= max_size
    
    def generate_file_id(self) -> str:
        """生成文件ID"""
        return str(uuid.uuid4())
    
    def get_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    async def save_uploaded_file(self, file: BinaryIO, filename: str, 
                                user_id: int) -> Dict[str, any]:
        """保存上传的文件"""
        try:
            # 生成文件ID和路径
            file_id = self.generate_file_id()
            file_ext = Path(filename).suffix.lower()
            file_type = self.get_file_type(filename)
            
            # 检查文件类型
            if not self.is_supported_file(filename):
                raise ValueError(f"不支持的文件类型: {file_ext}")
            
            # 创建用户目录
            user_dir = self.uploads_dir / str(user_id)
            user_dir.mkdir(exist_ok=True)
            
            # 保存文件
            file_path = user_dir / f"{file_id}{file_ext}"
            
            # 写入文件
            with open(file_path, "wb") as f:
                content = await file.read()
                file_size = len(content)
                
                # 验证文件大小
                if not self.validate_file_size(file_size, file_type):
                    raise ValueError(f"文件大小超过限制: {file_size} bytes")
                
                f.write(content)
            
            # 计算文件哈希
            file_hash = self.get_file_hash(file_path)
            
            # 生成缩略图
            thumbnail_path = None
            if file_type == 'image':
                thumbnail_path = await self.generate_image_thumbnail(file_path, file_id)
            elif file_type == 'video':
                thumbnail_path = await self.generate_video_thumbnail(file_path, file_id)
            
            # 获取文件元数据
            metadata = await self.get_file_metadata(file_path, file_type)
            
            return {
                'file_id': file_id,
                'filename': filename,
                'file_path': str(file_path),
                'file_type': file_type,
                'file_size': file_size,
                'file_hash': file_hash,
                'thumbnail_path': thumbnail_path,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"文件保存失败: {str(e)}")
            # 清理可能创建的文件
            if 'file_path' in locals() and file_path.exists():
                file_path.unlink()
            raise
    
    async def generate_image_thumbnail(self, image_path: Path, file_id: str) -> Optional[str]:
        """生成图片缩略图"""
        try:
            thumbnail_path = self.thumbnails_dir / f"{file_id}_thumb.jpg"
            
            with Image.open(image_path) as img:
                # 转换为RGB模式（处理RGBA等格式）
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # 生成缩略图
                img.thumbnail((300, 300), Image.Resampling.LANCZOS)
                img.save(thumbnail_path, 'JPEG', quality=85)
            
            return str(thumbnail_path)
            
        except Exception as e:
            logger.error(f"生成图片缩略图失败: {str(e)}")
            return None
    
    async def generate_video_thumbnail(self, video_path: Path, file_id: str) -> Optional[str]:
        """生成视频缩略图"""
        try:
            import cv2
            
            thumbnail_path = self.thumbnails_dir / f"{file_id}_thumb.jpg"
            
            # 打开视频文件
            cap = cv2.VideoCapture(str(video_path))
            
            # 跳到视频中间位置
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)
            
            # 读取帧
            ret, frame = cap.read()
            if ret:
                # 调整大小
                height, width = frame.shape[:2]
                if width > 300 or height > 300:
                    scale = min(300/width, 300/height)
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    frame = cv2.resize(frame, (new_width, new_height))
                
                # 保存缩略图
                cv2.imwrite(str(thumbnail_path), frame)
                cap.release()
                return str(thumbnail_path)
            
            cap.release()
            return None
            
        except ImportError:
            logger.warning("OpenCV未安装，无法生成视频缩略图")
            return None
        except Exception as e:
            logger.error(f"生成视频缩略图失败: {str(e)}")
            return None
    
    async def get_file_metadata(self, file_path: Path, file_type: str) -> Dict:
        """获取文件元数据"""
        metadata = {
            'created_at': datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
            'modified_at': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        }
        
        try:
            if file_type == 'image':
                with Image.open(file_path) as img:
                    metadata.update({
                        'width': img.width,
                        'height': img.height,
                        'format': img.format,
                        'mode': img.mode
                    })
            
            elif file_type == 'video':
                try:
                    import cv2
                    cap = cv2.VideoCapture(str(file_path))
                    
                    metadata.update({
                        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                        'fps': cap.get(cv2.CAP_PROP_FPS),
                        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                        'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
                    })
                    
                    cap.release()
                except ImportError:
                    pass
            
            elif file_type == 'audio':
                try:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_file(file_path)
                    
                    metadata.update({
                        'duration': len(audio) / 1000.0,  # 转换为秒
                        'channels': audio.channels,
                        'sample_rate': audio.frame_rate,
                        'bit_depth': audio.sample_width * 8
                    })
                except ImportError:
                    pass
        
        except Exception as e:
            logger.error(f"获取文件元数据失败: {str(e)}")
        
        return metadata
    
    def get_file_url(self, file_path: str, file_type: str = 'file') -> str:
        """获取文件访问URL"""
        # 将绝对路径转换为相对路径
        rel_path = Path(file_path).relative_to(self.base_dir)
        return f"/api/files/{file_type}/{rel_path}"
    
    def delete_file(self, file_path: str, thumbnail_path: str = None) -> bool:
        """删除文件"""
        try:
            # 删除主文件
            if os.path.exists(file_path):
                os.unlink(file_path)
            
            # 删除缩略图
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.unlink(thumbnail_path)
            
            return True
        except Exception as e:
            logger.error(f"删除文件失败: {str(e)}")
            return False
    
    def create_temp_file(self, suffix: str = '') -> str:
        """创建临时文件"""
        temp_file = tempfile.NamedTemporaryFile(
            dir=self.temp_dir,
            suffix=suffix,
            delete=False
        )
        temp_file.close()
        return temp_file.name
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """清理临时文件"""
        try:
            current_time = datetime.now().timestamp()
            deleted_count = 0
            
            for file_path in self.temp_dir.iterdir():
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_hours * 3600:  # 转换为秒
                        file_path.unlink()
                        deleted_count += 1
            
            logger.info(f"清理了 {deleted_count} 个临时文件")
            return deleted_count
            
        except Exception as e:
            logger.error(f"清理临时文件失败: {str(e)}")
            return 0
    
    def get_storage_stats(self) -> Dict:
        """获取存储统计信息"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_type': {}
        }
        
        try:
            for file_path in self.uploads_dir.rglob('*'):
                if file_path.is_file():
                    stats['total_files'] += 1
                    file_size = file_path.stat().st_size
                    stats['total_size'] += file_size
                    
                    file_type = self.get_file_type(file_path.name)
                    if file_type not in stats['by_type']:
                        stats['by_type'][file_type] = {'count': 0, 'size': 0}
                    
                    stats['by_type'][file_type]['count'] += 1
                    stats['by_type'][file_type]['size'] += file_size
        
        except Exception as e:
            logger.error(f"获取存储统计失败: {str(e)}")
        
        return stats
    
    def optimize_storage(self):
        """优化存储空间"""
        # 清理临时文件
        temp_cleaned = self.cleanup_temp_files()
        
        # 可以添加更多优化逻辑，如：
        # - 压缩旧文件
        # - 删除重复文件
        # - 清理无效的缩略图
        
        return {
            'temp_files_cleaned': temp_cleaned
        }

# 全局文件服务实例
file_service = FileService()