# Agent 目录代码总结

本文档总结了 `src/agent/` 目录下所有 Python 文件的类、函数、签名和基本功能。

---

## 1. `des_agent.py` - DES 配方设计主 Agent

### 类 (Classes)

#### `DESAgent`
```python
class DESAgent:
    def __init__(
        self,
        llm_client: Callable[[str], str],
        reasoning_bank: ReasoningBank,
        retriever: MemoryRetriever,
        extractor: MemoryExtractor,
        judge: LLMJudge,
        corerag_client: Optional[object] = None,
        largerag_client: Optional[object] = None,
        config: Optional[Dict] = None
    )
```
**功能**: DES 配方设计的主 Agent，整合 ReasoningBank 记忆系统和 CoreRAG/LargeRAG 工具。

**核心工作流**:
1. 从 ReasoningBank 检索相关记忆
2. 查询 CoreRAG 获取理论知识
3. 查询 LargeRAG 获取文献先例
4. 生成 DES 配方及推理
5. 评估结果（成功/失败）
6. 提取新记忆并巩固

**属性**:
- `llm_client`: LLM 推理客户端
- `memory`: ReasoningBank 实例
- `retriever`: 记忆检索器
- `extractor`: 记忆提取器
- `judge`: LLM 判断器
- `corerag`: CoreRAG 工具接口
- `largerag`: LargeRAG 工具接口
- `config`: 配置字典

### 方法 (Methods)

#### `solve_task(task: Dict) -> Dict`
**功能**: 解决 DES 配方任务的主入口点

**输入参数**:
- `task`: 任务字典，包含 `task_id`, `description`, `target_material`, `target_temperature`, `constraints`

**返回值**: 包含 `formulation`, `reasoning`, `confidence`, `status`, `supporting_evidence` 等的字典

#### `_retrieve_memories(task: Dict) -> List[MemoryItem]`
**功能**: 为任务检索相关记忆

#### `_query_corerag(task: Dict) -> Optional[Dict]`
**功能**: 查询 CoreRAG 获取理论知识

#### `_query_largerag(task: Dict) -> Optional[Dict]`
**功能**: 查询 LargeRAG 获取文献先例

#### `_generate_formulation(task: Dict, memories: List[MemoryItem], theory: Optional[Dict], literature: Optional[Dict]) -> Dict`
**功能**: 使用 LLM 和所有可用知识生成 DES 配方

#### `_build_formulation_prompt(task: Dict, memories: List[MemoryItem], theory: Optional[Dict], literature: Optional[Dict]) -> str`
**功能**: 构建配方生成的综合 prompt

#### `_parse_formulation_output(llm_output: str) -> Dict`
**功能**: 解析 LLM 输出以提取配方结构

---

## 2. `reasoningbank/memory.py` - 记忆数据结构

### 类 (Classes)

#### `MemoryItem`
```python
@dataclass
class MemoryItem:
    title: str
    description: str
    content: str
    source_task_id: Optional[str] = None
    is_from_success: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    embedding: Optional[List[float]] = None
    metadata: dict = field(default_factory=dict)
```
**功能**: 存储从 Agent 经验中提取的单个推理策略。与原始轨迹不同，记忆项目抽象掉底层执行细节，同时保留可迁移的推理模式。

**方法**:
- `__post_init__()`: 验证记忆项字段
- `to_dict() -> dict`: 转换为字典用于序列化
- `from_dict(data: dict) -> MemoryItem` (classmethod): 从字典创建记忆项
- `to_prompt_string() -> str`: 格式化为注入 Agent 系统 prompt 的字符串
- `to_detailed_string() -> str`: 格式化为带完整细节的多行字符串用于调试/日志

#### `MemoryQuery`
```python
@dataclass
class MemoryQuery:
    query_text: str
    top_k: int = 3
    filters: dict = field(default_factory=dict)
    min_similarity: float = 0.0
```
**功能**: 从 ReasoningBank 检索相关记忆的查询对象

