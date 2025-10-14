# CoreRAG 集成总结

## ✅ 完成状态

CoreRAG 工具已成功接入到 DESAgent 系统，遵循标准化的 `DESToolProtocol` 接口。

---

## 📋 集成内容

### 1. CoreRAG 适配器实现 (`corerag_adapter.py`)

**核心功能**：
- 封装 CoreRAG 的 `QueryManager` 为标准化接口
- 实现 `DESToolProtocol` 的 `query()` 和 `get_status()` 方法
- 自动管理 QueryManager 的生命周期（启动/停止）
- 处理本体加载和配置

**关键特性**：
```python
class CoreRAGAdapter:
    def __init__(self, max_workers: int = 2):
        # 初始化 QueryManager
        # 加载本体设置 (ONTOLOGY_SETTINGS)
        # 启动调度线程

    def query(self, query_dict: Dict) -> Optional[Dict]:
        # 提交查询到 QueryManager
        # 等待 Future 结果
        # 格式化为标准返回格式

    def get_status(self) -> Dict:
        # 检查 QueryManager 状态
        # 返回统计信息
```

**返回格式**：
```python
{
    "query": str,              # 原始查询
    "answer": str,             # 本体推理的答案
    "entities": List[str],     # 提取的实体
    "tool_calls": List[Dict],  # 本体工具调用记录
    "validation_status": str,  # 验证状态
    "formatted_text": str,     # LLM 友好格式
    "num_results": int,        # 结果数���
    "raw_state": Dict          # 完整的 QueryState
}
```

---

### 2. 配置和环境设置

**PROJECT_ROOT 设置**：
```python
# 自动设置 CoreRAG 的项目根目录
corerag_path = Path(__file__).parent.parent.parent / "tools" / "corerag"
os.environ['PROJECT_ROOT'] = str(corerag_path) + os.sep
```

**API Key 兼容性**：
```python
# 如果没有 OPENAI_API_KEY，使用 DASHSCOPE_API_KEY
if 'OPENAI_API_KEY' not in os.environ:
    if 'DASHSCOPE_API_KEY' in os.environ:
        os.environ['OPENAI_API_KEY'] = os.environ['DASHSCOPE_API_KEY']
```

**本体文件**：
- 位置：`src/tools/corerag/data/ontology/chem_ontology.owl`
- 包含：13,364 个类、5,859 个数据属性、4,557 个对象属性

---

### 3. DESAgent 集成

**在 `example_des_task.py` 中使用**：

```python
from agent.tools import create_corerag_adapter

# 初始化 CoreRAG 适配器
corerag = create_corerag_adapter(max_workers=1)
status = corerag.get_status()

if status["status"] == "ready":
    # CoreRAG 已就绪
    agent = DESAgent(..., corerag_client=corerag, ...)
```

**查询流程**：
```
DESAgent._query_corerag(task)
    ↓
CoreRAGAdapter.query(query_dict)
    ↓
QueryManager.submit_query()
    ↓
LangGraph workflow (多智能体查询流程)
    ↓
Future.result() (阻塞等待)
    ↓
格式化结果返回给 DESAgent
```

---

## 🎯 CoreRAG 工作原理

### QueryManager 架构

```
QueryManager
├── QueryQueueManager      # 查询队列和缓存
├── ThreadPoolExecutor     # 并发执行器
├── Dispatcher Thread      # 调度线程
└── Shared OntologyTools   # 共享本体工具（对象级锁保护）
```

### 查询执行流程

1. **提交查询** (`submit_query`)
   - 创建 Query 对象
   - 生成 Future 对象
   - 加入优先级队列

2. **调度执行** (Dispatcher Thread)
   - 从队列取出查询
   - 提交到 ThreadPoolExecutor

3. **LangGraph 工作流** (`_execute_query_with_langgraph`)
   - 查询规范化 (QueryParserAgent)
   - 实体匹配 (EntityMatcher)
   - 策略规划 (StrategyPlannerAgent)
   - 本体工具执行 (ToolExecutorAgent)
   - 结果验证 (ValidationAgent)
   - 答案生成 (ResultFormatterAgent)

4. **返回结果**
   - 完成 Future
   - 缓存结果（TTL: 1小时）

---

## 📊 当前工具状态对比

