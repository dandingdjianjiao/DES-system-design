# LargeRAG工具详细文档

基于LlamaIndex的大规模文献RAG系统，专门设计用于处理大规模科学文献集合（10,000+篇论文）。

## 概述

LargeRAG是DES-system-design项目的核心组件之一，提供：

- **大规模文档处理**：高效索引和检索海量文献
- **配置驱动**：灵活的YAML配置管理
- **标准化接口**：与项目其他工具保持一致的API设计
- **持久化存储**：避免重复计算，支持增量更新

## 项目结构

```
src/tools/largerag/
├── src/                          # 核心源代码
│   ├── config/                   # 配置管理
│   │   ├── settings.py          # 配置类定义
│   │   └── settings.yaml        # 默认配置文件
│   ├── core/                     # 核心功能模块（待实现）
│   ├── models/                   # 数据模型（待实现）
│   ├── utils/                    # 工具函数
│   │   ├── exceptions.py        # 异常定义
│   │   └── logging.py           # 日志工具
│   └── largerag.py              # 主接口类
├── data/                         # 数据存储目录
├── tests/                        # 测试文件
│   ├── unit/                    # 单元测试
│   └── integration/             # 集成测试
├── docs/                         # 详细文档
└── __init__.py                  # 包初始化
```

## 快速开始

### 安装依赖

```bash
cd src/tools/largerag
pip install -r requirements.txt
```

### 配置设置

复制环境变量模板：
```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的API密钥。

### 基本使用

```python
from src.tools.largerag import LargeRAG

# 初始化系统
rag = LargeRAG()

# 准备JSON数据
json_data = [
    {
        "text": "深共熔溶剂（DES）是一种新型绿色溶剂...",
        "type": "text",
        "title": "DES介绍"
    }
]

# 索引文档（当前为占位符实现）
rag.index_documents_from_json(json_data)

# 执行查询（当前为占位符实现）
response = rag.query("什么是深共熔溶剂？")
print(response)
```

### 自定义配置

```python
from src.tools.largerag.src.config.settings import LargeRAGSettings

# 创建自定义配置
settings = LargeRAGSettings()
settings.document_processing.chunk_size = 2000
settings.retrieval.top_k = 20

# 使用自定义配置初始化
rag = LargeRAG(config=settings)
```

### 从配置文件加载

```python
# 从YAML文件加载配置
rag = LargeRAG(config_path="path/to/your/config.yaml")
```

## 配置说明

主要配置项包括：

- **document_processing**: 文档处理参数（分块大小、重叠等）
- **embedding**: 嵌入模型配置（模型名称、API密钥等）
- **vector_store**: 向量存储配置（类型、持久化目录等）
- **retrieval**: 检索参数（top_k、相似性阈值等）
- **llm**: LLM配置（模型、温度、最大token等）
- **logging**: 日志配置（级别、文件路径等）
- **performance**: 性能配置（缓存、并行处理等）
- **system**: 系统配置（数据目录、指标等）

详细配置选项请参考 `src/config/settings.yaml`。

## 环境要求

- Python 3.8+
- 设置环境变量 `OPENAI_API_KEY`
- 设置环境变量 `PROJECT_ROOT`（可选，用于路径解析）

## 多LLM服务支持

LargeRAG支持多种OpenAI兼容的LLM服务：

### 支持的服务
- **OpenAI官方**: 默认支持
- **通义千问 (Qwen)**: 完全兼容
- **智谱AI (GLM)**: 完全兼容  
- **月之暗面 (Kimi)**: 支持对话模型
- **本地部署**: 支持vLLM、Ollama等

### 快速配置

通过环境变量切换服务：

```bash
# 使用通义千问
export OPENAI_API_KEY="your_dashscope_api_key"
export OPENAI_API_BASE="https://dashscope.aliyuncs.com/compatible-mode/v1"

# 使用智谱AI
export OPENAI_API_KEY="your_zhipuai_api_key"
export OPENAI_API_BASE="https://open.bigmodel.cn/api/paas/v4"
```

详细配置指南请参考 [替代LLM配置](ALTERNATIVE_LLMS.md)。

## 测试和验证

### 验证工具

LargeRAG提供了完整的验证工具链：

```bash
# 验证依赖包安装状态
python scripts/verify_dependencies.py

# 验证配置文件和环境变量
python scripts/verify_config.py

# 测试基本功能
python -m pytest tests/integration/test_basic_functionality.py -v

# 测试多LLM服务兼容性
python -m pytest tests/integration/test_alternative_llms.py -v
```

### 单元测试

```bash
python -m pytest src/tools/largerag/tests/unit/ -v
```

### 集成测试

```bash
python -m pytest src/tools/largerag/tests/integration/ -v
```

### 运行所有测试

```bash
python -m pytest src/tools/largerag/tests/ -v
```

## 开发状态

当前版本（v0.1.0）包含：

✅ **已完成**：
- 项目基础结构和目录组织
- YAML配置管理系统
- 主接口类框架
- 异常处理和日志系统
- 基础测试套件

🚧 **待实现**（后续任务）：
- 文档处理器（JSON到LlamaIndex Document转换）
- LlamaIndex集成（向量索引、查询引擎）
- 实际的索引和查询功能
- 性能优化和缓存机制

## 与其他工具的集成

LargeRAG设计为与项目其他工具协同工作：

- **CoreRAG**: 提供本体驱动的精确检索，LargeRAG提供广泛的文献覆盖
- **Data Agent**: 文献结果与实验数据交叉验证
- **路由Agent**: 统一调度和结果融合

## 相关文档

- [安装指南](INSTALLATION.md)
- [LLM集成指南](LLM_INTEGRATION_GUIDE.md)
- [替代LLM配置](ALTERNATIVE_LLMS.md)

## 许可证

本项目是DES-system-design项目的一部分。