#### `Trajectory`
```python
@dataclass
class Trajectory:
    task_id: str
    task_description: str
    steps: List[dict]
    outcome: str
    final_result: dict
    metadata: dict = field(default_factory=dict)
```
**功能**: 表示 Agent 针对一个任务的交互历史

**方法**:
- `to_dict() -> dict`: 转换为字典
- `from_dict(data: dict) -> Trajectory` (classmethod): 从字典创建轨迹

---

## 3. `reasoningbank/memory_manager.py` - ReasoningBank 记忆管理器

### 类 (Classes)

#### `ReasoningBank`
```python
class ReasoningBank:
    def __init__(
        self,
        embedding_func: Optional[Callable[[str], List[float]]] = None,
        max_items: int = 1000
    )
```
**功能**: Agent 推理策略的中央记忆存储和检索系统

**属性**:
- `memories`: 所有存储的 MemoryItem 对象列表
- `embedding_func`: 可选的嵌入计算函数
- `max_items`: 最大记忆容量（超出则移除最旧的）

### 方法 (Methods)

#### `add_memory(memory: MemoryItem, compute_embedding: bool = True) -> None`
**功能**: 向记忆库添加新的记忆项

#### `add_memories(memories: List[MemoryItem], compute_embeddings: bool = True) -> None`
**功能**: 批量添加多个记忆项

#### `get_all_memories() -> List[MemoryItem]`
**功能**: 获取所有存储的记忆

#### `get_memory_by_title(title: str) -> Optional[MemoryItem]`
**功能**: 通过标题检索记忆

#### `filter_memories(filters: Dict) -> List[MemoryItem]`
**功能**: 通过元数据条件过滤记忆

#### `consolidate(new_memories: List[MemoryItem]) -> None`
**功能**: 将新记忆整合到记忆库（当前实现为简单追加策略）

#### `save(filepath: str) -> None`
**功能**: 将记忆库持久化到磁盘（JSON 格式）

#### `load(filepath: str) -> None`
**功能**: 从磁盘加载记忆库

#### `clear() -> None`
**功能**: 清除记忆库中的所有记忆

#### `get_statistics() -> Dict`
**功能**: 获取记忆库的统计信息

#### `__len__() -> int`
**功能**: 返回记忆库中的记忆数量

#### `__repr__() -> str`
**功能**: 字符串表示

---

## 4. `reasoningbank/retriever.py` - 记忆检索器

### 类 (Classes)

#### `MemoryRetriever`
```python
class MemoryRetriever:
    def __init__(
        self,
        bank: ReasoningBank,
        embedding_func: Callable[[str], List[float]]
    )
```
**功能**: 使用基于嵌入的相似性搜索从 ReasoningBank 检索相关记忆

**属性**:
- `bank`: ReasoningBank 实例
- `embedding_func`: 计算查询嵌入的函数

### 方法 (Methods)

#### `retrieve(query: MemoryQuery) -> List[MemoryItem]`
**功能**: 检索查询的 top-k 最相关记忆

#### `retrieve_with_scores(query: MemoryQuery) -> List[Tuple[MemoryItem, float]]`
**功能**: 检索记忆及其相似度分数

#### `_get_candidates(filters: dict) -> List[MemoryItem]`
**功能**: 通过应用过滤器获取候选记忆（私有方法）

#### `_score_memories(query_embedding: List[float], candidates: List[MemoryItem]) -> List[Tuple[MemoryItem, float]]`
**功能**: 计算候选记忆的相似度分数（私有方法）

#### `_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float` (staticmethod)
**功能**: 计算两个向量之间的余弦相似度

### 函数 (Functions)

#### `format_memories_for_prompt(memories: List[MemoryItem]) -> str`
**功能**: 将检索到的记忆格式化为注入 Agent 系统 prompt 的字符串

---

## 5. `reasoningbank/judge.py` - LLM 判断器

### 类 (Classes)

#### `LLMJudge`
```python
class LLMJudge:
    def __init__(
        self,
        llm_client: Callable[[str], str],
        temperature: float = 0.0
    )
```
**功能**: 基于 LLM 的轨迹结果评估器，用于在没有真值标签的情况下进行测试时学习

