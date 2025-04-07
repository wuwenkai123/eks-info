# EKS信息收集工具

[![版本](https://img.shields.io/badge/版本-0.1.0-blue.svg)](https://github.com/your-username/eks-info)
[![Python](https://img.shields.io/badge/Python-3.6+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 项目简介

EKS信息收集工具是一个用于收集和分析Amazon EKS（Elastic Kubernetes Service）集群信息的Python工具。它可以帮助您获取集群节点的详细信息，计算资源使用率，并生成HTML格式的报告。报告可以保存在本地，也可以上传到AWS S3存储桶中。

## 功能特点

- 自动收集EKS集群节点信息
- 计算节点CPU和内存使用率
- 生成美观的HTML格式报告
- 支持将报告上传到S3存储桶
- 灵活的配置选项
- 详细的日志记录

## 安装步骤

### 前提条件

- Python 3.6+
- 有效的kubeconfig配置（用于访问EKS集群）
- （可选）AWS凭证（用于S3上传功能）

### 安装方法

1. 克隆仓库：

```bash
git clone https://github.com/your-username/eks-info.git
cd eks-info
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 配置说明

### 配置文件

默认配置文件为`config.yaml`，您可以根据需要修改配置。配置文件示例：

```yaml
# Kubernetes配置
kubernetes:
  # 使用当前上下文的kubeconfig文件
  use_kubeconfig: true
  # kubeconfig文件路径，如果为空则使用默认路径 (~/.kube/config)
  kubeconfig_path: ""

# S3上传配置
s3:
  # 是否启用S3上传功能
  enabled: false
  # S3存储桶名称
  bucket_name: "eks-info-bucket"
  # S3对象键前缀
  key_prefix: "reports/"
  # AWS区域
  region: "ap-northeast-1"
  # AWS凭证配置
  # 如果为空，将使用默认凭证提供链
  aws_access_key_id: ""
  aws_secret_access_key: ""

# 报告配置
report:
  # 报告输出目录
  output_dir: "./reports"
  # 报告文件名格式 (支持日期格式化)
  filename_format: "eks-info-report-%Y-%m-%d.html"
```

### AWS凭证配置

如果您需要使用S3上传功能，可以通过以下方式配置AWS凭证：

1. 在配置文件中直接指定`aws_access_key_id`和`aws_secret_access_key`
2. 使用AWS CLI配置（`aws configure`）
3. 使用环境变量（`AWS_ACCESS_KEY_ID`和`AWS_SECRET_ACCESS_KEY`）
4. 使用IAM角色（如果在EC2或EKS上运行）

## 使用方法

### 基本用法

```bash
python -m eks_info.main
```

### 命令行参数

```
用法: main.py [-h] [-c CONFIG] [-o OUTPUT_DIR] [--s3-upload] [--no-s3-upload]
              [--cluster-name CLUSTER_NAME] [-v] [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
              [--log-file LOG_FILE]

选项:
  -h, --help            显示帮助信息并退出
  -c CONFIG, --config CONFIG
                        配置文件路径 (默认: config.yaml)
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        报告输出目录 (覆盖配置文件中的设置)
  --s3-upload           启用S3上传 (覆盖配置文件中的设置)
  --no-s3-upload        禁用S3上传 (覆盖配置文件中的设置)
  --cluster-name CLUSTER_NAME
                        集群名称 (默认: EKS集群)
  -v, --version         显示程序版本并退出
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        日志级别 (默认: INFO)
  --log-file LOG_FILE   日志文件路径
```

### 示例

1. 使用自定义配置文件：

```bash
python -m eks_info.main -c my-config.yaml
```

2. 指定输出目录：

```bash
python -m eks_info.main -o /path/to/reports
```

3. 启用S3上传：

```bash
python -m eks_info.main --s3-upload
```

4. 指定集群名称：

```bash
python -m eks_info.main --cluster-name "生产集群"
```

5. 设置日志级别和日志文件：

```bash
python -m eks_info.main --log-level DEBUG --log-file eks-info.log
```

## 报告示例

生成的HTML报告包含以下信息：

- 集群名称和报告生成时间
- 节点摘要（节点数量、总CPU和内存）
- 节点详细信息（包括名称、实例类型、CPU和内存使用率等）
- 节点标签和污点信息

## 贡献指南

欢迎贡献代码、报告问题或提出改进建议！请遵循以下步骤：

1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详情请参阅[LICENSE](LICENSE)文件。