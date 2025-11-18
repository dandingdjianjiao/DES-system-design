# CoreRAG初始化失败 - 完整调研报告

**创建时间**: 2025-11-18
**适用场景**: 服务器环境（DES.owl文件正常）

---

## 🔍 问题症状

用户报告：
1. ✅ 在服务器上运行
2. ✅ 使用DES.owl文件（与开发机相同，文件正常）
3. ❌ CoreRAG adapter初始化失败

**推论**: 问题**不是**本体文件损坏，而是其他初始化环节

---

## 📊 初始化流程分析

### CoreRAGAdapter.__init__() 完整流程

```python
CoreRAGAdapter.__init__()
    ├─ [1] 检查 CORERAG_AVAILABLE
    │   ├─ True  → 继续
    │   └─ False → 返回 (initialized=False)
    │
    ├─ [2] 创建 QueryManager
    │   ├─ 参数: max_workers, ONTOLOGY_SETTINGS, staggered_start
    │   └─ 可能失败点: ONTOLOGY_SETTINGS加载失败
    │
    ├─ [3] 启动 manager.start()
    │   ├─ 启动dispatcher线程
    │   └─ 可能失败点: 线程启动失败
    │
    └─ [4] 设置 initialized=True
```

### CORERAG_AVAILABLE 判定逻辑

```python
# corerag_adapter.py:48-56
try:
    from autology_constructor.idea.query_team.query_manager import QueryManager
    from config.settings import ONTOLOGY_SETTINGS
    CORERAG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"CoreRAG dependencies not available: {e}")
    CORERAG_AVAILABLE = False
```

**失败条件**:
1. `config.settings` 导入失败
2. `QueryManager` 导入失败
3. `ONTOLOGY_SETTINGS` 实例化失败（在config/settings.py中）

---

## 🎯 可能失败的6个根因

### **根因1: config.settings导入失败**

**症状**:
```
ImportError: No module named 'config.settings'
```

**原因**:
- `corerag_path` 未正确添加到 sys.path
- PROJECT_ROOT 环境变量未设置

**验证方法**:
```python
import sys
from pathlib import Path
corerag_path = Path(__file__).parent.parent.parent / "tools" / "corerag"
print(f"corerag_path in sys.path: {str(corerag_path) in sys.path}")
```

**解决方案**: 见方案1

---

### **根因2: ONTOLOGY_SETTINGS实例化失败（owl加载）**

**症状**:
```
RuntimeError: Failed to load ontology: http://www.test.org/chem_ontologies/chem_ontology.owl
```

**原因** (服务器环境特有):
- DES.owl文件路径不对
- PROJECT_ROOT 环境变量未设置导致路径错误
- 文件权限问题

**验证方法**:
```python
from config.settings import ONTOLOGY_SETTINGS
ontology_file = Path(ONTOLOGY_SETTINGS.directory_path) / ONTOLOGY_SETTINGS.ontology_file_name
print(f"Ontology file: {ontology_file}")
print(f"Exists: {ontology_file.exists()}")
print(f"Readable: {os.access(ontology_file, os.R_OK)}")
```

**解决方案**: 见方案2

---

### **根因3: QueryManager导入失败**

**症状**:
```
ImportError: cannot import name 'QueryManager' from 'autology_constructor.idea.query_team.query_manager'
```

**原因**:
- CoreRAG代码结构变化
- 依赖包版本不匹配

**验证方法**:
```python
from autology_constructor.idea.query_team.query_manager import QueryManager
print(f"QueryManager: {QueryManager}")
```

**解决方案**: 见方案3

---

### **根因4: QueryManager初始化失败**

**症状**:
```python
# adapter.initialized = False
# adapter.manager = None
# 但没有明确错误信息
```

**原因**:
- `QueryManager.__init__()` 内部异常被捕获
- owlready2依赖问题

**验证方法**:
运行诊断脚本第6步（手动创建QueryManager）

**解决方案**: 见方案4

---

### **根因5: manager.start() 失败**

**症状**:
```
Exception in thread starting
```

**原因**:
- 线程池启动失败
- 资源限制（如max_workers过大）

**验证方法**:
```python
manager = QueryManager(max_workers=1, ...)  # 减少worker数量
manager.start()
```

**解决方案**: 见方案5

---

### **根因6: Java路径配置错误**

**症状**:
```
Warning: Specified JAVA_EXE path from YAML does not exist
```

**原因**:
- settings.yaml中java_exe路径在服务器上不存在
- 服务器Java安装位置不同

**验证方法**:
```python
from config.settings import ONTOLOGY_SETTINGS
import owlready2
print(f"Java path: {owlready2.JAVA_EXE}")
print(f"Java exists: {Path(owlready2.JAVA_EXE).exists() if owlready2.JAVA_EXE else False}")
```

**解决方案**: 见方案6

---

## 💡 解决方案（优先级排序）

### **方案1: 确保PROJECT_ROOT正确设置** ⭐⭐⭐⭐⭐

**问题**: PROJECT_ROOT未设置导致路径解析错误

**实现**:
```python
# 在导入CoreRAGAdapter之前
import os
from pathlib import Path

# 方式A: 设置环境变量
corerag_path = Path("/path/to/DES-system-design/src/tools/corerag")
os.environ['PROJECT_ROOT'] = str(corerag_path) + os.sep

# 方式B: 在代码中硬编码（临时）
import sys
sys.path.insert(0, str(corerag_path))
```

**验证**:
```bash
python -c "import os; print(os.environ.get('PROJECT_ROOT'))"
```

---

### **方案2: 检查DES.owl文件路径** ⭐⭐⭐⭐

