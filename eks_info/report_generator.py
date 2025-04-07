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
        if isinstance(node_summary, list) and len(node_summary) > 0:
            try:
                summary_table = build_table(
                    node_summary,
                    'blue_light',
                    font_size='medium',
                    text_align='center',
                    width='100%'
                )
            except AttributeError as e:
                logger.warning(f"生成表格时出错: {str(e)}")
                summary_table = "<p>生成节点摘要表格时出错</p>"
        else:
            summary_table = "<p>没有可用的节点信息</p>"
        
        # 准备节点详细信息
        node_details = self._prepare_node_details(nodes)
        
        # 生成HTML内容
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.cluster_name} - 节点信息报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 10px; padding: 0; }}
        h1, h2, h3 {{ color: #333; margin: 5px 0; }}
        .header {{ margin-bottom: 10px; }}
        .summary {{ margin-bottom: 15px; }}
        .node-details {{ margin-bottom: 20px; }}
        .node-card {{ border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin-bottom: 10px; }}
        .node-card h3 {{ margin-top: 0; cursor: pointer; color: #0066cc; }}
        .node-card h3:hover {{ text-decoration: underline; }}
        .node-info {{ display: flex; flex-wrap: wrap; }}
        .node-info-item {{ flex: 1; min-width: 200px; margin-bottom: 5px; }}
        .usage-bar {{ background-color: #f0f0f0; height: 15px; border-radius: 7px; margin-top: 3px; }}
        .usage-fill {{ height: 100%; border-radius: 7px; }}
        .usage-low {{ background-color: #4CAF50; }}
        .usage-medium {{ background-color: #FFC107; }}
        .usage-high {{ background-color: #F44336; }}
        .footer {{ margin-top: 15px; font-size: 0.8em; color: #666; }}
        .hidden {{ display: none; }}
        .node-details-container {{ margin-top: 10px; border-top: 1px solid #eee; padding-top: 10px; }}
        .pod-list {{ margin-top: 10px; }}
        .pod-item {{ border: 1px solid #eee; border-radius: 3px; padding: 5px; margin-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ padding: 4px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
    </style>
    <script>
        function toggleNodeDetails(nodeName) {
            const detailsContainer = document.getElementById('details-' + nodeName);
            const nodeHeader = document.getElementById('header-' + nodeName);
            if (detailsContainer.classList.contains('hidden')) {
                detailsContainer.classList.remove('hidden');
                if (nodeHeader) nodeHeader.classList.add('expanded');
            } else {
                detailsContainer.classList.add('hidden');
                if (nodeHeader) nodeHeader.classList.remove('expanded');
            }
        }
    </script>
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
        
        # 检查节点列表是否为空
        if not nodes:
            return summary  # 返回空列表
            
        for node in nodes:
            summary.append({
                '节点名称': node['name'],
                '实例类型': node['instance_type'],
                '状态': node['status'],
                'CPU容量': node['capacity']['cpu'],
                'CPU使用率': f"{node['usage']['cpu']['percentage']}%",
                '内存容量': node['capacity']['memory'],
                '内存使用率': f"{node['usage']['memory']['percentage']}%",
                'Pod数量': f"{node['usage']['pods']['used']}/{node['usage']['pods']['capacity']}",
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
        
        # 检查节点列表是否为空
        if not nodes:
            return "<p>没有可用的节点详细信息</p>"
            
        for node in nodes:
            # 确定使用率颜色类
            cpu_class = self._get_usage_class(node['usage']['cpu']['percentage'])
            memory_class = self._get_usage_class(node['usage']['memory']['percentage'])
            pods_class = self._get_usage_class(node['usage']['pods']['percentage'])
            
            # 生成节点卡片HTML，添加点击事件和隐藏的详细信息区域
            node_name_safe = node['name'].replace('.', '-').replace(':', '-')
            
            # 生成节点卡片HTML
            details_html += f"""
            <div class="node-card">
                <h3 id="header-{node_name_safe}" onclick="toggleNodeDetails('{node_name_safe}')">{node['name']}</h3>
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
                        <p><strong>Pod使用率:</strong> {node['usage']['pods']['used']}/{node['usage']['pods']['capacity']} ({node['usage']['pods']['percentage']}%)</p>
                        <div class="usage-bar">
                            <div class="usage-fill {pods_class}" style="width: {min(node['usage']['pods']['percentage'], 100)}%"></div>
                        </div>
                    </div>
                </div>
                
                <!-- 隐藏的详细信息区域 -->
                <div id="details-{node_name_safe}" class="node-details-container hidden">
                    <h4>节点详细信息</h4>
                    <table>
                        <tr>
                            <th>属性</th>
                            <th>值</th>
                        </tr>
                        <tr>
                            <td>名称</td>
                            <td>{node['name']}</td>
                        </tr>
                        <tr>
                            <td>实例类型</td>
                            <td>{node['instance_type']}</td>
                        </tr>
                        <tr>
                            <td>状态</td>
                            <td>{node['status']}</td>
                        </tr>
                        <tr>
                            <td>创建时间</td>
                            <td>{node['creation_timestamp']}</td>
                        </tr>
                        <tr>
                            <td>CPU容量</td>
                            <td>{node['capacity']['cpu']}</td>
                        </tr>
                        <tr>
                            <td>内存容量</td>
                            <td>{node['capacity']['memory']}</td>
                        </tr>
                        <tr>
                            <td>Pod容量</td>
                            <td>{node['capacity']['pods']}</td>
                        </tr>
                        <tr>
                            <td>可分配CPU</td>
                            <td>{node['allocatable']['cpu']}</td>
                        </tr>
                        <tr>
                            <td>可分配内存</td>
                            <td>{node['allocatable']['memory']}</td>
                        </tr>
                        <tr>
                            <td>可分配Pod数</td>
                            <td>{node['allocatable']['pods']}</td>
                        </tr>
                    </table>
                    
                    <h4>节点地址</h4>
                    <table>
                        <tr>
                            <th>类型</th>
                            <th>地址</th>
                        </tr>
                        {self._format_addresses(node['addresses'])}
                    </table>
                    
                    <h4>节点条件</h4>
                    <table>
                        <tr>
                            <th>类型</th>
                            <th>状态</th>
                            <th>原因</th>
                            <th>最后变更时间</th>
                        </tr>
                        {self._format_conditions(node['conditions'])}
                    </table>
                    
                    {self._format_taints(node['taints'])}
                    
                    <h4>节点标签</h4>
                    <table>
                        <tr>
                            <th>键</th>
                            <th>值</th>
                        </tr>
                        {self._format_labels(node['labels'])}
                    </table>
                    
                    <h4>Pod列表</h4>
                    <div id="pods-{node_name_safe}" class="pod-list">
                        加载中...
                    </div>
                    <script>
                        document.addEventListener('DOMContentLoaded', function() {{
                            document.getElementById('pods-{node_name_safe}').innerHTML = `{self._get_node_pods_html(node['name'])}`;
                        }});
                    </script>
                </div>
            </div>
            """
        
        return details_html
        
    def _format_addresses(self, addresses: Dict[str, str]) -> str:
        """
        格式化节点地址信息为HTML表格行
        """
        if not addresses:
            return "<tr><td colspan='2'>无地址信息</td></tr>"
            
        html = ""
        for addr_type, addr in addresses.items():
            html += f"<tr><td>{addr_type}</td><td>{addr}</td></tr>"
        return html
        
    def _format_conditions(self, conditions: List[Dict[str, str]]) -> str:
        """
        格式化节点条件信息为HTML表格行
        """
        if not conditions:
            return "<tr><td colspan='4'>无条件信息</td></tr>"
            
        html = ""
        for condition in conditions:
            html += f"<tr><td>{condition['type']}</td><td>{condition['status']}</td><td>{condition['reason']}</td><td>{condition['last_transition_time']}</td></tr>"
        return html
        
    def _format_taints(self, taints: List[Dict[str, str]]) -> str:
        """
        格式化节点污点信息为HTML表格
        """
        if not taints:
            return ""
            
        html = "<h4>节点污点</h4><table><tr><th>键</th><th>值</th><th>效果</th></tr>"
        for taint in taints:
            html += f"<tr><td>{taint['key']}</td><td>{taint['value']}</td><td>{taint['effect']}</td></tr>"
        html += "</table>"
        return html
        
    def _format_labels(self, labels: Dict[str, str]) -> str:
        """
        格式化节点标签信息为HTML表格行
        """
        if not labels:
            return "<tr><td colspan='2'>无标签信息</td></tr>"
            
        html = ""
        for key, value in labels.items():
            html += f"<tr><td>{key}</td><td>{value}</td></tr>"
        return html
        
    def _get_node_pods_html(self, node_name: str) -> str:
        """
        获取节点上的Pod信息并格式化为HTML
        """
        try:
            from eks_info.k8s_client import K8sClient
            k8s_client = K8sClient()
            pods = k8s_client.get_node_pods(node_name)
            
            if not pods:
                return "<p>该节点上没有运行的Pod</p>"
                
            html = ""
            for pod in pods:
                html += f"""
                <div class="pod-item">
                    <p><strong>名称:</strong> {pod['name']}</p>
                    <p><strong>命名空间:</strong> {pod['namespace']}</p>
                    <p><strong>状态:</strong> {pod['status']}</p>
                    <p><strong>创建时间:</strong> {pod['creation_timestamp']}</p>
                    <p><strong>容器数:</strong> {pod['containers']}</p>
                    <details>
                        <summary>资源请求</summary>
                        <table>
                            <tr>
                                <th>容器</th>
                                <th>CPU</th>
                                <th>内存</th>
                            </tr>
                            {self._format_pod_resources(pod['resource_requests'])}
                        </table>
                    </details>
                </div>
                """
            return html.replace('"', '\\"')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取节点Pod信息失败: {str(e)}")
            return f"<p>获取Pod信息失败: {str(e)}</p>"
            
    def _format_pod_resources(self, resources: Dict[str, Dict[str, str]]) -> str:
        """
        格式化Pod资源请求信息为HTML表格行
        """
        if not resources:
            return "<tr><td colspan='3'>无资源请求信息</td></tr>"
            
        html = ""
        for container, resource in resources.items():
            html += f"<tr><td>{container}</td><td>{resource.get('cpu', '0')}</td><td>{resource.get('memory', '0')}</td></tr>"
        return html
        
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