| 工具 | 状态 | 数据源 | 接口 | 说明 |
|------|------|--------|------|------|
| **LargeRAG** | ✅ 完成 | 531 篇文献 | 标准化 | 向量检索 |
| **CoreRAG** | ✅ 完成 | 13K+ 类本体 | 标准化 | 本体推理 |
| ExpData | 📋 待设计 | - | - | 实验数据 |

---

## 🚀 使用示例

### 基础用法

```python
from agent.tools import create_corerag_adapter

# 创建适配器
corerag = create_corerag_adapter(max_workers=2)

# 查询理论知识
result = corerag.query({
    "query": "What are the key principles for dissolving cellulose using DES?",
    "focus": ["hydrogen_bonding", "component_selection"],
    "priority": "normal"
})

if result:
    print(f"Answer: {result['answer']}")
    print(f"Entities: {result['entities']}")
    print(f"Formatted:\n{result['formatted_text']}")
```

### 在 DESAgent 中使用

```python
from agent import DESAgent
from agent.tools import create_corerag_adapter, create_largerag_adapter

# 初始化工具
corerag = create_corerag_adapter()
largerag = create_largerag_adapter()

# 创建 Agent
agent = DESAgent(
    llm_client=llm,
    reasoning_bank=bank,
    retriever=retriever,
    extractor=extractor,
    judge=judge,
    corerag_client=corerag,    # ← 本体推理
    largerag_client=largerag,  # ← 文献检索
    config=config
)

# 解决任务
result = agent.solve_task({
    "task_id": "task_001",
    "description": "Design DES for cellulose",
    "target_material": "cellulose",
    "target_temperature": 25
})
```

---

## ⚠️ 已知问题和解决方案

### 1. API Key 问题

**问题**：CoreRAG 需要 `OPENAI_API_KEY` 环境变量

**解决方案**：
- 适配器自动将 `DASHSCOPE_API_KEY` 映射为 `OPENAI_API_KEY`
- 确保在 `.env` 文件中设置了 API key

### 2. 本体文件路径

**问题**：CoreRAG 使用 `${PROJECT_ROOT}` 变量查找本体文件

**解决方案**：
- 适配器自动设置 `PROJECT_ROOT` 为 CoreRAG 目录
- 本体文件位于：`src/tools/corerag/data/ontology/`

### 3. 查询超时

**问题**：复杂查询可能超时（默认 120 秒）

**解决方案**：
```python
# 在 query() 方法中可以调整超时
state_result = future.result(timeout=120)  # 可修改此值
```

### 4. 资源清理

**问题**：QueryManager 需要显式停止

**解决方案**：
- 适配器使用 `atexit` 注册清理函数
- 也可以手动调用 `adapter._cleanup()`

---

## 🔧 配置选项

### QueryManager 参数

```python
corerag = CoreRAGAdapter(
    max_workers=2  # 并发工作线程数（默认 2）
)
```

### 查询参数

```python
result = corerag.query({
    "query": str,           # 必需：查询文本
    "focus": List[str],     # 可选：关注主题
    "priority": str         # 可选："normal", "high", "low"
})
```

---

## 📈 性能特性

1. **查询缓存**：相同查询 1 小时内返回缓存结果
2. **共享本体**：多线程共享一个本体实例（对象级锁保护）
3. **SQLite 缓存**：本体数据持久化到临时文件
4. **并发执行**：支持多个查询并发处理（可配置 max_workers）

---

## 🎓 技术栈

- **本体推理**：owlready2 + OWL 2.0
- **工作流**：LangGraph (StateGraph)
- **并发**：ThreadPoolExecutor + concurrent.futures.Future
- **LLM**：OpenAI-compatible API (DashScope/OpenAI)

---

## 📝 下一步工作

1. ✅ **标准化接口**：完成
2. ✅ **LargeRAG 集成**：完成
3. ✅ **CoreRAG 集成**：完成
4. 📋 **实验数据工具**：待设计
5. 📋 **真实实验反馈接口**：待实现
6. 📋 **端到端测试**：待进行

---

## 🔗 相关文档

- `TOOL_STANDARDIZATION.md` - 工具标准化规范
- `README.md` - 工具包概述
- `src/tools/corerag/README.md` - CoreRAG 详细文档
- `src/agent/AGENT_CODE_SUMMARY.md` - Agent 代码总结

---

**创建时间**：2025-10-14
**状态**：✅ CoreRAG 集成完成
