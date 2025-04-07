# -*- coding: utf-8 -*-
"""
日志配置模块

该模块提供配置应用程序日志记录的功能。
"""

import logging
import os
from datetime import datetime
from typing import Optional


def setup_logger(log_level: str = 'INFO', log_file: Optional[str] = None) -> None:
    """
    设置日志记录器

    Args:
        log_level: 日志级别，默认为INFO
        log_file: 日志文件路径，如果为None则只输出到控制台
    """
    # 转换日志级别字符串为对应的常量
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 基本配置
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 配置根日志记录器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # 配置文件处理器
        logging.basicConfig(
            level=numeric_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    else:
        # 只配置控制台处理器
        logging.basicConfig(
            level=numeric_level,
            format=log_format
        )
    
    # 设置第三方库的日志级别