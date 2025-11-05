# Reranker 过滤配置说明

## 概述

在检索系统中，有两个阶段可以进行相似度过滤：
1. **向量检索阶段**: 基于 cosine 相似度过滤
2. **Reranker 阶段**: 基于 Reranker 模型的重排分数过滤

由于这两种分数是**不同的度量标准**，现在提供了**两个独立的阈值参数**来分别控制这两个阶段的过滤。

## 配置参数

在 `src/tools/largerag/config/settings.yaml` 的 `retrieval` 配置块中：

```yaml
retrieval:
  similarity_top_k: 20              # 向量检索召回数量
  rerank_top_n: 10                  # Reranker 最终返回数量
  similarity_threshold: 0.8         # 向量检索相似度阈值（0 = 禁用，>0 = 启用）
  rerank_threshold: 0.0              # Reranker 分数阈值（0 = 禁用，>0 = 启用）
```

### 参数说明

- **`similarity_threshold`**: 向量检索阶段的 cosine 相似度阈值
  - `0`: 不过滤
  - `> 0`: 过滤掉相似度 < 该值的文档
  - 推荐值: 0.6-0.8

- **`rerank_threshold`**: Reranker 阶段的分数阈值
  - `0`: 不过滤
  - `> 0`: 过滤掉 reranker 分数 < 该值的文档
  - 推荐值: 0.5-0.7（注意：Reranker 分数范围通常与 cosine 相似度不同）

## 过滤策略

### 策略 1: 严格质量控制（两次过滤）

**配置:**
```yaml
similarity_threshold: 0.7-0.8
rerank_threshold: 0.5-0.7
```

**工作流程:**
1. 向量检索召回 `similarity_top_k` 个候选文档
2. 过滤掉 cos 相似度 < `similarity_threshold` 的文档
3. Reranker 对剩余文档重排
4. 过滤掉 Reranker 分数 < `rerank_threshold` 的文档
5. 返回前 `rerank_top_n` 个结果

**适用场景:**
- 宁缺毋滥，需要最高质量的检索结果
- 对准确性要求极高的场景

**注意事项:**
- 可能导致返回结果数量不足 `rerank_top_n`
- 两个阈值可以根��实际分数分布独立调整

### 策略 2: 充分利用 Reranker（推荐）

**配置:**
```yaml
similarity_threshold: 0.6-0.7      # 较宽松的阈值
rerank_threshold: 0.0               # 不过滤
```

**工作流程:**
1. 向量检索召回 `similarity_top_k` 个候选文档
2. 过滤掉 cos 相似度 < `similarity_threshold` 的文档
3. Reranker 对剩余文档重排
4. 直接返回前 `rerank_top_n` 个结果（不再过滤）

**适用场景:**
- 充分利用 Reranker 的重排能力
- 希望获得足够数量的高质量结果
- 平衡准确性和召回率

**优势:**
- 给 Reranker 足够的候选池进行精排
- 保证返回 `rerank_top_n` 个结果（如果候选池足够）

### 策略 3: 只信任 Reranker

**配置:**
```yaml
similarity_threshold: 0.0           # 不过滤
rerank_threshold: 0.5-0.7
```

**工作流程:**
1. 向量检索召回 `similarity_top_k` 个候选文档（不过滤）
2. Reranker 对所有文档重排
3. 过滤掉 Reranker 分数 < `rerank_threshold` 的文档
4. 返回剩余结果

**适用场景:**
- 完全信任 Reranker 的判断能力
- 向量相似度可能不准确的情况
- 需要最大召回 + Reranker 精选

### 策略 4: 最大召回（不过滤）

**配置:**
```yaml
similarity_threshold: 0.0
rerank_threshold: 0.0
```

**工作流程:**
1. 向量检索召回 `similarity_top_k` 个候选文档（不过滤）
2. Reranker 对所有文档重排
3. 返回前 `rerank_top_n` 个结果

**适用场景:**
- 探索性检索，需要最大召回
- 信任 Reranker 的重排能力
- 对相似度阈值不确定时

## 设计优势

相比使用单一阈值或布尔开关，使用**两个独立的数值阈值**有以下优势：

