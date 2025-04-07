# -*- coding: utf-8 -*-
"""
配置加载器模块

该模块提供从YAML配置文件加载配置的功能。
"""

import logging
import os
from typing import Dict, Any, Optional

import yaml

logger = logging.getLogger(__name__)


class ConfigLoader:
    """配置加载器类，用于加载和管理配置"""

    def __init__(self, config_file: str):
        """
        初始化配置加载器

        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
        logger.debug(f"已加载配置文件: {config_file}")

    def _load_config(self) -> Dict[str, Any]:
        """
        从YAML文件加载配置

        Returns:
            配置字典
        """
        try:
            if not os.path.exists(self.config_file):
                logger.warning(f"配置文件不存在: {self.config_file}，将使用默认配置")
                return self._get_default_config()

            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            # 确保配置包含所有必要的部分
            if not config:
                logger.warning("配置文件为空，将使用默认配置")
                return self._get_default_config()

            # 确保配置包含所有必要的部分
            default_config = self._get_default_config()
            for section in default_config:
                if section not in config:
                    logger.warning(f"配置文件缺少 {section} 部分，将使用默认值")
                    config[section] = default_config[section]

            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}，将使用默认配置")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置

        Returns:
            默认配置字典
        """
        return {
            'kubernetes': {
                'use_kubeconfig': True,
                'kubeconfig_path': ''
            },
            's3': {
                'enabled': False,
                'bucket_name': 'eks-info-bucket',
                'key_prefix': 'reports/',
                'region': 'ap-northeast-1',
                'aws_access_key_id': '',
                'aws_secret_access_key': ''
            },
            'report': {
                'output_dir': './reports',
                'filename_format': 'eks-info-report-%Y-%m-%d.html'
            }
        }

    def get_kubernetes_config(self) -> Dict[str, Any]:
        """
        获取Kubernetes配置

        Returns:
            Kubernetes配置字典
        """
        return self.config.get('kubernetes', self._get_default_config()['kubernetes'])

    def get_s3_config(self) -> Dict[str, Any]:
        """
        获取S3上传配置

        Returns:
            S3上传配置字典
        """
        return self.config.get('s3', self._get_default_config()['s3'])

    def get_report_config(self) -> Dict[str, Any]:
        """
        获取报告配置

        Returns:
            报告配置字典
        """
        return self.config.get('report', self._get_default_config()['report'])

    def update_config(self, **kwargs) -> None:
        """
        更新配置

        Args:
            **kwargs: 要更新的配置项
        """
        # 更新S3上传开关
        if 's3_upload' in kwargs and kwargs['s3_upload'] is not None:
            self.config['s3']['enabled'] = kwargs['s3_upload']
            logger.debug(f"已更新S3上传开关: {kwargs['s3_upload']}")

        # 更新报告输出目录
        if 'output_dir' in kwargs and kwargs['output_dir']:
            self.config['report']['output_dir'] = kwargs['output_dir']
            logger.debug(f"已更新报告输出目录: {kwargs['output_dir']}")