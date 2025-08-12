# LargeRAG工具安装指南

## 概述

LargeRAG是基于LlamaIndex的大规模文献RAG系统，用于处理和检索大量科学文献。

## 依赖包安装

### 1. 核心依赖

已安装的核心依赖包包括：

- **LlamaIndex核心包**: `llama-index`, `llama-index-core`
- **嵌入模型支持**: `llama-index-embeddings-openai`, `openai`
- **LLM支持**: `llama-index-llms-openai`
- **向量数据库**: `llama-index-vector-stores-chroma`, `chromadb`
- **文档处理**: `llama-index-readers-file`
- **配置管理**: `pyyaml`, `python-dotenv`
- **数据处理**: `pandas`, `numpy`
- **日志**: `structlog`

### 2. 安装验证

运行以下命令验证依赖包安装：

```bash
python src/tools/largerag/verify_dependencies.py
```

## 配置设置

### 1. 环境变量配置

复制示例环境变量文件：

```bash
cp src/tools/largerag/.env.example src/tools/largerag/.env
```

编辑 `.env` 文件，设置您的OpenAI API密钥：

```env
OPENAI_API_KEY=your_actual_api_key_here
```

### 2. 配置文件

主配置文件位于 `src/tools/largerag/src/config/settings.yaml`，包含：

- **文档处理配置**: 分块大小、重叠等
- **嵌入模型配置**: OpenAI嵌入模型设置
- **向量存储配置**: Chroma数据库设置
- **检索配置**: 检索参数
- **LLM配置**: GPT模型设置
- **系统配置**: 目录路径、日志等

### 3. 配置验证

运行以下命令验证配置：

```bash
python src/tools/largerag/verify_config.py
```

## 功能测试

运行基本功能测试：

```bash
python src/tools/largerag/test_basic_functionality.py
```

此测试将验证：
- LlamaIndex核心功能导入
- Chroma向量数据库基本操作
- 文档处理功能
- OpenAI配置

## 目录结构

安装完成后，将创建以下目录结构：

```
data/largerag/
├── indexes/          # Chroma向量数据库持久化目录
├── cache/           # 缓存目录
└── temp/            # 临时文件目录

logs/
├── largerag.log     # 主日志文件
└── largerag_metrics.json  # 性能指标文件
```

## 使用说明

### 1. 基本导入

```python
from largerag import LargeRAG

# 创建LargeRAG实例
rag = LargeRAG()
```

### 2. 配置加载

```python
from largerag.src.config.settings import Settings

# 加载配置
settings = Settings()
```

## 故障排除

### 常见问题

1. **OpenAI API密钥未设置**
   - 确保在 `.env` 文件中设置了 `OPENAI_API_KEY`
   - 或通过环境变量设置

2. **Chroma数据库权限问题**
   - 确保对数据目录有读写权限
   - 检查目录路径是否正确

3. **依赖包版本冲突**
   - 查看安装输出中的警告信息
   - 考虑使用虚拟环境隔离依赖

### 日志查看

查看详细日志：

```bash
tail -f logs/largerag.log
```

## 下一步

依赖包安装完成后，您可以：

1. 开始实现核心功能模块
2. 配置文档处理管道
3. 设置向量索引管理
4. 实现查询引擎

更多详细信息请参考项目文档。