1. **更灵活**: 可以为两种不同的度量分数设置不同的阈值
2. **更合理**: cosine 相似度和 Reranker 分数的分布可能完全不同
3. **更简洁**: 0 表示禁用，> 0 表示启用并指定阈值，���义清晰
4. **更精确**: 可以根据实际数据分布独立调优两个阈值

## 代码实现

### 修改文件

1. **配置文件** (`src/tools/largerag/config/settings.yaml:37`)
   ```yaml
   rerank_threshold: 0.0  # 新增参数
   ```

2. **配置类** (`src/tools/largerag/config/settings.py:95`)
   ```python
   rerank_threshold: float  # Reranker 分数阈值（0 = 禁用）
   ```

3. **查询引擎** (`src/tools/largerag/core/query_engine.py`)
   - query() 方法的过滤逻辑 (第116-122行)
   - get_similar_documents() 方法的过滤逻辑 (第207-215行)

### 核心逻辑变化

**修改前** (使用相同阈值):
```python
# Reranker 之后使用 similarity_threshold 过滤
if self.settings.retrieval.similarity_threshold > 0:
    nodes = [n for n in nodes if n.score >= similarity_threshold]
```

**修改后** (使用独立阈值):
```python
# Reranker 之后使用 rerank_threshold 过滤
if self.settings.retrieval.rerank_threshold > 0:
    nodes = [n for n in nodes if n.score >= rerank_threshold]
```

## 测试验证

运行测试脚本查看当前配置:
```bash
python src/tools/largerag/examples/test_rerank_filter.py
```

输出示例:
```
检索配置:
  - similarity_top_k: 20
  - rerank_top_n: 10
  - similarity_threshold: 0.8
  - rerank_threshold: 0.0

过滤策略解释:
✓ 向量检索阶段: 过滤 cosine 相似度 < 0.8 的文档
✗ Reranker 阶段: 不过滤（rerank_threshold = 0）
=> 总计: 一次过滤（仅向量检索）
```

## 推荐配置

### 对于 DES 文献检索系统

考虑到需要平衡准确性和覆盖率，推荐使用**策略 2**:

```yaml
retrieval:
  similarity_top_k: 20
  rerank_top_n: 10
  similarity_threshold: 0.65       # 较宽松，给 Reranker 足够候选
  rerank_threshold: 0.0             # 不过滤，充分利用 Reranker 重排
```

**理由:**
- 向量检索阶段过滤掉明显不相关的文档
- Reranker 在足够大的候选池中精排，充分发挥其语义理解能力
- 保证返回 10 个高质量结果，适合 Agent 综合分析

### 其他可选配置

**如果发现结果质量不够高:**
```yaml
similarity_threshold: 0.7
rerank_threshold: 0.6    # 启用第二次过滤
```

**如果发现结果数量不足:**
```yaml
similarity_threshold: 0.6   # 降低阈值
rerank_threshold: 0.0
```

## 注意事项

1. **阈值设置**: Reranker 分数和 cosine 相似度的量纲可能不同，需要分别调优
2. **结果数量**: 如果两次过滤都很严格，可能导致实际返回数量 < `rerank_top_n`
3. **性能考虑**: Reranker API 调用有成本，`similarity_top_k` 不宜设置过大
4. **日志监控**: 注意查看日志中的 "Filtered X nodes" 信息，了解过滤效果
5. **分数分布**: 建议在实际数据上观察两种分数的分布，再设置合适的阈值

## 调试建议

### 查看分数分布

在 `get_similar_documents()` 返回前添加日志，观察实际分数：

```python
for node in nodes:
    logger.debug(f"Node score: {node.score}, content preview: {node.text[:100]}")
```

### 逐步调整阈值

1. 先设置 `similarity_threshold = 0.0, rerank_threshold = 0.0`，观察原始结果
2. 根据结果质量，逐步提高 `similarity_threshold`
3. 如果仍需进一步过滤，再调整 `rerank_threshold`

## 相关代码位置

- 配置文件: `src/tools/largerag/config/settings.yaml:37`
- 配置类: `src/tools/largerag/config/settings.py:95`
- query() 方法过滤: `src/tools/largerag/core/query_engine.py:116-122`
- get_similar_documents() 过滤: `src/tools/largerag/core/query_engine.py:207-215`
- 测试脚本: `src/tools/largerag/examples/test_rerank_filter.py`
