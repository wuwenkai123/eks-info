# -*- coding: utf-8 -*-
"""
Kubernetes客户端模块

该模块提供与Kubernetes集群交互的功能，用于获取节点信息。
"""

import logging
import os
from typing import Dict, List, Optional, Any

from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

logger = logging.getLogger(__name__)


class K8sClient:
    """Kubernetes客户端类，用于与Kubernetes API交互"""

    def __init__(self, use_kubeconfig: bool = True, kubeconfig_path: Optional[str] = None):
        """
        初始化Kubernetes客户端

        Args:
            use_kubeconfig: 是否使用kubeconfig文件进行认证
            kubeconfig_path: kubeconfig文件路径，如果为None则使用默认路径
        """
        try:
            if use_kubeconfig:
                if kubeconfig_path and os.path.exists(kubeconfig_path):
                    config.load_kube_config(config_file=kubeconfig_path)
                else:
                    config.load_kube_config()
            else:
                # 在集群内部运行时使用
                config.load_incluster_config()

            self.core_v1_api = client.CoreV1Api()
            logger.info("成功初始化Kubernetes客户端")
        except Exception as e:
            logger.error(f"初始化Kubernetes客户端失败: {str(e)}")
            raise

    def get_nodes(self) -> List[Dict[str, Any]]:
        """
        获取集群中所有节点信息

        Returns:
            包含节点信息的字典列表
        """
        try:
            nodes = self.core_v1_api.list_node().items
            node_list = []

            for node in nodes:
                node_info = {
                    'name': node.metadata.name,
                    'instance_type': node.metadata.labels.get('node.kubernetes.io/instance-type', 'Unknown'),
                    'creation_timestamp': node.metadata.creation_timestamp,
                    'status': self._get_node_status(node),
                    'capacity': {
                        'cpu': node.status.capacity.get('cpu', 'Unknown'),
                        'memory': node.status.capacity.get('memory', 'Unknown'),
                        'pods': node.status.capacity.get('pods', 'Unknown')
                    },
                    'allocatable': {
                        'cpu': node.status.allocatable.get('cpu', 'Unknown'),
                        'memory': node.status.allocatable.get('memory', 'Unknown'),
                        'pods': node.status.allocatable.get('pods', 'Unknown')
                    },
                    'labels': node.metadata.labels,
                    'taints': self._get_node_taints(node),
                    'conditions': self._get_node_conditions(node),
                    'addresses': self._get_node_addresses(node)
                }
                node_list.append(node_info)

            logger.info(f"成功获取到 {len(node_list)} 个节点信息")
            return node_list
        except ApiException as e:
            logger.error(f"获取节点信息失败: {str(e)}")
            raise

    def _get_node_status(self, node) -> str:
        """
        获取节点状态

        Args:
            node: Kubernetes节点对象

        Returns:
            节点状态字符串
        """
        for condition in node.status.conditions:
            if condition.type == 'Ready':
                return 'Ready' if condition.status == 'True' else 'NotReady'
        return 'Unknown'

    def _get_node_conditions(self, node) -> List[Dict[str, str]]:
        """
        获取节点条件信息

        Args:
            node: Kubernetes节点对象

        Returns:
            节点条件信息列表
        """
        conditions = []
        for condition in node.status.conditions:
            conditions.append({
                'type': condition.type,
                'status': condition.status,
                'reason': condition.reason,
                'message': condition.message,
                'last_transition_time': condition.last_transition_time
            })
        return conditions

    def _get_node_taints(self, node) -> List[Dict[str, str]]:
        """
        获取节点污点信息

        Args:
            node: Kubernetes节点对象

        Returns:
            节点污点信息列表
        """
        taints = []
        if node.spec.taints:
            for taint in node.spec.taints:
                taints.append({
                    'key': taint.key,
                    'value': taint.value,
                    'effect': taint.effect
                })
        return taints

    def _get_node_addresses(self, node) -> Dict[str, str]:
        """
        获取节点地址信息

        Args:
            node: Kubernetes节点对象

        Returns:
            节点地址信息字典
        """
        addresses = {}
        for address in node.status.addresses:
            addresses[address.type] = address.address
        return addresses

    def get_node_pods(self, node_name: str) -> List[Dict[str, Any]]:
        """
        获取指定节点上运行的所有Pod

        Args:
            node_name: 节点名称

        Returns:
            Pod信息列表
        """
        try:
            field_selector = f'spec.nodeName={node_name}'
            pods = self.core_v1_api.list_pod_for_all_namespaces(field_selector=field_selector).items
            pod_list = []

            for pod in pods:
                pod_info = {
                    'name': pod.metadata.name,
                    'namespace': pod.metadata.namespace,
                    'status': pod.status.phase,
                    'creation_timestamp': pod.metadata.creation_timestamp,
                    'containers': len(pod.spec.containers),
                    'resource_requests': self._get_pod_resource_requests(pod)
                }
                pod_list.append(pod_info)

            logger.info(f"成功获取到节点 {node_name} 上的 {len(pod_list)} 个Pod")
            return pod_list
        except ApiException as e:
            logger.error(f"获取节点 {node_name} 上的Pod信息失败: {str(e)}")
            raise

    def _get_pod_resource_requests(self, pod) -> Dict[str, Dict[str, str]]:
        """
        获取Pod的资源请求

        Args:
            pod: Kubernetes Pod对象

        Returns:
            Pod资源请求信息
        """
        resources = {}
        for container in pod.spec.containers:
            if container.resources and container.resources.requests:
                resources[container.name] = {
                    'cpu': container.resources.requests.get('cpu', '0'),
                    'memory': container.resources.requests.get('memory', '0')
                }
            else:
                resources[container.name] = {
                    'cpu': '0',
                    'memory': '0'
                }
        return resources
        
    def get_pods(self) -> List[Dict[str, Any]]:
        """
        获取集群中所有Pod信息

        Returns:
            包含Pod信息的字典列表
        """
        try:
            pods = self.core_v1_api.list_pod_for_all_namespaces().items
            pod_list = []

            for pod in pods:
                containers = []
                for container in pod.spec.containers:
                    container_info = {
                        'name': container.name,
                        'image': container.image,
                        'resources': {
                            'requests': {}
                        }
                    }
                    
                    # 获取资源请求
                    if container.resources and container.resources.requests:
                        container_info['resources']['requests'] = {
                            'cpu': container.resources.requests.get('cpu', '0'),
                            'memory': container.resources.requests.get('memory', '0')
                        }
                    
                    containers.append(container_info)
                
                pod_info = {
                    'name': pod.metadata.name,
                    'namespace': pod.metadata.namespace,
                    'node_name': pod.spec.node_name,
                    'status': pod.status.phase,
                    'creation_timestamp': pod.metadata.creation_timestamp,
                    'containers': containers
                }
                pod_list.append(pod_info)

            logger.info(f"成功获取到 {len(pod_list)} 个Pod信息")
            return pod_list
        except ApiException as e:
            logger.error(f"获取Pod信息失败: {str(e)}")
            raise
        resources = {}
        for container in pod.spec.containers:
            if container.resources and container.resources.requests:
                resources[container.name] = {
                    'cpu': container.resources.requests.get('cpu', '0'),
                    'memory': container.resources.requests.get('memory', '0')
                }
            else:
                resources[container.name] = {'cpu': '0', 'memory': '0'}
        return resources