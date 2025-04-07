# -*- coding: utf-8 -*-
"""
S3上传模块

该模块提供将报告上传到AWS S3存储桶的功能。
"""

import logging
import os
from typing import Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Uploader:
    """S3上传器类，用于将文件上传到S3存储桶"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化S3上传器

        Args:
            config: S3配置字典
        """
        self.enabled = config.get('enabled', False)
        self.bucket_name = config.get('bucket_name', '')
        self.key_prefix = config.get('key_prefix', '')
        self.region = config.get('region', 'ap-northeast-1')
        self.aws_access_key_id = config.get('aws_access_key_id', None)
        self.aws_secret_access_key = config.get('aws_secret_access_key', None)
        
        # 初始化S3客户端
        if self.enabled:
            self._init_s3_client()
            logger.info(f"S3上传功能已启用，目标存储桶: {self.bucket_name}")
        else:
            logger.info("S3上传功能已禁用")

    def _init_s3_client(self) -> None:
        """
        初始化S3客户端
        """
        try:
            # 如果提供了凭证，则使用提供的凭证
            if self.aws_access_key_id and self.aws_secret_access_key:
                self.s3_client = boto3.client(
                    's3',
                    region_name=self.region,
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key
                )
            else:
                # 否则使用默认凭证提供链
                self.s3_client = boto3.client('s3', region_name=self.region)
            
            # 验证存储桶是否存在
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.debug(f"成功连接到S3存储桶: {self.bucket_name}")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404':
                logger.error(f"S3存储桶不存在: {self.bucket_name}")
            elif error_code == '403':
                logger.error(f"没有访问S3存储桶的权限: {self.bucket_name}")
            else:
                logger.error(f"初始化S3客户端失败: {str(e)}")
            self.enabled = False
        except Exception as e:
            logger.error(f"初始化S3客户端失败: {str(e)}")
            self.enabled = False

    def upload_file(self, file_path: str) -> Optional[str]:
        """
        将文件上传到S3存储桶

        Args:
            file_path: 要上传的文件路径

        Returns:
            上传成功返回S3 URL，失败返回None
        """
        if not self.enabled:
            logger.warning("S3上传功能已禁用，跳过上传")
            return None
        
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"要上传的文件不存在: {file_path}")
                return None
            
            # 构建S3对象键
            file_name = os.path.basename(file_path)
            s3_key = f"{self.key_prefix.rstrip('/')}/{file_name}" if self.key_prefix else file_name
            
            # 上传文件
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            
            # 构建S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{s3_key}"
            logger.info(f"文件已成功上传到S3: {s3_url}")
            return s3_url
        except ClientError as e:
            logger.error(f"上传文件到S3失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"上传文件到S3失败: {str(e)}")
            return None