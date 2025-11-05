# aggregate_small_chunks 配置参数说明

## 概述

`aggregate_small_chunks` 是一个布尔型配置参数，控制在 token 和 sentence 分块模式下，是否将 JSON 文件内的多个片段聚合为一个Document对象。

## 配置位置

### settings.yaml

```yaml
document_processing:
  splitter_type: "token"                        # 分块策略: token / semantic / sentence
  chunk_size: 512                               # 分块大小（token）
  chunk_overlap: 50                             # 重叠大小（token）
  separator: "\n\n"                             # 分块分隔符

  # 小分块聚合配置（当 splitter_type=token 或 sentence 时生效）
  aggregate_small_chunks: false                 # 是否聚合小于 chunk_size 的 JSON 分块
                                                 # true: 多个小分块会被合并为一个 chunk（直到达到 chunk_size）
                                                 # false: 保持现有逻辑（只有大分块才会被继续分割）
```

## 行为模式详解

### 不聚合模式（aggregate_small_chunks: false）- 默认行为

**特点：保留 JSON 原始分块点**

- JSON 文件中的每个 text 条目 → 创建一个独立的 Document 对象
- 小于 chunk_size 的 Document 保持不变
- 大于 chunk_size 的 Document 会被 Splitter 分割

**示例：**
```
JSON 文件 (content_list_process.json):
├── text[0]: "Deep eutectic solvents are..." (150 tokens)
├── text[1]: "They have lower melting..." (80 tokens)
├── text[2]: "DES are used in..." (120 tokens)
└── ...

↓ DocumentProcessor处理（不聚合）

生成 Documents:
├── Doc[0]: text[0] (150 tokens)
├── Doc[1]: text[1] (80 tokens)
├── Doc[2]: text[2] (120 tokens)
└── ...

↓ Splitter处理（chunk_size=512）

最终 Nodes:
├── Node[0]: Doc[0] (150 tokens) - 未分割
├── Node[1]: Doc[1] (80 tokens) - 未分割
├── Node[2]: Doc[2] (120 tokens) - 未分割
└── ...
```

**测试结果：**
```
不聚合模式: 76 个text条目 → 76 个Documents → 76+ 个Nodes
```

### 聚合模式（aggregate_small_chunks: true）

**特点：消除 JSON 分块点，按文件聚合**

- 一个 JSON 文件的所有 text 条目 → 合并为一个 Document 对象
- 使用 separator（默认 `\n\n`）连接各个片段
- Splitter 会统一重新分块（不受原 JSON 结构限制）

**示例：**
```
JSON 文件 (content_list_process.json):
├── text[0]: "Deep eutectic solvents are..." (150 tokens)
├── text[1]: "They have lower melting..." (80 tokens)
├── text[2]: "DES are used in..." (120 tokens)
└── ...

↓ DocumentProcessor处理（聚合）

生成 Documents:
└── Doc[0]: text[0] + "\n\n" + text[1] + "\n\n" + text[2] + ... (3500 tokens)

↓ Splitter处理（chunk_size=512, overlap=50）

最终 Nodes:
├── Node[0]: Doc[0][0:512] - 重新分块
├── Node[1]: Doc[0][462:974] - 带重叠
├── Node[2]: Doc[0][924:1436] - 带重叠
└── ...
```

**测试结果：**
```
聚合模式: 76 个text条目 → 1 个Document → 7-10 个Nodes（根据chunk_size）
```

## 适用场景

### 使用不聚合模式（aggregate_small_chunks: false）的场景

✅ **需要保留文档原始结构**
- 每个段落/章节需要独立检索
- 元数据（page_idx, text_level）对检索很重要
- 希望保持文献的逻辑分段

✅ **JSON 分块质量高**
- 预处理已���做了合理的段落划分
- 每个 text 条目是完整的语义单元

✅ **检索粒度要求细**
- 希望精确定位到具体段落
- 需要返回原始文献的段落级引用

### 使用聚合模式（aggregate_small_chunks: true）的场景

✅ **希望统一重新分块**
- 不关心 JSON 的原始分块方式
- 希望按照统一的 chunk_size 标准重新划分

✅ **JSON 分块过于碎片化**
- 每个 text 条目很短（<100 tokens）
- 希望合并成更大的语义块

✅ **最大化上下文连贯性**
- 需要跨段落的上下文信息
- 避免重要信息被 JSON 分块点切断

✅ **优化索引大小**
- 减少 Node 数量，降低存储和检索开销
- 每个 Node 包含更多上下文信息

## 性能影响

### 索引大小

| 模式 | Documents | Nodes | 索引大小 |
|------|-----------|-------|----------|
| 不聚合 | 多（~76/文件） | 多 | 较大 |
| 聚合 | 少（1/文件） | 少 | 较小 |

### 检索质量

