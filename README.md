# DES-system-design

基于AI的低共熔溶剂（Deep Eutectic Solvent, DES）配方预测系统，旨在预测能在低温条件下最大化溶解指定材料的DES配方。

## 系统概述

DES-system-design 采用多Agent协作架构，结合本体驱动的知识表示、大规模文献检索和实验数据分析，为科学研究提供智能化的配方设计支持。

### 核心理念

- **科学发现导向**：不是简单的黑盒优化，而是激发LLM的参数化知识与RAG知识共同进行科学设计
- **推理驱动**：重点优化Agent的设计行为流程和推理质量，而非单纯的配方-溶解度映射
- **知识整合**：结合理论原理、文献事实和实验数据进行综合分析

## 系统架构

### 工具组件（Tools）

#### 1. CoreRAG - 本体驱动RAG系统 ✅
- **状态**：已完成核心功能
- **功能**：基于OWL本体的精确知识检索
- **特点**：
  - 处理多个化学本体文件（OWL格式）
  - Agent团队架构（critic、dreamer、query团队）
  - 本体构建和工作流管理
  - 配置驱动的设置管理

#### 2. LargeRAG - 大规模文献RAG系统 🚧
- **状态**：开发中（v0.1.0）
- **功能**：基于LlamaIndex的海量文献检索
- **特点**：
  - 支持10,000+篇文献的向量数据库
  - 集成Chroma向量存储和OpenAI嵌入模型
  - **多LLM服务兼容**：支持通义千问、智谱AI、Kimi等OpenAI兼容服务
  - **智能LLM类选择**：自动选择最优LLM和嵌入模型类，确保最佳兼容性和性能
  - 完整的包管理和安装配置（setup.py）
  - 配置驱动的系统管理（YAML配置）
  - 标准化的测试框架（单元测试+集成测试）
  - 依赖验证工具（verify_dependencies.py）
  - 基本功能测试工具（test_basic_functionality.py）
  - 配置验证工具（verify_config.py）
  - 多LLM兼容性测试（test_alternative_llms.py）
  - 与项目其他工具的标准化接口

#### 3. Data Agent - 实验数据处理工具 📋
- **状态**：待开发
- **功能**：数值型实验数据处理
- **特点**：
  - Excel/CSV数据操作
  - 配方-温度-溶解比例数据查询
  - MCP工具集成

### 核心Agent

#### 路由Agent - 高层调度器 📋
- **状态**：待开发
- **功能**：任务分析、工具调度、推理分析、报告生成
- **特点**：
  - 智能任务分解和工具选择
  - 多源信息融合和推理
  - 科学报告自动生成

## 项目结构

```
DES-system-design/
├── data/                          # 数据存储
├── notebooks/                     # Jupyter notebooks原型开发
├── reports/                       # Agent生成的实验提案报告
├── src/                          # 源代码
│   ├── agent/                    # Agent核心逻辑（待开发）
│   └── tools/                    # 可调用工具集
│       ├── corerag/             # 核心RAG工具（✅ 已完成）
│       ├── largerag/            # 大规模RAG工具（🚧 开发中）
│       │   ├── src/             # 核心源代码
│       │   ├── tests/           # 测试文件
│       │   ├── data/            # 数据存储
│       │   ├── requirements.txt # 依赖配置
│       │   ├── setup.py         # 安装配置
│       │   ├── verify_dependencies.py # 依赖验证工具
│       │   ├── verify_config.py # 配置验证工具
│       │   ├── test_basic_functionality.py # 基本功能测试
│       │   ├── test_alternative_llms.py # 多LLM兼容性测试
│       │   ├── ALTERNATIVE_LLMS.md # LLM服务配置指南
│       │   └── .env.example     # 环境变量配置示例
│       └── experimental_data/   # 实验数据处理工具（📋 待开发）
├── .kiro/                        # Kiro IDE配置
│   ├── specs/                   # 开发规格说明
│   │   └── largerag-pipeline/   # LargeRAG开发规格
│   └── steering/                # 项目指导文档
└── README.md                     # 项目文档
```

## 技术栈

### 核心技术
- **Python**: 主要开发语言
- **LlamaIndex**: 大规模文献RAG管道
- **OWL本体**: 知识表示和推理
- **向量数据库**: 文献嵌入存储和检索
- **OpenAI API**: 外部LLM服务
- **Pandas**: 数据处理和分析

### 开发工具
- **Java**: OWL本体处理（JDK 23）
- **Agent框架**: 多Agent协作系统
- **配置管理**: YAML配置文件驱动
- **依赖验证**: 自动化依赖包验证工具
- **包管理**: setuptools和pip集成

