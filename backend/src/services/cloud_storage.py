"""
云存储服务模块
支持多种云存储提供商：AWS S3, 阿里云OSS, 腾讯云COS, 七牛云等
"""

import os
import uuid
import mimetypes
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pathlib import Path
import asyncio
from datetime import datetime, timedelta
import hashlib
import json
import logging

logger = logging.getLogger(__name__)

# 云存储提供商SDK
try:
    import boto3
    from botocore.exceptions import ClientError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

try:
    import oss2
    ALIYUN_AVAILABLE = True
except ImportError:
    ALIYUN_AVAILABLE = False

try:
    from qcloud_cos import CosConfig, CosS3Client
    TENCENT_AVAILABLE = True
except ImportError:
    TENCENT_AVAILABLE = False

try:
    from qiniu import Auth, put_file, BucketManager
    QINIU_AVAILABLE = True
except ImportError:
    QINIU_AVAILABLE = False


class CloudStorageProvider(ABC):
    """云存储提供商抽象基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = self.__class__.__name__.lower().replace('provider', '')
    
    @abstractmethod
    async def upload_file(self, local_path: str, remote_path: str, metadata: Dict = None) -> Dict[str, Any]:
        """上传文件到云存储"""
        pass
    
    @abstractmethod
    async def download_file(self, remote_path: str, local_path: str) -> bool:
        """从云存储下载文件"""
        pass
    
    @abstractmethod
    async def delete_file(self, remote_path: str) -> bool:
        """删除云存储中的文件"""
        pass
    
    @abstractmethod
    async def get_file_url(self, remote_path: str, expires_in: int = 3600) -> str:
        """获取文件的访问URL"""
        pass
    
    @abstractmethod
    async def list_files(self, prefix: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        """列出文件"""
        pass
    
    def generate_remote_path(self, filename: str, folder: str = "videos") -> str:
        """生成远程文件路径"""
        file_ext = Path(filename).suffix
        unique_name = f"{uuid.uuid4()}{file_ext}"
        date_path = datetime.now().strftime("%Y/%m/%d")
        return f"{folder}/{date_path}/{unique_name}"


class AWSS3Provider(CloudStorageProvider):
    """AWS S3 存储提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not AWS_AVAILABLE:
            raise ImportError("boto3 is required for AWS S3 support")
        
        self.client = boto3.client(
            's3',
            aws_access_key_id=config['access_key'],
            aws_secret_access_key=config['secret_key'],
            region_name=config.get('region', 'us-east-1')
        )
        self.bucket_name = config['bucket_name']
    
    async def upload_file(self, local_path: str, remote_path: str, metadata: Dict = None) -> Dict[str, Any]:
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            # 设置内容类型
            content_type, _ = mimetypes.guess_type(local_path)
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.client.upload_file(local_path, self.bucket_name, remote_path, ExtraArgs=extra_args)
            
            return {
                'success': True,
                'provider': 'aws_s3',
                'remote_path': remote_path,
                'url': f"https://{self.bucket_name}.s3.amazonaws.com/{remote_path}"
            }
        except ClientError as e:
            logger.error(f"AWS S3 upload failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def download_file(self, remote_path: str, local_path: str) -> bool:
        try:
            self.client.download_file(self.bucket_name, remote_path, local_path)
            return True
        except ClientError as e:
            logger.error(f"AWS S3 download failed: {e}")
            return False
    
    async def delete_file(self, remote_path: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=remote_path)
            return True
        except ClientError as e:
            logger.error(f"AWS S3 delete failed: {e}")
            return False
    
    async def get_file_url(self, remote_path: str, expires_in: int = 3600) -> str:
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': remote_path},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"AWS S3 URL generation failed: {e}")
            return ""
    
    async def list_files(self, prefix: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=limit
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj['ETag'].strip('"')
                })
            
            return files
        except ClientError as e:
            logger.error(f"AWS S3 list failed: {e}")
            return []


