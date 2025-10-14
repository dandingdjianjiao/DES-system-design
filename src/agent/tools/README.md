# DESAgent 工具适配器

本目录包含 DESAgent 使用的所有外部知识工具的标准化适配器。

## 🎯 设计理念

为了让 DESAgent 能够统一管理多个异构知识源，我们定义了 **`DESToolProtocol`** 接口协议。所有工具适配器都遵循这个协议，提供统一的调用方式。

## 📁 文件结构

```
tools/
├── README.md                      # 本文件
├── TOOL_STANDARDIZATION.md        # 详细标准化规范
├── __init__.py                    # 包导出
├── base.py                        # DESToolProtocol 定义
├── largerag_adapter.py            # ✅ LargeRAG 适配器（已实现）
└── corerag_adapter.py             # 🚧 CoreRAG 适配器（模板）
```

## ⚡ 快速开始

### 1. 导入工具

```python
from agent.tools import (
    create_largerag_adapter,
    create_corerag_adapter,
    DESToolProtocol,
    ToolStatus
)
```

### 2. 创建适配器

```python
# 创建 LargeRAG 适配器（文献检索）
largerag = create_largerag_adapter()

# 创建 CoreRAG 适配器（理论知识）
corerag = create_corerag_adapter()

# 检查状态
print(largerag.get_status())  # {"status": "ready", ...}
print(corerag.get_status())   # {"status": "not_initialized", ...}
```

### 3. 查询工具

```python
# 查询 LargeRAG
result = largerag.query({
    "query": "DES for cellulose dissolution",
    "top_k": 5
})

if result:
    print(f"找到 {result['num_results']} 个文献")
    print(result['formatted_text'])  # LLM 友好格式
```

### 4. 在 DESAgent 中使用

```python
from agent.des_agent import DESAgent

agent = DESAgent(
    llm_client=llm_client,
    reasoning_bank=bank,
    retriever=retriever,
    extractor=extractor,
    judge=judge,
    corerag_client=corerag,      # ← 标准化接口
    largerag_client=largerag,    # ← 标准化接口
    config=config
)

# Agent 内部统一调用 query() 方法
result = agent.solve_task(task)
```

## 🛠️ 已实现的工具

### LargeRAG Adapter ✅

**功能**: 从 10,000+ 篇 DES 科学文献中检索信息

**状态**: 已完成并测试通过

**数据源**: Chroma 向量数据库（531 个文档已索引）

**测试**:
```bash
conda activate ontologyconstruction
python src/agent/tools/largerag_adapter.py
```

**输出示例**:
```
✓ Implements DESToolProtocol: True
✓ Status: {'status': 'ready', 'stats': {...}}
✓ Retrieved 3 documents
```

### CoreRAG Adapter 🚧

**功能**: 从化学本体查询理论知识

**状态**: 模板已创建，等待集成 CoreRAG 系统

**下一步**: 取消注释 TODO 部分，连接真实的 CoreRAG 查询系统

**测试**:
```bash
python src/agent/tools/corerag_adapter.py
```

## 🔌 接口协议

所有工具必须实现 `DESToolProtocol`:

```python
class DESToolProtocol(Protocol):
    def query(self, query_dict: Dict[str, Any]) -> Optional[Dict]:
        """查询工具"""
        ...

    def get_status(self) -> Dict[str, Any]:
        """获取状态"""
        ...
```

**标准状态码**:
- `"ready"`: 工具已就绪
- `"error"`: 工具错误
- `"no_data"`: 无数据加载
- `"not_initialized"`: 未初始化

详细规范请参考 [`TOOL_STANDARDIZATION.md`](./TOOL_STANDARDIZATION.md)

## ✅ 接口验证

```python
from agent.tools import validate_tool_interface

# 验证工具是否符合协议
is_valid = validate_tool_interface(my_tool)
print(f"Tool is valid: {is_valid}")
```

## 📊 当前实现状态

| 工具 | 状态 | 文件 | 说明 |
|------|------|------|------|
| **LargeRAG** | ✅ 完成 | `largerag_adapter.py` | 文献检索，531 篇文档已索引 |
| **CoreRAG** | 🚧 模板 | `corerag_adapter.py` | 本体查询，等待集成 |
| **ExperimentalData** | 📋 规划 | - | 实验数据查询，待设计 |

## 🚀 添加新工具

1. 复制 `corerag_adapter.py` 作为模板
2. 实现 `query()` 和 `get_status()` 方法
3. 在 `__init__.py` 中导出
4. 添加测试代码
5. 更新本 README

详细步骤请参考 `TOOL_STANDARDIZATION.md` 中的"创建新工具适配器"章节。

## 🎓 设计优势

1. **统一接口**: DESAgent 无需关心工具内部实现
2. **易于扩展**: 添加新工具只需实现 2 个方法
3. **类型安全**: 使用 `typing.Protocol` 提供类型检查
4. **灵活性高**: 各工具可以有自己的特殊返回格式
5. **便于测试**: 可以轻松创建 mock 工具

## 📚 相关文档

- [`TOOL_STANDARDIZATION.md`](./TOOL_STANDARDIZATION.md) - 详细标准化规范
- [`base.py`](./base.py) - Protocol 定义和辅助类
- [`../AGENT_CODE_SUMMARY.md`](../AGENT_CODE_SUMMARY.md) - Agent 代码总结

## 🔗 使用示例

完整示例请参考:
- `src/agent/examples/example_des_task.py` - 完整 Agent 使用示例
- `src/agent/des_agent.py` - Agent 内部如何调用工具

---

**问题反馈**: 如有问题请在项目 issue 中提出