## 快速开始

### 环境设置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 设置环境变量
export OPENAI_API_KEY="your-api-key"
export PROJECT_ROOT="/path/to/project"
```

### LLM服务配置

LargeRAG工具支持多种LLM服务，通过修改环境变量即可切换：

#### 使用OpenAI官方服务
```bash
# .env文件
OPENAI_API_KEY=your_openai_api_key
# OPENAI_API_BASE 不设置，使用默认值
```

#### 使用通义千问 (Qwen)
```bash
# .env文件
OPENAI_API_KEY=your_dashscope_api_key
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

#### 使用智谱AI (GLM)
```bash
# .env文件
OPENAI_API_KEY=your_zhipuai_api_key
OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4
```

#### 使用月之暗面 (Kimi)
```bash
# .env文件
OPENAI_API_KEY=your_moonshot_api_key
OPENAI_API_BASE=https://api.moonshot.cn/v1
```

**注意**: 不同服务需要在`settings.yaml`中调整模型名称。详细配置请参考 `src/tools/largerag/ALTERNATIVE_LLMS.md`。

### 依赖管理

每个工具都有独立的依赖管理：

```bash
# CoreRAG工具（已完成，依赖较少）
cd src/tools/corerag
# 直接使用，无需额外安装

# LargeRAG工具（开发中）
cd src/tools/largerag

# 验证依赖状态
python verify_dependencies.py

# 安装依赖
pip install -r requirements.txt

# 验证安装结果
python verify_dependencies.py
```

### 使用CoreRAG工具

```python
# CoreRAG工具已精简完成，可直接使用
cd src/tools/corerag/autology_constructor
python test.py
```

### 使用LargeRAG工具

```bash
# 进入LargeRAG工具目录
cd src/tools/largerag

# 验证依赖包安装状态
python verify_dependencies.py

# 安装LargeRAG工具依赖
pip install -r requirements.txt

# 或使用setup.py安装
pip install -e .

# 验证配置文件和环境变量
python verify_config.py

# 测试基本功能
python test_basic_functionality.py

# 测试多LLM服务兼容性
python test_alternative_llms.py
```

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

