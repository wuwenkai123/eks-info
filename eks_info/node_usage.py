# -*- coding: utf-8 -*-
"""
节点使用率计算模块

该模块提供计算Kubernetes节点资源使用率的功能。
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class NodeUsageCalculator:
    """节点使用率计算器类，用于计算节点的CPU和内存使用率"""

    def __init__(self, k8s_client):
        """
        初始化节点使用率计算器

        Args:
            k8s_client: Kubernetes客户端实例
        """
        self.k8s_client = k8s_client
        logger.debug("初始化节点使用率计算器")

    def calculate_node_usage(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        计算节点的资源使用率

        Args:
            nodes: 节点信息列表

        Returns:
            包含使用率信息的节点列表
        """
        try:
            # 获取节点上运行的Pod信息
            pods = self.k8s_client.get_pods()
            
            # 按节点名称组织Pod
            pods_by_node = {}
            for pod in pods:
                node_name = pod.get('node_name')
                if node_name:
                    if node_name not in pods_by_node:
                        pods_by_node[node_name] = []
                    pods_by_node[node_name].append(pod)
            
            # 计算每个节点的资源使用率
            for node in nodes:
                node_name = node['name']
                node_pods = pods_by_node.get(node_name, [])
                
                # 计算CPU使用率
                cpu_capacity = self._parse_cpu(node['capacity']['cpu'])
                cpu_usage = sum(self._calculate_pod_cpu_usage(pod) for pod in node_pods)
                cpu_usage_percentage = (cpu_usage / cpu_capacity * 100) if cpu_capacity > 0 else 0
                
                # 计算内存使用率
                memory_capacity = self._parse_memory(node['capacity']['memory'])
                memory_usage = sum(self._calculate_pod_memory_usage(pod) for pod in node_pods)
                memory_usage_percentage = (memory_usage / memory_capacity * 100) if memory_capacity > 0 else 0
                
                # 添加使用率信息到节点
                node['usage'] = {
                    'cpu': {
                        'capacity': cpu_capacity,
                        'used': cpu_usage,
                        'percentage': round(cpu_usage_percentage, 2)
                    },
                    'memory': {
                        'capacity': memory_capacity,
                        'used': memory_usage,
                        'percentage': round(memory_usage_percentage, 2)
                    },
                    'pods': {
                        'capacity': int(node['capacity']['pods']),
                        'used': len(node_pods),
                        'percentage': round(len(node_pods) / int(node['capacity']['pods']) * 100, 2) if node['capacity']['pods'] != 'Unknown' else 0
                    }
                }
            
            logger.info(f"已计算 {len(nodes)} 个节点的资源使用率")
            return nodes
        except Exception as e:
            logger.error(f"计算节点使用率失败: {str(e)}")
            # 如果计算失败，返回原始节点列表
            return nodes

    def _parse_cpu(self, cpu_str: str) -> float:
        """
        解析CPU字符串为核心数

        Args:
            cpu_str: CPU字符串，如'2'或'200m'

        Returns:
            CPU核心数
        """
        try:
            if cpu_str == 'Unknown':
                return 0
            
            if cpu_str.endswith('m'):
                return float(cpu_str[:-1]) / 1000
            else:
                return float(cpu_str)
        except (ValueError, TypeError):
            logger.warning(f"无法解析CPU值: {cpu_str}，将使用0")
            return 0

    def _parse_memory(self, memory_str: str) -> int:
        """
        解析内存字符串为字节数

        Args:
            memory_str: 内存字符串，如'2Gi'或'200Mi'

        Returns:
            内存字节数
        """
        try:
            if memory_str == 'Unknown':
                return 0
            
            if memory_str.endswith('Ki'):
                return int(memory_str[:-2]) * 1024
            elif memory_str.endswith('Mi'):
                return int(memory_str[:-2]) * 1024 * 1024
            elif memory_str.endswith('Gi'):
                return int(memory_str[:-2]) * 1024 * 1024 * 1024
            elif memory_str.endswith('Ti'):
                return int(memory_str[:-2]) * 1024 * 1024 * 1024 * 1024
            elif memory_str.endswith('Pi'):
                return int(memory_str[:-2]) * 1024 * 1024 * 1024 * 1024 * 1024
            elif memory_str.endswith('Ei'):
                return int(memory_str[:-2]) * 1024 * 1024 * 1024 * 1024 * 1024 * 1024
            elif memory_str.endswith('k'):
                return int(memory_str[:-1]) * 1000
            elif memory_str.endswith('M'):
                return int(memory_str[:-1]) * 1000 * 1000
            elif memory_str.endswith('G'):
                return int(memory_str[:-1]) * 1000 * 1000 * 1000
            elif memory_str.endswith('T'):
                return int(memory_str[:-1]) * 1000 * 1000 * 1000 * 1000
            elif memory_str.endswith('P'):
                return int(memory_str[:-1]) * 1000 * 1000 * 1000 * 1000 * 1000
            elif memory_str.endswith('E'):
                return int(memory_str[:-1]) * 1000 * 1000 * 1000 * 1000 * 1000 * 1000
            else:
                return int(memory_str)
        except (ValueError, TypeError):
            logger.warning(f"无法解析内存值: {memory_str}，将使用0")
            return 0

    def _calculate_pod_cpu_usage(self, pod: Dict[str, Any]) -> float:
        """
        计算Pod的CPU使用量

        Args:
            pod: Pod信息字典

        Returns:
            CPU使用量（核心数）
        """
        try:
            containers = pod.get('containers', [])
            return sum(self._parse_cpu(container.get('resources', {}).get('requests', {}).get('cpu', '0')) 
                      for container in containers)
        except Exception as e:
            logger.warning(f"计算Pod CPU使用量失败: {str(e)}")
            return 0

    def _calculate_pod_memory_usage(self, pod: Dict[str, Any]) -> int:
        """
        计算Pod的内存使用量

        Args:
            pod: Pod信息字典

        Returns:
            内存使用量（字节）
        """
        try:
            containers = pod.get('containers', [])
            return sum(self._parse_memory(container.get('resources', {}).get('requests', {}).get('memory', '0')) 
                      for container in containers)
        except Exception as e:
            logger.warning(f"计算Pod内存使用量失败: {str(e)}")
            return 0