class AliyunOSSProvider(CloudStorageProvider):
    """阿里云OSS存储提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not ALIYUN_AVAILABLE:
            raise ImportError("oss2 is required for Aliyun OSS support")
        
        auth = oss2.Auth(config['access_key'], config['secret_key'])
        self.bucket = oss2.Bucket(auth, config['endpoint'], config['bucket_name'])
    
    async def upload_file(self, local_path: str, remote_path: str, metadata: Dict = None) -> Dict[str, Any]:
        try:
            headers = {}
            if metadata:
                for key, value in metadata.items():
                    headers[f'x-oss-meta-{key}'] = str(value)
            
            # 设置内容类型
            content_type, _ = mimetypes.guess_type(local_path)
            if content_type:
                headers['Content-Type'] = content_type
            
            result = self.bucket.put_object_from_file(remote_path, local_path, headers=headers)
            
            return {
                'success': True,
                'provider': 'aliyun_oss',
                'remote_path': remote_path,
                'url': f"https://{self.bucket.bucket_name}.{self.bucket.endpoint.replace('https://', '')}/{remote_path}",
                'etag': result.etag
            }
        except Exception as e:
            logger.error(f"Aliyun OSS upload failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def download_file(self, remote_path: str, local_path: str) -> bool:
        try:
            self.bucket.get_object_to_file(remote_path, local_path)
            return True
        except Exception as e:
            logger.error(f"Aliyun OSS download failed: {e}")
            return False
    
    async def delete_file(self, remote_path: str) -> bool:
        try:
            self.bucket.delete_object(remote_path)
            return True
        except Exception as e:
            logger.error(f"Aliyun OSS delete failed: {e}")
            return False
    
    async def get_file_url(self, remote_path: str, expires_in: int = 3600) -> str:
        try:
            url = self.bucket.sign_url('GET', remote_path, expires_in)
            return url
        except Exception as e:
            logger.error(f"Aliyun OSS URL generation failed: {e}")
            return ""
    
    async def list_files(self, prefix: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        try:
            files = []
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix, max_keys=limit):
                files.append({
                    'key': obj.key,
                    'size': obj.size,
                    'last_modified': obj.last_modified,
                    'etag': obj.etag.strip('"')
                })
            return files
        except Exception as e:
            logger.error(f"Aliyun OSS list failed: {e}")
            return []


class TencentCOSProvider(CloudStorageProvider):
    """腾讯云COS存储提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not TENCENT_AVAILABLE:
            raise ImportError("cos-python-sdk-v5 is required for Tencent COS support")
        
        cos_config = CosConfig(
            Region=config['region'],
            SecretId=config['access_key'],
            SecretKey=config['secret_key']
        )
        self.client = CosS3Client(cos_config)
        self.bucket_name = config['bucket_name']
    
    async def upload_file(self, local_path: str, remote_path: str, metadata: Dict = None) -> Dict[str, Any]:
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            # 设置内容类型
            content_type, _ = mimetypes.guess_type(local_path)
            if content_type:
                extra_args['ContentType'] = content_type
            
            response = self.client.upload_file(
                Bucket=self.bucket_name,
                LocalFilePath=local_path,
                Key=remote_path,
                **extra_args
            )
            
            return {
                'success': True,
                'provider': 'tencent_cos',
                'remote_path': remote_path,
                'url': f"https://{self.bucket_name}.cos.{self.client._conf._region}.myqcloud.com/{remote_path}",
                'etag': response.get('ETag', '').strip('"')
            }
        except Exception as e:
            logger.error(f"Tencent COS upload failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def download_file(self, remote_path: str, local_path: str) -> bool:
        try:
            self.client.download_file(
                Bucket=self.bucket_name,
                Key=remote_path,
                DestFilePath=local_path
            )
            return True
        except Exception as e:
            logger.error(f"Tencent COS download failed: {e}")
            return False
    
    async def delete_file(self, remote_path: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=remote_path)
            return True
        except Exception as e:
            logger.error(f"Tencent COS delete failed: {e}")
            return False
    
    async def get_file_url(self, remote_path: str, expires_in: int = 3600) -> str:
        try:
            url = self.client.get_presigned_download_url(
                Bucket=self.bucket_name,
                Key=remote_path,
                Expired=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"Tencent COS URL generation failed: {e}")
            return ""
    
    async def list_files(self, prefix: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        try:
            response = self.client.list_objects(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=limit
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'],
                    'etag': obj['ETag'].strip('"')
                })
            
            return files
        except Exception as e:
            logger.error(f"Tencent COS list failed: {e}")
            return []


class QiniuProvider(CloudStorageProvider):
    """七牛云存储提供商"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        if not QINIU_AVAILABLE:
            raise ImportError("qiniu is required for Qiniu support")
        
        self.auth = Auth(config['access_key'], config['secret_key'])
        self.bucket_name = config['bucket_name']
        self.domain = config.get('domain', '')
        self.bucket_manager = BucketManager(self.auth)
    
    async def upload_file(self, local_path: str, remote_path: str, metadata: Dict = None) -> Dict[str, Any]:
        try:
            token = self.auth.upload_token(self.bucket_name, remote_path)
            ret, info = put_file(token, remote_path, local_path)
            
            if info.status_code == 200:
                url = f"http://{self.domain}/{remote_path}" if self.domain else ""
                return {
                    'success': True,
                    'provider': 'qiniu',
                    'remote_path': remote_path,
                    'url': url,
                    'hash': ret.get('hash', '')
                }
            else:
                return {'success': False, 'error': f"Upload failed with status {info.status_code}"}
        except Exception as e:
            logger.error(f"Qiniu upload failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def download_file(self, remote_path: str, local_path: str) -> bool:
        try:
            if not self.domain:
                return False
            
            import requests
            url = f"http://{self.domain}/{remote_path}"
            response = requests.get(url)
            
            if response.status_code == 200:
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                return True
            return False
        except Exception as e:
            logger.error(f"Qiniu download failed: {e}")
            return False
    
    async def delete_file(self, remote_path: str) -> bool:
        try:
            ret, info = self.bucket_manager.delete(self.bucket_name, remote_path)
            return info.status_code == 200
        except Exception as e:
            logger.error(f"Qiniu delete failed: {e}")
            return False
    
    async def get_file_url(self, remote_path: str, expires_in: int = 3600) -> str:
        try:
            if not self.domain:
                return ""
            
            base_url = f"http://{self.domain}/{remote_path}"
            private_url = self.auth.private_download_url(base_url, expires=expires_in)
            return private_url
        except Exception as e:
            logger.error(f"Qiniu URL generation failed: {e}")
            return ""
    
    async def list_files(self, prefix: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        try:
            ret, eof, info = self.bucket_manager.list(self.bucket_name, prefix=prefix, limit=limit)
            
            if info.status_code == 200:
                files = []
                for item in ret.get('items', []):
                    files.append({
                        'key': item['key'],
                        'size': item['fsize'],
                        'last_modified': datetime.fromtimestamp(item['putTime'] / 10000000).isoformat(),
                        'hash': item['hash']
                    })
                return files
            return []
        except Exception as e:
            logger.error(f"Qiniu list failed: {e}")
            return []


class CloudStorageManager:
    """云存储管理器"""
    
    def __init__(self):
        self.providers = {}
        self.default_provider = None
        self.load_config()
    
    def load_config(self):
        """加载云存储配置"""
        config_file = Path("config/cloud_storage.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.setup_providers(config)
            except Exception as e:
                logger.error(f"Failed to load cloud storage config: {e}")
        
        # 从环境变量加载配置
        self.load_from_env()
    
    def load_from_env(self):
        """从环境变量加载配置"""
        # AWS S3
        if all(key in os.environ for key in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_S3_BUCKET']):
            aws_config = {
                'access_key': os.environ['AWS_ACCESS_KEY_ID'],
                'secret_key': os.environ['AWS_SECRET_ACCESS_KEY'],
                'bucket_name': os.environ['AWS_S3_BUCKET'],
                'region': os.environ.get('AWS_REGION', 'us-east-1')
            }
            try:
                self.providers['aws_s3'] = AWSS3Provider(aws_config)
                if not self.default_provider:
                    self.default_provider = 'aws_s3'
            except ImportError:
                logger.warning("AWS S3 configured but boto3 not installed")
        
        # 阿里云OSS
        if all(key in os.environ for key in ['ALIYUN_ACCESS_KEY', 'ALIYUN_SECRET_KEY', 'ALIYUN_OSS_BUCKET', 'ALIYUN_OSS_ENDPOINT']):
            oss_config = {
                'access_key': os.environ['ALIYUN_ACCESS_KEY'],
                'secret_key': os.environ['ALIYUN_SECRET_KEY'],
                'bucket_name': os.environ['ALIYUN_OSS_BUCKET'],
                'endpoint': os.environ['ALIYUN_OSS_ENDPOINT']
            }
            try:
                self.providers['aliyun_oss'] = AliyunOSSProvider(oss_config)
                if not self.default_provider:
                    self.default_provider = 'aliyun_oss'
            except ImportError:
                logger.warning("Aliyun OSS configured but oss2 not installed")
        
        # 腾讯云COS
        if all(key in os.environ for key in ['TENCENT_SECRET_ID', 'TENCENT_SECRET_KEY', 'TENCENT_COS_BUCKET', 'TENCENT_COS_REGION']):
            cos_config = {
                'access_key': os.environ['TENCENT_SECRET_ID'],
                'secret_key': os.environ['TENCENT_SECRET_KEY'],
                'bucket_name': os.environ['TENCENT_COS_BUCKET'],
                'region': os.environ['TENCENT_COS_REGION']
            }
            try:
                self.providers['tencent_cos'] = TencentCOSProvider(cos_config)
                if not self.default_provider:
                    self.default_provider = 'tencent_cos'
            except ImportError:
                logger.warning("Tencent COS configured but cos-python-sdk-v5 not installed")
        
        # 七牛云
        if all(key in os.environ for key in ['QINIU_ACCESS_KEY', 'QINIU_SECRET_KEY', 'QINIU_BUCKET']):
            qiniu_config = {
                'access_key': os.environ['QINIU_ACCESS_KEY'],
                'secret_key': os.environ['QINIU_SECRET_KEY'],
                'bucket_name': os.environ['QINIU_BUCKET'],
                'domain': os.environ.get('QINIU_DOMAIN', '')
            }
            try:
                self.providers['qiniu'] = QiniuProvider(qiniu_config)
                if not self.default_provider:
                    self.default_provider = 'qiniu'
            except ImportError:
                logger.warning("Qiniu configured but qiniu SDK not installed")
    
    def setup_providers(self, config: Dict[str, Any]):
        """设置云存储提供商"""
        for provider_name, provider_config in config.get('providers', {}).items():
            if not provider_config.get('enabled', False):
                continue
            
            try:
                if provider_name == 'aws_s3' and AWS_AVAILABLE:
                    self.providers[provider_name] = AWSS3Provider(provider_config)
                elif provider_name == 'aliyun_oss' and ALIYUN_AVAILABLE:
                    self.providers[provider_name] = AliyunOSSProvider(provider_config)
                elif provider_name == 'tencent_cos' and TENCENT_AVAILABLE:
                    self.providers[provider_name] = TencentCOSProvider(provider_config)
                elif provider_name == 'qiniu' and QINIU_AVAILABLE:
                    self.providers[provider_name] = QiniuProvider(provider_config)
            except Exception as e:
                logger.error(f"Failed to setup {provider_name}: {e}")
        
        # 设置默认提供商
        self.default_provider = config.get('default_provider')
        if self.default_provider not in self.providers:
            self.default_provider = next(iter(self.providers.keys())) if self.providers else None
    
    def get_provider(self, provider_name: Optional[str] = None) -> Optional[CloudStorageProvider]:
        """获取云存储提供商"""
        if provider_name:
            return self.providers.get(provider_name)
        return self.providers.get(self.default_provider) if self.default_provider else None
    
    async def upload_file(self, local_path: str, remote_path: str = None, provider_name: str = None, metadata: Dict = None) -> Dict[str, Any]:
        """上传文件到云存储"""
        provider = self.get_provider(provider_name)
        if not provider:
            return {'success': False, 'error': 'No cloud storage provider available'}
        
        if not remote_path:
            remote_path = provider.generate_remote_path(Path(local_path).name)
        
        return await provider.upload_file(local_path, remote_path, metadata)
    
    async def download_file(self, remote_path: str, local_path: str, provider_name: str = None) -> bool:
        """从云存储下载文件"""
        provider = self.get_provider(provider_name)
        if not provider:
            return False
        
        return await provider.download_file(remote_path, local_path)
    
    async def delete_file(self, remote_path: str, provider_name: str = None) -> bool:
        """删除云存储中的文件"""
        provider = self.get_provider(provider_name)
        if not provider:
            return False
        
        return await provider.delete_file(remote_path)
    
    async def get_file_url(self, remote_path: str, expires_in: int = 3600, provider_name: str = None) -> str:
        """获取文件的访问URL"""
        provider = self.get_provider(provider_name)
        if not provider:
            return ""
        
        return await provider.get_file_url(remote_path, expires_in)
    
    def list_providers(self) -> List[str]:
        """列出可用的云存储提供商"""
        return list(self.providers.keys())
    
    def is_enabled(self) -> bool:
        """检查是否启用了云存储"""
        return len(self.providers) > 0


# 全局云存储管理器实例
cloud_storage = CloudStorageManager()