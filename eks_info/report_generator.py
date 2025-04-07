# -*- coding: utf-8 -*-
"""
报告生成器模块

该模块提供生成HTML格式报告的功能。
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Any

from pretty_html_table import build_table

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成器类，用于生成HTML格式的报告"""

    def __init__(self, cluster_name: str, output_dir: str, filename_format: str):
        """
        初始化报告生成器

        Args:
            cluster_name: 集群名称
            output_dir: 报告输出目录
            filename_format: 报告文件名格式（支持日期格式化）
        """
        self.cluster_name = cluster_name
        self.output_dir = output_dir
        self.filename_format = filename_format
        logger.debug(f"初始化报告生成器，输出目录: {output_dir}")

    def generate_report(self, nodes: List[Dict[str, Any]]) -> str:
        """
        生成HTML格式的报告

        Args:
            nodes: 节点信息列表

        Returns:
            生成的报告文件路径
        """
        try:
            # 确保输出目录存在
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, exist_ok=True)
            
            # 生成报告文件名
            now = datetime.now()
            filename = now.strftime(self.filename_format)
            report_file = os.path.join(self.output_dir, filename)
            
            # 生成HTML内容
            html_content = self._generate_html_content(nodes, now)
            
            # 写入文件
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"报告已生成: {report_file}")
            return report_file
        except Exception as e:
            logger.error(f"生成报告失败: {str(e)}")
            raise

    def _generate_html_content(self, nodes: List[Dict[str, Any]], timestamp: datetime) -> str:
        """
        生成HTML内容

        Args:
            nodes: 节点信息列表
            timestamp: 报告生成时间戳

        Returns:
            HTML内容字符串
        """
        # 准备节点摘要数据
        node_summary = self._prepare_node_summary(nodes)
        
        # 生成节点摘要表格
        summary_table = build_table(
            node_summary,
            'blue_light',
            font_size='medium',
            text_align='center',
            width='100%'
        )
        
        # 准备节点详细信息
        node_details = self._prepare_node_details(nodes)
        
        # 生成HTML内容
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.cluster_name} - 节点信息报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                .header {{ margin-bottom: 20px; }}
                .summary {{ margin-bottom: 30px; }}
                .node-details {{ margin-bottom: 40px; }}
                .node-card {{ border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 20px; }}
                .node-card h3 {{ margin-top: 0; }}
                .node-info {{ display: flex; flex-wrap: wrap; }}
                .node-info-item {{ flex: 1; min-width: 200px; margin-bottom: 10px; }}
                .usage-bar {{ background-color: #f0f0f0; height: 20px; border-radius: 10px; margin-top: 5px; }}
                .usage-fill {{ height: 100%; border-radius: 10px; }}
                .usage-low {{ background-color: #4CAF50; }}
                .usage-medium {{ background-color: #FFC107; }}
                .usage-high {{ background-color: #F44336; }}
                .footer {{ margin-top: 30px; font-size: 0.8em; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{self.cluster_name} - 节点信息报告</h1>
                <p>生成时间: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary">
                <h2>节点摘要</h2>
                {summary_table}
            </div>
            
            <div class="node-details">
                <h2>节点详细信息</h2>
                {node_details}
            </div>
            
            <div class="footer">
                <p>由EKS信息收集工具生成</p>
            </div>
        </body>
        </html>
        """
        
        return html

    def _prepare_node_summary(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        准备节点摘要数据

        Args:
            nodes: 节点信息列表

        Returns:
            节点摘要数据列表
        """
        summary = []
        
        for node in nodes:
            summary.append({
                '节点名称': node['name'],
                '实例类型': node['instance_type'],
                '状态': node['status'],
                'CPU容量': node['capacity']['cpu'],
                'CPU使用率': f"{node['usage']['cpu']['percentage']}%",
                '内存容量': node['capacity']['memory'],
                '内存使用率': f"{node['usage']['memory']['percentage']}%",
                'Pod数量': f"{node['usage']['pods']['used']}/{node['usage']['pods']['total']}",
                'Pod使用率': f"{node['usage']['pods']['percentage']}%"
            })
        
        return summary

    def _prepare_node_details(self, nodes: List[Dict[str, Any]]) -> str:
        """
        准备节点详细信息HTML

        Args:
            nodes: 节点信息列表

        Returns:
            节点详细信息HTML字符串
        """
        details_html = ""
        
        for node in nodes:
            # 确定使用率颜色类
            cpu_class = self._get_usage_class(node['usage']['cpu']['percentage'])
            memory_class = self._get_usage_class(node['usage']['memory']['percentage'])
            pods_class = self._get_usage_class(node['usage']['pods']['percentage'])
            
            # 生成节点卡片HTML
            details_html += f"""
            <div class="node-card">
                <h3>{node['name']}</h3>
                <div class="node-info">
                    <div class="node-info-item">
                        <p><strong>实例类型:</strong> {node['instance_type']}</p>
                        <p><strong>状态:</strong> {node['status']}</p>
                        <p><strong>创建时间:</strong> {node['creation_timestamp']}</p>
                    </div>
                    <div class="node-info-item">
                        <p><strong>CPU:</strong> {node['capacity']['cpu']}</p>
                        <p><strong>内存:</strong> {node['capacity']['memory']}</p>
                        <p><strong>Pod容量:</strong> {node['capacity']['pods']}</p>
                    </div>
                </div>
                
                <div class="node-usage">
                    <div class="node-info-item">
                        <p><strong>CPU使用率:</strong> {node['usage']['cpu']['percentage']}%</p>
                        <div class="usage-bar">
                            <div class="usage-fill {cpu_class}" style="width: {min(node['usage']['cpu']['percentage'], 100)}%"></div>
                        </div>
                    </div>
                    
                    <div class="node-info-item">
                        <p><strong>内存使用率:</strong> {node['usage']['memory']['percentage']}%</p>
                        <div class="usage-bar">
                            <div class="usage-fill {memory_class}" style="width: {min(node['usage']['memory']['percentage'], 100)}%"></div>
                        </div>
                    </div>
                    
                    <div class="node-info-item">
                        <p><strong>Pod使用率:</strong> {node['usage']['pods']['used']}/{node['capacity']['pods']} ({node['usage']['pods']['percentage']}%)</p>
                        <div class="usage-bar">
                            <div class="usage-fill {pods_class}" style="width: {min(node['usage']['pods']['percentage'], 100)}%"></div>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        return details_html
        
    def _get_usage_class(self, percentage: float) -> str:
        """
        根据使用率百分比获取对应的CSS类名

        Args:
            percentage: 使用率百分比

        Returns:
            CSS类名
        """
        if percentage < 50:
            return "usage-low"
        elif percentage < 80:
            return "usage-medium"
        else:
            return "usage-high"