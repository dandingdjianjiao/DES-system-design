# DESAgent 工具标准化规范

## 概述

为了保证 DESAgent 能够统一管理多个知识工具（LargeRAG、CoreRAG、实验数据工具等），我们定义了 **`DESToolProtocol`** 接口协议，所有工具适配器都必须遵循这个接口。

## 设计原则

1. **统一接口**: 所有工具���用相同的 `query()` 和 `get_status()` 方法
2. **鸭子类型**: 使用 `typing.Protocol`，不强制继承基类
3. **灵活扩展**: 各工具可以有自己的特殊方法和返回格式
4. **类型安全**: 提供完整的类型提示支持

## 核心接口定义

### DESToolProtocol

所有工具适配器必须实现以下两个方法：

```python
from typing import Protocol, Dict, Optional, Any

class DESToolProtocol(Protocol):
    def query(self, query_dict: Dict[str, Any]) -> Optional[Dict]:
        """
        查询工具获取知识

        Args:
            query_dict: 查询参数字典
                - query (str): 查询文本 [必需]
                - top_k (int): 返回结果数量 [可选]
                - filters (dict): 过滤条件 [可选]
                - ... 工具特定参数

        Returns:
            包含查询结果的字典，或失败时返回 None
            ��荐包含字段：
                - query (str): 原始查询文本
                - formatted_text (str): 格式化的结果文本（供 LLM 使用）
                - num_results (int): 结果数量
                - ... 工具特定字段
        """
        ...

    def get_status(self) -> Dict[str, Any]:
        """
        获取工具状态

        Returns:
            包含状态信息的字典：
                - status (str): 状态码（ready/error/no_data/not_initialized）
                - message (str): 可读的状态消息 [可选]
                - stats (dict): 统计信息 [可选]
        """
        ...
```

### 标准状态码

```python
class ToolStatus:
    READY = "ready"                      # 工具已就绪
    ERROR = "error"                      # 工具错误
    NO_DATA = "no_data"                  # 无数据加载
    NOT_INITIALIZED = "not_initialized"  # 未初始化
```

## 已实现的工具

### 1. LargeRAGAdapter ✅

**功能**: 从 10,000+ 篇 DES 文献中检索信息

**实现文件**: `largerag_adapter.py`

**查询示例**:
```python
from agent.tools import create_largerag_adapter

largerag = create_largerag_adapter()

result = largerag.query({
    "query": "DES formulations for cellulose at 25��C",
    "top_k": 5,
    "filters": {"material_type": "polymer"}
})

# 返回格式
{
    "query": "DES formulations for cellulose at 25°C",
    "num_results": 5,
    "documents": [...],  # 原始文档列表
    "formatted_text": "Document 1...\n\nDocument 2..."  # LLM 友好格式
}
```

**状态检查**:
```python
status = largerag.get_status()
# {"status": "ready", "stats": {"document_count": 531, ...}}
```

### 2. CoreRAGAdapter 🚧

**功能**: 从化学本体中查询理论知识

**实现文件**: `corerag_adapter.py`

**当前状态**: 模板已创建，等待集成真实 CoreRAG 系统

**查询示例**:
```python
from agent.tools import create_corerag_adapter

corerag = create_corerag_adapter()

result = corerag.query({
    "query": "What are the key principles for dissolving cellulose using DES?",
    "focus": ["hydrogen_bonding", "component_selection", "molar_ratio"]
})

# 返回格式
{
    "query": "...",
    "theory": "理论知识文本",
    "entities": ["Cellulose", "Hydrogen Bond", ...],
    "relationships": [...],
    "formatted_text": "## Theoretical Principles...",
    "num_results": 1
}
```

### 3. ExperimentalDataTool 📋

**功能**: 查询实验数据库（配方-温度-溶解度）

**状态**: 设计阶段，未实现

## 在 DESAgent 中使用

### 初始化工具