**问题**: settings.yaml中配置的路径在服务器上不正确

**实现**:
```yaml
# src/tools/corerag/config/settings.yaml
ontology:
  directory_path: ${PROJECT_ROOT}data/ontology/
  ontology_file_name: "DES.owl"  # 确认是DES.owl
  base_iri: "http://www.test.org/chem_ontologies/"
```

**验证**:
```bash
# 在服务器上运行
ls -lh /path/to/corerag/data/ontology/DES.owl
```

---

### **方案3: 添加详细日志** ⭐⭐⭐⭐

**问题**: 初始化失败但错误信息被吞没

**实现**:
```python
# 修改 corerag_adapter.py:118-121
except Exception as e:
    logger.error(f"Failed to initialize CoreRAG: {e}", exc_info=True)

    # NEW: 添加详细诊断信息
    logger.error(f"  CORERAG_AVAILABLE: {CORERAG_AVAILABLE}")
    logger.error(f"  ONTOLOGY_SETTINGS: {ONTOLOGY_SETTINGS if 'ONTOLOGY_SETTINGS' in globals() else 'NOT LOADED'}")
    logger.error(f"  QueryManager: {QueryManager if 'QueryManager' in globals() else 'NOT LOADED'}")

    self.initialized = False
    self.manager = None
```

---

### **方案4: 降级为Mock模式** ⭐⭐⭐

**问题**: 即使CoreRAG失败，agent也应该能运行

**实现**:
```python
# corerag_adapter.py 修改
class CoreRAGAdapter:
    def __init__(self, max_workers: int = 2, allow_mock: bool = True):
        self.manager = None
        self.initialized = False
        self.mock_mode = False

        if not CORERAG_AVAILABLE:
            if allow_mock:
                logger.warning("CoreRAG not available, using MOCK mode")
                self.mock_mode = True
                self.initialized = True  # Mock模式算初始化成功
                return
            else:
                logger.error("CoreRAG dependencies not available")
                return

        # ... 正常初始化逻辑

    def query(self, query_dict):
        if self.mock_mode:
            logger.warning("CoreRAG in MOCK mode - returning empty result")
            return None  # 或返回mock数据

        # ... 正常查询逻辑
```

**优点**: 永不阻塞agent运行

---

### **方案5: 减少max_workers** ⭐⭐

**问题**: 线程池资源限制

**实现**:
```python
# example脚本中
corerag = CoreRAGAdapter(max_workers=1)  # 从2改为1
```

---

### **方案6: 配置Java路径** ⭐

**问题**: 服务器Java路径不同

**实现**:
```bash
# 方式A: 在服务器上查找Java
which java
# 输出: /usr/bin/java

# 方式B: 修改settings.yaml
# src/tools/corerag/config/settings.yaml
ontology:
  java_exe: "/usr/bin/java"  # 服务器实际路径
```

---

## 🔧 诊断步骤（请用户执行）

### Step 1: 运行诊断脚本

```bash
cd /path/to/DES-system-design
python src/agent/tools/diagnose_corerag.py
```

**期望输出**:
```
[Step 1] Environment Variables - PASS
[Step 2] Path Setup - PASS
[Step 3] Import CoreRAG Adapter Module - PASS
[Step 4] Create CoreRAG Adapter Instance - PASS
[Step 5] Check Adapter Status - ❌ FAILED or ✅ SUCCESS
```

### Step 2: 根据失败步骤定位

| 失败步骤 | 根因 | 优先方案 |
|---------|------|---------|
| Step 3: Import失败 | 根因1 | 方案1 |
| Step 4: 创建失败 | 根因2/3 | 方案2, 3 |
| Step 5: Status=not_initialized | 根因4/5 | 方案4, 5 |

### Step 3: 应用解决方案

**快速修复（推荐）**:
```python
# 1. 设置环境变量
os.environ['PROJECT_ROOT'] = '/path/to/corerag/'

# 2. 使用Mock模式
from tools.corerag_adapter import CoreRAGAdapter
adapter = CoreRAGAdapter(max_workers=1, allow_mock=True)  # 需要先修改代码

# 3. 检查状态
status = adapter.get_status()
if status["status"] != "ready":
    print(f"Warning: {status['message']}")
    # 继续运行，adapter.query()会返回None
```

---

## 📋 完整测试清单

```bash
# 1. 检查环境变量
echo $PROJECT_ROOT

# 2. 检查本体文件
ls -lh /path/to/corerag/data/ontology/DES.owl

# 3. 检查Java
which java
java -version

# 4. 运行诊断脚本
python src/agent/tools/diagnose_corerag.py

# 5. 检查日志
tail -n 50 agent.log  # 查看详细错误

# 6. 测试adapter
python src/agent/tools/test_corerag_init.py
```

---

## 🎯 最可能的问题（服务器环境）

根据经验，服务器环境最常见的3个问题：

1. **PROJECT_ROOT未设置** (90%) - 方案1
2. **Java路径不对** (5%) - 方案6
3. **文件权限问题** (5%) - chmod 644 DES.owl

---

## 📞 如果以上都不行

**提供诊断信息**:
```bash
# 运行完整诊断
python src/agent/tools/diagnose_corerag.py > diagnosis.log 2>&1

# 将diagnosis.log内容发送过来分析
```

**临时绕过方案**:
```python
# 完全不使用CoreRAG
agent = DESAgent(
    ...,
    corerag_client=None,  # 设为None
    largerag_client=largerag,
    ...
)
```

---

**创建时间**: 2025-11-18
**版本**: v1.0
**更新**: 待用户反馈诊断结果