**属性**:
- `llm_client`: 调用 LLM 的函数或对象
- `temperature`: 采样温度（0.0 为确定性）

### 方法 (Methods)

#### `evaluate(trajectory: Trajectory) -> Dict`
**功能**: 评估轨迹是成功还是失败

**返回值**: 包含 `status` ("success"/"failure"), `thoughts` (判断推理), `reason` (失败解释) 的字典

#### `_build_judge_prompt(trajectory: Trajectory) -> str`
**功能**: 从轨迹构建判断 prompt（私有方法）

#### `_format_trajectory_steps(steps: list) -> str`
**功能**: 格式化轨迹步骤用于显示在 prompt 中（私有方法）

---

## 6. `reasoningbank/extractor.py` - 记忆提取器

### 类 (Classes)

#### `MemoryExtractor`
```python
class MemoryExtractor:
    def __init__(
        self,
        llm_client: Callable[[str], str],
        temperature: float = 1.0,
        max_items_per_trajectory: int = 3
    )
```
**功能**: 从 Agent 轨迹中提取可泛化的推理策略，将原始执行历史转换为结构化记忆项

**属性**:
- `llm_client`: 调用 LLM 的函数或对象
- `temperature`: 提取的采样温度（更高 = 更多样化的记忆）
- `max_items_per_trajectory`: 每个轨迹的最大记忆项数

### 方法 (Methods)

#### `extract_from_trajectory(trajectory: Trajectory, outcome: Literal["success", "failure"]) -> List[MemoryItem]`
**功能**: 从单个轨迹提取记忆项

#### `extract_from_multiple_trajectories(trajectories: List[Trajectory], outcomes: List[str]) -> List[MemoryItem]`
**功能**: 通过比较多个轨迹提取记忆（MaTTS 并行扩展），使用自我对比识别一致的成功模式和常见陷阱

#### `_build_extraction_prompt(trajectory: Trajectory, outcome: str) -> str`
**功能**: 为单个轨迹构建提取 prompt（私有方法）

#### `_build_parallel_prompt(trajectories: List[Trajectory], outcomes: List[str]) -> str`
**功能**: 为并行轨迹提取构建 prompt（私有方法）

---

## 7. `reasoningbank/__init__.py` - ReasoningBank 包初始化

**导出的组件**:
- `MemoryItem`, `MemoryQuery`, `Trajectory`
- `ReasoningBank`
- `MemoryRetriever`, `format_memories_for_prompt`
- `MemoryExtractor`
- `LLMJudge`

**版本**: `__version__ = "0.1.0"`

---

## 8. `prompts/extraction_prompts.py` - 记忆提取 Prompts

### 常量 (Constants)

#### `SUCCESS_EXTRACTION_PROMPT`
**功能**: 指导 LLM 从成功的轨迹中提取可泛化推理策略的 prompt 模板

#### `FAILURE_EXTRACTION_PROMPT`
**功能**: 指导 LLM 从失败的轨迹中提取教训和预防策略的 prompt 模板

#### `PARALLEL_MATTS_PROMPT`
**功能**: 用于通过比较多个轨迹提取策略的 prompt 模板（支持 MaTTS 并行扩展）

### 函数 (Functions)

#### `format_trajectory_for_extraction(trajectory: dict) -> str`
**功能**: 格式化轨迹字典用于提取 prompts

#### `parse_extracted_memories(llm_output: str) -> list`
**功能**: 解析 LLM 输出以提取记忆项

**预期格式**:
```
# Memory Item N
## Title: ...
## Description: ...
## Content: ...
```

**返回值**: 包含 `title`, `description`, `content` 键的字典列表

---

## 9. `prompts/judge_prompts.py` - 判断 Prompts

### 常量 (Constants)

#### `JUDGE_PROMPT`
**功能**: 指导 LLM 评估 DES 配方任务是否成功完成的 prompt 模板

**评估标准**:
- **成功**: 有效的 HBD/HBA、合理的摩尔比、满足约束、科学合理的推理
- **失败**: 无效配方、化学不兼容、不切实际的摩尔比、违反化学原理

