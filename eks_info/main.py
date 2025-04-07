# -*- coding: utf-8 -*-
"""EKS信息收集工具主程序

该模块是应用程序的主入口点，整合了所有功能模块。
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

from eks_info.config_loader import ConfigLoader
from eks_info.k8s_client import K8sClient
from eks_info.node_usage import NodeUsageCalculator
from eks_info.report_generator import ReportGenerator
from eks_info.s3_uploader import S3Uploader
from eks_info.logger import setup_logger
from eks_info import __version__


logger = logging.getLogger(__name__)


def parse_arguments():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description='EKS集群信息收集工具')
    parser.add_argument('-c', '--config', default='config.yaml',
                        help='配置文件路径 (默认: config.yaml)')
    parser.add_argument('-o', '--output-dir',
                        help='报告输出目录 (覆盖配置文件中的设置)')
    parser.add_argument('--s3-upload', action='store_true',
                        help='启用S3上传 (覆盖配置文件中的设置)')
    parser.add_argument('--no-s3-upload', action='store_true',
                        help='禁用S3上传 (覆盖配置文件中的设置)')
    parser.add_argument('--cluster-name', default='EKS集群',
                        help='集群名称 (默认: EKS集群)')
    parser.add_argument('-v', '--version', action='version',
                        version=f'%(prog)s {__version__}')
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='日志级别 (默认: INFO)')
    parser.add_argument('--log-file',
                        help='日志文件路径')
    
    return parser.parse_args()


def main():
    """
    主函数
    """
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置日志
    setup_logger(log_level=args.log_level, log_file=args.log_file)
    logger.info(f"启动EKS信息收集工具 v{__version__}")
    
    try:
        # 加载配置
        config_loader = ConfigLoader(args.config)
        logger.debug("配置加载完成")
        
        # 处理命令行参数覆盖配置
        s3_upload = None
        if args.s3_upload:
            s3_upload = True
        elif args.no_s3_upload:
            s3_upload = False
        
        config_loader.update_config(
            s3_upload=s3_upload,
            output_dir=args.output_dir
        )
        
        # 获取配置
        k8s_config = config_loader.get_kubernetes_config()
        s3_config = config_loader.get_s3_config()
        report_config = config_loader.get_report_config()
        
        # 初始化Kubernetes客户端
        k8s_client = K8sClient(
            use_kubeconfig=k8s_config.get('use_kubeconfig', True),
            kubeconfig_path=k8s_config.get('kubeconfig_path')
        )
        
        # 获取节点信息
        logger.info("正在获取节点信息...")
        nodes = k8s_client.get_nodes()
        logger.info(f"获取到 {len(nodes)} 个节点")
        
        # 计算节点使用率
        logger.info("正在计算节点使用率...")
        calculator = NodeUsageCalculator(k8s_client)
        nodes_with_usage = calculator.calculate_node_usage(nodes)
        
        # 生成报告
        logger.info("正在生成报告...")
        report_generator = ReportGenerator(
            cluster_name=args.cluster_name,
            output_dir=report_config.get('output_dir'),
            filename_format=report_config.get('filename_format')
        )
        report_file = report_generator.generate_report(nodes_with_usage)
        logger.info(f"报告已生成: {report_file}")
        
        # 上传到S3
        if s3_config.get('enabled', False):
            logger.info("正在上传报告到S3...")
            s3_uploader = S3Uploader(s3_config)
            s3_url = s3_uploader.upload_file(report_file)
            if s3_url:
                logger.info(f"报告已上传到S3: {s3_url}")
            else:
                logger.warning("上传报告到S3失败")
        
        logger.info("EKS信息收集完成")
        return 0
    except Exception as e:
        logger.error(f"执行过程中发生错误: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())