| 维度 | 不聚合模式 | 聚合模式 |
|------|-----------|----------|
| 精确性 | ⭐⭐⭐⭐ 精确到段落 | ⭐⭐⭐ 精确到chunk |
| 上下文 | ⭐⭐⭐ 段落内上下文 | ⭐⭐⭐⭐ 跨段落上下文 |
| 召回�� | ⭐⭐⭐⭐ 段落级召回 | ⭐⭐⭐ chunk级召回 |
| 元数据 | ⭐⭐⭐⭐ 保留详细元数据 | ⭐⭐⭐ 部分元数据丢失 |

## 与 splitter_type 的交互

### token / sentence 模式

- ✅ **aggregate_small_chunks 对两种模式都有效**
- 聚合发生在 DocumentProcessor 阶段（加载时）
- Splitter 根据 chunk_size 和 chunk_overlap 进一步处理
- **影响**：主要影响chunk大小的均匀性和是否保留原始文档结构

### semantic 模式（语义分割）

- ✅ **aggregate_small_chunks 对语义模式特别重要**
- **不聚合的问���**：
  - 每个JSON片段单独做语义分割
  - ❌ 无法识别**跨JSON片段**的语义连续性
  - 例如：两个JSON片段讨论同一话题，但因为是独立的Document，SemanticSplitter无法发现它们语义相关
- **聚合的优势**：
  - ✅ 整个文档一起做语义分割
  - ✅ 算法可以看到完整文档，正确识别整体的语义边界
  - ✅ 避免人为的JSON分块点干扰语义相似度计算
- **推荐**：semantic模式下建议启用聚合（aggregate_small_chunks: true）

## 元数据差异

### 不聚合模式的元数据

```python
{
    "doc_hash": "08e506adb...",
    "page_idx": 0,
    "text_level": 1,
    "has_citations": True,
    "source_file": "content_list_process.json",
    "item_idx": 5,
    "aggregated": False
}
```

### 聚合模式的元数据

```python
{
    "doc_hash": "08e506adb...",
    "source_file": "content_list_process.json",
    "aggregated": True,
    "num_segments": 76,
    "page_idx_range": "0-15"
}
```

## 使用建议

### 推荐配置

**场景1：追求检索精确性和可解释性**
```yaml
document_processing:
  splitter_type: "token"
  chunk_size: 512
  chunk_overlap: 50
  aggregate_small_chunks: false  # 保留文档结构
```

**场景2：追求上下文完整性和检索效率**
```yaml
document_processing:
  splitter_type: "token"
  chunk_size: 1024  # 更大的chunk_size配合聚合
  chunk_overlap: 100
  aggregate_small_chunks: true  # 统一重新分块
```

**场景3：语义分割（推荐聚合）**
```yaml
document_processing:
  splitter_type: "semantic"
  semantic_breakpoint_threshold: 0.5
  aggregate_small_chunks: true  # 让语义分割算法看到完整文档
```
> 注意：语义模式下，聚合可以避免JSON分块点干扰语义边界识别，推荐启用

### 实验性调优

1. **对比测试**：使用相同的查询，对比两种模式的检索效果
2. **查看日志**：观察 Node 数量和分布
3. **评估召回**：检查是否有重要信息被分块点切断
4. **调整 chunk_size**：聚合模式通常需要更大的 chunk_size（768-1024）

## 测试方法

```bash
# 运行聚合功能测试
cd src/tools/largerag
python examples/test_aggregation_correct.py
```

## 相关文件

- **配置文件**：`src/tools/largerag/config/settings.yaml`
- **配置类**：`src/tools/largerag/config/settings.py:DocumentProcessingConfig`
- **实现代码**：`src/tools/largerag/core/document_processor.py`
- **测试脚本**：`src/tools/largerag/examples/test_aggregation_correct.py`

## 常见问题

### Q1: 聚合后如何保留原始的 page_idx 信息？

A: 聚合模式会保存 `page_idx_range`（如 "0-15"），但会丢失单个段落的精确页码。如果需要精确页码，建议使用不聚合模式。

### Q2: 聚合模式下 chunk_size 如何选择？

A: 建议使用更大的 chunk_size（768-1024），以充分利用聚合后的大Document。小 chunk_size（256-512）可能导致过多的分割。

### Q3: 可以只对某些文件聚合吗？

A: 当前不支持。aggregate_small_chunks 是全局配置。如需此功能，可以在代码中为不同文件夹使用不同的 DocumentProcessor 实例。

### Q4: 聚合会影响 embedding 缓存吗？

A: 会。聚合改变了 Document 的文本内容，因此会生成不同的 embedding。首次使用聚合模式时需要重新计算 embedding。

### Q5: 性能影响有多大？

A:
- **索引构建**：聚合模式稍快（Document数量减少）
- **检索速度**：相似（取决于最终Node数量）
- **存储空间**：聚合模式略小（减少元数据开销）

## 版本历史

- **2025-11-05**: 初始实现，支持 token 和 sentence 模式
- 参数名称：aggregate_small_chunks
- 默认值：false（保持向后兼容）
