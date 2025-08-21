"""
Amazon S3 存储实现
"""
import os
from typing import BinaryIO, Optional, Dict, Any, Tuple

import boto3
from botocore.exceptions import ClientError

from .base import StorageBackend
from ...exceptions import StorageError


class S3Storage(StorageBackend):
    """Amazon S3 存储实现"""
    
    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        region_name: str = None,
        endpoint_url: str = None,
    ):
        """
        初始化 S3 存储
        
        Args:
            bucket_name: S3 存储桶名称
            aws_access_key_id: AWS 访问密钥 ID
            aws_secret_access_key: AWS 密钥
            region_name: 区域名称
            endpoint_url: 自定义终端节点 URL（用于兼容其他 S3 兼容存储）
        """
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
            endpoint_url=endpoint_url or None,
        )
    
    async def upload_fileobj(
        self,
        file_path: str,
        file_obj: BinaryIO,
        content_type: str = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> None:
        """
        上传文件对象到 S3
        """
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            if metadata:
                extra_args['Metadata'] = metadata
                
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                file_path,
                ExtraArgs=extra_args
            )
        except ClientError as e:
            raise StorageError(f"Failed to upload file to S3: {str(e)}")
    
    def get_download_url(self, file_path: str, filename: str, expires_in: int = 3600) -> str:
        """
        获取预签名的下载 URL
        """
        try:
            return self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_path,
                    'ResponseContentDisposition': f'attachment; filename="{filename}"'
                },
                ExpiresIn=expires_in
            )
        except ClientError as e:
            raise StorageError(f"Failed to generate download URL: {str(e)}")
    
    def delete_file(self, file_path: str) -> None:
        """
        删除 S3 中的文件
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_path
            )
        except ClientError as e:
            # 如果文件不存在，忽略错误
            if e.response['Error']['Code'] != 'NoSuchKey':
                raise StorageError(f"Failed to delete file from S3: {str(e)}")
    
    def generate_upload_url(
        self,
        file_path: str,
        content_type: str,
        file_size: int,
        metadata: Optional[Dict[str, str]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        生成预签名的上传 URL
        """
        try:
            # 准备上传参数
            conditions = [
                ["content-length-range", file_size, file_size],
                {"Content-Type": content_type},
            ]
            
            # 添加元数据条件
            if metadata:
                for key, value in metadata.items():
                    conditions.append({f"x-amz-meta-{key}": value})
            
            # 生成预签名 POST 策略
            presigned_post = self.s3_client.generate_presigned_post(
                self.bucket_name,
                file_path,
                Fields={
                    'Content-Type': content_type,
                    **{f'x-amz-meta-{k}': v for k, v in (metadata or {}).items()}
                },
                Conditions=conditions,
                ExpiresIn=3600  # 1 小时过期
            )
            
            return presigned_post['url'], presigned_post['fields']
            
        except ClientError as e:
            raise StorageError(f"Failed to generate upload URL: {str(e)}")