### 函数 (Functions)

#### `parse_judge_output(llm_output: str) -> dict`
**功能**: 解析 LLM 判断输出以提取状态和推理

**预期格式**:
```
Thoughts: ...
Status: SUCCESS/FAILURE
Reason: ... (可选，仅用于失败)
```

**返回值**: 包含 `status` ("success"/"failure"), `thoughts`, `reason` (可选) 的字典

---

## 10. `prompts/__init__.py` - Prompts 包初始化

**导出的组件**:
- `SUCCESS_EXTRACTION_PROMPT`
- `FAILURE_EXTRACTION_PROMPT`
- `PARALLEL_MATTS_PROMPT`
- `format_trajectory_for_extraction`
- `parse_extracted_memories`
- `JUDGE_PROMPT`
- `parse_judge_output`

---

## 11. `examples/example_des_task.py` - DES 任务示例脚本

### 函数 (Functions)

#### `mock_llm_client(prompt: str) -> str`
**功能**: 用于演示的模拟 LLM 客户端（生产环境中应替换为实际 API）

#### `mock_embedding_func(text: str) -> list`
**功能**: 用于演示的模拟嵌入函数（生产环境中应使用 OpenAI embeddings API）

#### `load_config(config_path: str = None) -> dict`
**功能**: 从 YAML 文件加载配置

#### `create_mock_corerag_client()`
**功能**: 创建模拟的 CoreRAG 客户端

#### `create_mock_largerag_client()`
**功能**: 创建模拟的 LargeRAG 客户端

#### `main()`
**功能**: 主示例工作流，演示完整的 ReasoningBank 框架使用

**演示流程**:
1. 加载配置
2. 初始化 ReasoningBank 组件（bank, retriever, extractor, judge）
3. 创建工具客户端（CoreRAG, LargeRAG）
4. 初始化 DESAgent
5. 顺序解决多个测试任务
6. 显示结果和统计信息
7. 保存记忆库

---

## 12. `tests/test_reasoningbank.py` - ReasoningBank 单元测试

### 测试类 (Test Classes)

#### `TestMemoryItem`
**功能**: 测试 MemoryItem 数据结构

**测试方法**:
- `test_create_memory_item()`: 测试创建有效的记忆项
- `test_memory_validation()`: 测试空字段是否引发错误
- `test_memory_serialization()`: 测试 `to_dict` 和 `from_dict`
- `test_prompt_formatting()`: 测试 prompt 字符串生成

#### `TestReasoningBank`
**功能**: 测试 ReasoningBank 记忆管理器

**测试方法**:
- `test_create_bank()`: 测试创建记忆库
- `test_add_memory()`: 测试添加记忆
- `test_max_items_limit()`: 测试记忆库强制执行 max_items 限制
- `test_filter_memories()`: 测试通过元数据过滤
- `test_save_load()`: 测试持久化

#### `TestMemoryRetriever`
**功能**: 测试 MemoryRetriever

**测试方法**:
- `test_create_retriever()`: 测试创建检索器
- `test_retrieval()`: 测试记忆检索
- `test_retrieval_with_filters()`: 测试带元数据过滤器的检索

#### `TestTrajectory`
**功能**: 测试 Trajectory 数据结构

**测试方法**:
- `test_create_trajectory()`: 测试创建轨迹
- `test_trajectory_serialization()`: 测试轨迹的 to/from dict

### 辅助函数 (Helper Functions)

#### `mock_embedding(text: str) -> list`
**功能**: 用于测试的模拟嵌入函数

**运行测试**: `python -m pytest test_reasoningbank.py -v`

---

## 13. `utils/llm_client.py` - LLM 客户端

### 类 (Classes)

#### `LLMClient`
```python
class LLMClient:
    def __init__(
        self,
        provider: str = "dashscope",
        model: str = "qwen-plus",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    )
```
**功能**: 使用 OpenAI 兼容 API 的通用 LLM 客户端

**支持的提供商**:
- OpenAI (api.openai.com)
- DashScope/Aliyun (dashscope.aliyuncs.com/compatible-mode/v1)
- 自定义 OpenAI 兼容端点