# 检查系统状态
status = rag.get_system_status()
print(status)
```

## LargeRAG工具详细说明

### 当前实现状态

LargeRAG工具基于LlamaIndex框架，目前已完成基础架构和配置系统：

#### 已实现功能 ✅
- **项目结构**: 完整的Python包结构，包含src、config、data、tests目录
- **配置管理**: 基于YAML的配置系统，支持动态加载和验证
- **主接口类**: LargeRAG类提供统一的API接口
- **依赖管理**: requirements.txt和setup.py完整配置
- **多层测试工具**:
  - `verify_dependencies.py`: 验证所有依赖包安装状态
  - `verify_config.py`: 验证配置文件和环境变量设置
  - `test_basic_functionality.py`: 测试核心组件基本功能
  - `test_alternative_llms.py`: 测试多LLM服务兼容性
- **多LLM服务支持**: 兼容通义千问、智谱AI、Kimi等OpenAI兼容服务
- **日志系统**: 结构化日志记录，支持文件和控制台输出
- **错误处理**: 完善的异常处理和错误信息

#### 测试和验证工具

LargeRAG工具提供了完整的测试和验证工具链：

##### 1. 依赖验证工具 (`verify_dependencies.py`)
验证LlamaIndex生态系统的复杂依赖：
```bash
cd src/tools/largerag
python verify_dependencies.py
```
验证内容：
- LlamaIndex核心包（llama-index, llama-index-core）
- OpenAI集成（嵌入模型和LLM）
- Chroma向量数据库
- 文档处理和配置管理工具
- 数据处理库（pandas, numpy）

##### 2. 配置验证工具 (`verify_config.py`)
验证配置文件和环境变量设置：
```bash
python verify_config.py
```
验证内容：
- YAML配置文件加载
- OpenAI API密钥环境变量
- Chroma向量数据库配置
- 目录结构和权限

##### 3. 基本功能测试 (`test_basic_functionality.py`) ✅
测试核心组件的基本功能：
```bash
python test_basic_functionality.py
```
测试内容：
- **LlamaIndex核心组件导入**: Document, VectorStoreIndex, SimpleNodeParser, OpenAI, ChromaVectorStore等
- **Chroma向量数据库基本操作**: 创建集合、添加文档、执行查询
- **文档处理功能**: Document对象创建、节点解析器功能
- **OpenAI配置验证**: 嵌入模型和LLM实例化（不实际调用API）
- **完全离线测试**: 不依赖外部API，快速验证环境配置
- **详细报告**: 彩色输出、成功率统计、问题诊断

##### 4. 多LLM兼容性测试 (`test_alternative_llms.py`)
测试不同LLM服务的兼容性：
```bash
python test_alternative_llms.py
```
支持的服务：
- **通义千问 (Qwen)**: 完全兼容，支持qwen-turbo、qwen-plus等模型，智能选择DashScope专用类
- **智谱AI (GLM)**: 完全兼容，支持glm-4、glm-3-turbo等模型
- **月之暗面 (Kimi)**: 支持moonshot系列对话模型，嵌入需要其他服务
- **本地部署**: 支持vLLM、Ollama等本地服务

**智能特性**:
- 根据API基础URL自动检测服务类型和推荐模型
- 智能选择LLM类：优先使用专用LLM类（如DashScope），回退到OpenAI兼容模式
- 智能选择嵌入模型类：根据服务类型自动选择合适的嵌入模型类
- 提供针对性的配置示例和注意事项
- 支持混合使用不同服务（如LLM用Qwen，嵌入用OpenAI）
- 实际模型功能测试，验证文本生成能力

#### 占位符实现

当前的`index_documents_from_json`和`query`方法是占位符实现，为后续开发提供接口框架。

## 开发状态

### 已完成组件 ✅
- **CoreRAG工具**: 精简的本体驱动RAG系统
  - 化学本体处理（OWL格式，多个本体文件）
  - Agent团队架构（query团队）
  - 本体构建和工作流管理
  - 配置管理系统

### 开发中组件 🚧
- **LargeRAG工具**: 基于LlamaIndex的大规模文献RAG
  - 项目基础结构和配置系统 ✅
  - YAML配置管理系统 ✅
  - 主接口类框架和占位符实现 ✅
  - LlamaIndex依赖包安装和验证 ✅
  - **完整测试工具链** ✅
    - **依赖验证工具**（verify_dependencies.py）✅ - 自动检测LlamaIndex生态依赖
    - **配置验证工具**（verify_config.py）✅ - 验证YAML配置和环境变量
    - **基本功能测试**（test_basic_functionality.py）✅ - 核心组件离线功能测试
    - **多LLM兼容性测试**（test_alternative_llms.py）✅ - 智能服务检测和实际功能验证
  - 多LLM服务支持（通义千问、智谱AI、Kimi等）✅
    - 智能LLM类选择：优先使用专用类，自动回退兼容模式
    - 实际功能测试：验证模型文本生成能力
  - 文档处理器核心功能 📋
  - 索引管理器 📋
  - 查询引擎 📋

### 待开发组件 📋
- **Data Agent**: Excel/CSV数据处理工具
- **路由Agent**: 高层调度和推理系统
- **工作流编排器**: 整合所有工具的调度器

## 开发阶段规划

### 第一阶段：完善工具箱（当前阶段）
- [x] CoreRAG工具完成
- [🚧] LargeRAG工具开发
- [ ] 实验数据处理工具开发
- [ ] 在notebooks中测试各工具集成

### 第二阶段：构建核心工作流
- [ ] 实现路由Agent
- [ ] 创建工作流编排器
- [ ] 建立工具间的统一接口

### 第三阶段：系统集成与优化
- [ ] 完整的端到端工作流测试
- [ ] 报告生成和人机交互
- [ ] 强化学习集成准备

## 长期规划

- **强化学习优化**: 引入RL框架优化路由Agent的决策行为
- **HITL**: 通过人类专家反馈进行系统改进
- **自举预测模型**: 利用系统产生的高质量实验数据逐步构建预测模型

## 贡献指南

### 代码规范
- **目录**: 小写下划线 (snake_case)
- **Python文件**: 小写下划线 (snake_case)
- **类**: 帕斯卡命名 (PascalCase)
- **函数/变量**: 小写下划线 (snake_case)

### 开发原则
- 独立工具包：每个工具是自包含的Python包
- 配置外部化：使用YAML配置，遵循CoreRAG模式
- 本体驱动：利用OWL本体进行知识表示和推理
- 渐进式开发：基于现有基础，逐步添加组件
- Agent协作：设计多Agent协作的工作流

## 许可证

本项目采用开源许可证，详情请参考LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues: [GitHub Issues](链接待添加)
- 邮箱: [邮箱待添加]

---

*DES System Design Team - 致力于AI驱动的科学发现*