```python
from agent.tools import (
    create_largerag_adapter,
    create_corerag_adapter,
    validate_tool_interface
)
from agent.des_agent import DESAgent

# 创建工具适配器
largerag_client = create_largerag_adapter()
corerag_client = create_corerag_adapter()

# 验证接口（可选）
assert validate_tool_interface(largerag_client)
assert validate_tool_interface(corerag_client)

# 初始化 Agent
agent = DESAgent(
    llm_client=llm_client,
    reasoning_bank=bank,
    retriever=retriever,
    extractor=extractor,
    judge=judge,
    corerag_client=corerag_client,
    largerag_client=largerag_client,
    config=config
)
```

### Agent 内部调用

在 `DESAgent._query_largerag()` 和 `DESAgent._query_corerag()` 方法中：

```python
def _query_largerag(self, task: Dict) -> Optional[Dict]:
    if not self.largerag:
        return None

    query = {
        "query": f"DES formulations for {task['target_material']}",
        "top_k": 10
    }

    result = self.largerag.query(query)  # 统一接口
    return result

def _query_corerag(self, task: Dict) -> Optional[Dict]:
    if not self.corerag:
        return None

    query = {
        "query": f"Key principles for dissolving {task['target_material']}",
        "focus": ["hydrogen_bonding", "component_selection"]
    }

    result = self.corerag.query(query)  # 统一接口
    return result
```

## 接口验证

### 自动验证

```python
from agent.tools import validate_tool_interface

# 验证工具是否符合协议
is_valid = validate_tool_interface(my_tool)
if not is_valid:
    raise ValueError("Tool does not implement DESToolProtocol")
```

### 手动检查

```python
# 检查方法是否存���
assert hasattr(tool, 'query') and callable(tool.query)
assert hasattr(tool, 'get_status') and callable(tool.get_status)
```

## 创建新工具适配器

### 模板

```python
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class MyToolAdapter:
    """
    适配器说明

    Implements: DESToolProtocol
    """

    def __init__(self):
        """初始化工具"""
        try:
            # 初始化底层工具
            self.tool = MyTool()
            logger.info("MyTool adapter initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MyTool: {e}")
            self.tool = None

    def query(self, query_dict: Dict[str, Any]) -> Optional[Dict]:
        """查询方法"""
        if self.tool is None:
            logger.error("MyTool not initialized")
            return None

        try:
            query_text = query_dict.get("query", "")
            # 调用底层工具
            result = self.tool.search(query_text)

            # 格式化为标准返回格式
            return {
                "query": query_text,
                "formatted_text": self._format_result(result),
                "num_results": len(result),
                "raw_data": result
            }
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """状态检查"""
        if self.tool is None:
            return {"status": "error", "message": "Tool not initialized"}

        return {"status": "ready"}

    def _format_result(self, result) -> str:
        """格式化结果为 LLM 友好文本"""
        return str(result)

# 便捷函数
def create_my_tool_adapter():
    return MyToolAdapter()
```

### 集成到 `__init__.py`

```python
from .my_tool_adapter import MyToolAdapter, create_my_tool_adapter

__all__ = [
    ...,
    "MyToolAdapter",
    "create_my_tool_adapter",
]
```

## 优势

1. **统一管理**: DESAgent 只需要知道 `query()` 和 `get_status()` 两个方法
2. **易于扩展**: 添加新工具只需实现这两个方法
3. **类型安全**: IDE 可以提供自动补全和类型检查
4. **灵活性高**: 各工具可以有自己的特殊返回格式
5. **便于测试**: 可以轻松创建 mock 工具用于测试

## 测试

运行工具测试：

```bash
# 测试 LargeRAG 适配器
conda activate ontologyconstruction
python src/agent/tools/largerag_adapter.py

# 测试 CoreRAG 适配器
python src/agent/tools/corerag_adapter.py
```

## 下一步

1. ✅ LargeRAG 适配器：已完成并测试
2. 🚧 CoreRAG 适配器：模板已创建，需要集成真实系统
3. 📋 实验数据工具：待设计和实现