**属性**:
- `client`: OpenAI 客户端实例
- `model`: 模型名称
- `temperature`: 采样温度
- `max_tokens`: 最大完成令牌数

### 方法 (Methods)

#### `chat(prompt: str, system_prompt: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None, **kwargs) -> str`
**功能**: 发送聊天完成请求

**参数**:
- `prompt`: 用户 prompt
- `system_prompt`: 可选的系统 prompt
- `temperature`: 覆盖默认温度
- `max_tokens`: 覆盖默认 max_tokens
- `**kwargs`: API 调用的额外参数

**返回值**: 生成的文本响应

#### `__call__(prompt: str, **kwargs) -> str`
**功能**: `chat()` 方法的简写

### 函数 (Functions)

#### `create_llm_client_from_config(config: Dict[str, Any]) -> LLMClient`
**功能**: 从配置字典创建 LLM 客户端

---

## 14. `utils/embedding_client.py` - 嵌入客户端

### 类 (Classes)

#### `EmbeddingClient`
```python
class EmbeddingClient:
    def __init__(
        self,
        provider: str = "dashscope",
        model: str = "text-embedding-v3",
        dimension: Optional[int] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    )
```
**功能**: 使用 OpenAI 兼容 API 的通用嵌入客户端

**支持的提供商**:
- OpenAI (text-embedding-3-small, text-embedding-3-large)
- DashScope/Aliyun (text-embedding-v3)
- 自定义 OpenAI 兼容端点

**属性**:
- `client`: OpenAI 客户端实例
- `model`: 嵌入模型名称
- `dimension`: 嵌入维度（如果支持）

### 方法 (Methods)

#### `embed(text: str, **kwargs) -> List[float]`
**功能**: 为单个文本生成嵌入

#### `embed_batch(texts: List[str], **kwargs) -> List[List[float]]`
**功能**: 为多个文本生成嵌入

#### `__call__(text: str, **kwargs) -> List[float]`
**功能**: `embed()` 方法的简写

#### `cosine_similarity(vec1: List[float], vec2: List[float]) -> float`
**功能**: 计算两个向量之间的余弦相似度

**返回值**: 余弦相似度（0 到 1）

### 函数 (Functions)

#### `create_embedding_client_from_config(config: Dict[str, Any]) -> EmbeddingClient`
**功能**: 从配置字典创建嵌入客户端

---

## 总结

### 核心架构组件

1. **DESAgent** (`des_agent.py`): 主 Agent 类，编排整个 DES 配方设计流程
2. **ReasoningBank 系统** (`reasoningbank/`):
   - `MemoryItem`, `MemoryQuery`, `Trajectory`: 核心数据结构
   - `ReasoningBank`: 记忆存储和管理
   - `MemoryRetriever`: 基于嵌入的相似性搜索
   - `MemoryExtractor`: 从轨迹提取推理策略
   - `LLMJudge`: LLM 驱动的成功/失败评估
3. **Prompts** (`prompts/`): 用于提取和判断的 LLM prompt 模板
4. **工具类** (`utils/`): LLM 和嵌入 API 客户端

### 工作流

```
用户任务 → DESAgent.solve_task()
    ↓
    1. 检索相关记忆 (MemoryRetriever)
    2. 查询工具 (CoreRAG, LargeRAG)
    3. 生成配方 (LLM + 记忆 + 知识)
    4. 评估结果 (LLMJudge)
    5. 提取新记忆 (MemoryExtractor)
    6. 巩固到记忆库 (ReasoningBank)
    ↓
返回结果 + 更新的记忆库
```

### 设计特点

- **记忆增强**: 从过去经验中学习，无需重新训练模型
- **测试时学习**: 使用 LLM-as-a-Judge 在没有真值标签的情况下学习
- **多源知识融合**: 整合理论知识（CoreRAG）、文献知识（LargeRAG）和经验知识（ReasoningBank）
- **可扩展架构**: 模块化设计，易于添加新工具和记忆策略
