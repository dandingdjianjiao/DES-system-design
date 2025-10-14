# ReasoningBank Framework Implementation Plan for DES System

**Date:** 2025-10-14
**Author:** System Design Team
**Reference:** [ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory](2509.25140v1.pdf)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [ReasoningBank Framework Overview](#reasoningbank-framework-overview)
3. [DES System Integration Design](#des-system-integration-design)
4. [Core Components Architecture](#core-components-architecture)
5. [Tool Integration Strategy](#tool-integration-strategy)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Testing & Validation Strategy](#testing--validation-strategy)
8. [Risks & Mitigation](#risks--mitigation)

---

## 1. Executive Summary

### Purpose
This document outlines the implementation plan for integrating the **ReasoningBank** framework as the core Reasoning Agent for the DES (Deep Eutectic Solvent) formulation prediction system, replacing the originally planned RL-based agent architecture.

### Key Decisions
- **Framework Choice**: Adopt ReasoningBank instead of pure RL-based approach
- **Rationale**:
  - Test-time learning without需要大量标注数据
  - 从成功和失败经验中学习，适合化学领域的知识积累
  - Memory-driven experience scaling更适合科学推理任务
  - 实现复杂度低于完整的PPO训练框架

### Expected Benefits
1. **Self-Evolving Capability**: Agent learns from each DES design task
2. **Knowledge Transfer**: Generalizable reasoning strategies across similar tasks
3. **Efficiency**: Reduces redundant exploration in formulation space
4. **Interpretability**: Memory items provide explainable design rationale

---

## 2. ReasoningBank Framework Overview

### 2.1 Core Concept

ReasoningBank is a **memory-augmented agent framework** that:
- Distills **generalizable reasoning strategies** from both successful and failed experiences
- Stores memory as structured **reasoning hints** (not raw trajectories)
- Enables **test-time learning** without ground-truth labels
- Scales through **memory-aware test-time scaling (MaTTS)**

### 2.2 Memory Schema

Each memory item consists of:
```python
{
    "title": str,        # Concise identifier of the strategy
    "description": str,  # One-sentence summary
    "content": str       # 1-5 sentences of distilled reasoning
}
```

### 2.3 Three-Stage Workflow

```
┌─────────────────────────────────────────────────────────┐
│                   Reasoning Agent                        │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  (1) Memory Retrieval                          │    │
│  │      - Query ReasoningBank with task           │    │
│  │      - Retrieve top-k relevant memory items    │    │
│  │      - Inject into agent's system prompt       │    │
│  └────────────────────────────────────────────────┘    │
│                         ↓                                 │
│  ┌────────────────────────────────────────────────┐    │
│  │  (2) Task Execution                            │    │
│  │      - Use CoreRAG for theoretical knowledge   │    │
│  │      - Use LargeRAG for literature facts       │    │
│  │      - Generate DES formulation candidates     │    │
│  └────────────────────────────────────────────────┘    │
│                         ↓                                 │
│  ┌────────────────────────────────────────────────┐    │
│  │  (3) Memory Extraction & Consolidation         │    │
│  │      - Evaluate outcome (success/failure)      │    │
│  │      - Extract reasoning strategies            │    │
│  │      - Add new memory items to ReasoningBank   │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 3. DES System Integration Design

### 3.1 Task Definition

**Input**: DES formulation task
```python
{
    "target_material": "cellulose",
    "target_temperature": -20,
    "constraints": {
        "viscosity": "<100 cP",
        "components": ["HBD", "HBA"]
    }
}
```

**Output**: DES formulation recommendation
```python
{
    "formulation": {
        "HBD": "Choline chloride",
        "HBA": "Urea",
        "molar_ratio": "1:2"
    },
    "reasoning": "...",
    "confidence": 0.85,
    "supporting_evidence": [...]
}
```

### 3.2 Success/Failure Criteria

#### Success Indicators
1. **Predicted solubility** ≥ target threshold
2. **Temperature feasibility** within ±5°C
3. **Chemical compatibility** verified
4. **Literature precedent** exists

#### Failure Indicators
1. Predicted solubility < threshold
2. Incompatible component combination
3. Unfeasible molar ratios
4. Contradicts established chemistry principles

### 3.3 Memory Content for DES Domain

**Example Memory Items**:

```markdown
# Memory Item 1
## Title: Prioritize Hydrogen Bond Network Analysis
## Description: When designing DES for polar materials, analyze H-bond strength first
## Content: For dissolving polar polymers like cellulose, the hydrogen bond donating/accepting capability of DES components is the primary factor. Use CoreRAG to retrieve H-bond parameters before exploring molar ratios. Components with strong H-bond networks (e.g., choline chloride + urea) generally outperform weak ones.

# Memory Item 2
## Title: Avoid Known Incompatible Pairs
## Description: Certain HBD-HBA combinations fail due to chemical incompatibility
## Content: If previous attempts showed that quaternary ammonium salts + acidic HBDs lead to decomposition, explicitly avoid such combinations. Check LargeRAG for reported incompatibilities before proposing new formulations.

# Memory Item 3
## Title: Temperature-Viscosity Trade-off Strategy
## Description: Low-temperature DES design requires balancing viscosity
## Content: At temperatures below -10°C, DES viscosity increases dramatically. When targeting low-temperature applications, prioritize components with lower molecular weight and weaker intermolecular forces. If initial candidates show high viscosity, consider adding small amounts of co-solvents (retrieve precedents from LargeRAG).
```

---

## 4. Core Components Architecture

### 4.1 Directory Structure

```
src/agent/
├── reasoningbank/
│   ├── __init__.py
│   ├── memory.py              # Memory item data structures
│   ├── memory_manager.py      # CRUD operations for memory bank
│   ├── retriever.py           # Embedding-based similarity search
│   ├── extractor.py           # Memory extraction from trajectories
│   ├── judge.py               # LLM-as-a-judge for success/failure
│   └── matts.py               # Memory-aware test-time scaling
│
├── des_agent.py               # Main DES formulation agent
├── config.py                  # Configuration settings
├── prompts/
│   ├── extraction_prompts.py  # Prompts for memory extraction
│   ├── judge_prompts.py       # Prompts for outcome evaluation
│   └── agent_prompts.py       # Agent system prompts
│
├── examples/
│   └── example_des_task.py    # Example usage
│
└── tests/
    ├── test_memory.py
    ├── test_extractor.py
    └── test_des_agent.py
```

### 4.2 Core Classes

#### 4.2.1 MemoryItem

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class MemoryItem:
    """A single reasoning strategy stored in ReasoningBank"""
    title: str
    description: str
    content: str
    source_task_id: Optional[str] = None
    is_from_success: bool = True
    created_at: str = None
    embedding: Optional[list] = None
```

#### 4.2.2 ReasoningBank

```python
class ReasoningBank:
    """
    Central memory storage and retrieval system
    """
    def __init__(self, embedding_model: str = "text-embedding-3-small"):
        self.memories: List[MemoryItem] = []
        self.embedding_model = embedding_model

    def add_memory(self, memory: MemoryItem) -> None:
        """Add a new memory item with embedding"""
        pass

    def retrieve(self, query: str, top_k: int = 3) -> List[MemoryItem]:
        """Retrieve top-k most relevant memories"""
        pass

    def consolidate(self, new_memories: List[MemoryItem]) -> None:
        """Consolidate new memories (currently simple append)"""
        pass

    def save(self, filepath: str) -> None:
        """Persist memory bank to disk"""
        pass

    def load(self, filepath: str) -> None:
        """Load memory bank from disk"""
        pass
```

#### 4.2.3 MemoryExtractor

```python
class MemoryExtractor:
    """
    Extracts reasoning strategies from agent trajectories
    """
    def __init__(self, llm_client, extraction_prompts):
        self.llm = llm_client
        self.prompts = extraction_prompts

    def extract_from_trajectory(
        self,
        task: dict,
        trajectory: List[dict],
        outcome: Literal["success", "failure"]
    ) -> List[MemoryItem]:
        """
        Extract up to 3 memory items from a single trajectory
        """
        pass
```

#### 4.2.4 DESAgent

```python
class DESAgent:
    """
    Main DES formulation design agent with ReasoningBank
    """
    def __init__(
        self,
        llm_client,
        reasoning_bank: ReasoningBank,
        corerag_client,
        largerag_client,
        config: dict
    ):
        self.llm = llm_client
        self.memory = reasoning_bank
        self.corerag = corerag_client
        self.largerag = largerag_client
        self.config = config

    def solve_task(self, task: dict) -> dict:
        """
        Main workflow:
        1. Retrieve relevant memories
        2. Query CoreRAG/LargeRAG
        3. Generate formulation
        4. Extract & consolidate memories
        """
        # (1) Memory Retrieval
        memories = self.memory.retrieve(task["description"], top_k=3)

        # (2) Tool Interaction
        theory = self.corerag.query(task)
        literature = self.largerag.query(task)

        # (3) Formulation Generation
        result = self._generate_formulation(task, memories, theory, literature)

        # (4) Memory Extraction
        outcome = self._evaluate_outcome(result, task)
        new_memories = self._extract_memories(task, result, outcome)
        self.memory.consolidate(new_memories)

        return result
```

---

## 5. Tool Integration Strategy

### 5.1 CoreRAG Integration

**Purpose**: Retrieve theoretical principles for DES design

**Query Pattern**:
```python
corerag_query = {
    "query": f"What are the key factors for dissolving {target_material} using DES?",
    "focus": ["hydrogen_bonding", "component_selection", "molar_ratio"]
}

# CoreRAG returns structured ontology knowledge
theory_response = corerag.query(corerag_query)
```

**Usage in Agent**:
- Memory items guide which ontology classes to query
- Theoretical principles validate proposed formulations

### 5.2 LargeRAG Integration

**Purpose**: Retrieve literature precedents and experimental conditions

**Query Pattern**:
```python
largerag_query = {
    "query": f"DES formulations for {target_material} at {target_temp}°C",
    "filters": {
        "material_type": "polymer",
        "temperature_range": [-30, -10]
    },
    "top_k": 10
}

# LargeRAG returns relevant literature snippets
literature_response = largerag.query(largerag_query)
```

**Usage in Agent**:
- Find similar successful cases
- Identify reported failures to avoid

### 5.3 Tool Call Sequence

```
Task Input
    ↓
Memory Retrieval
    ↓
┌──────────────────────────────┐
│  Memory guides tool selection │
└──────────────────────────────┘
    ↓
    ├──→ CoreRAG (if memory suggests theoretical gap)
    ├──→ LargeRAG (if memory suggests literature search)
    └──→ Both (default for complex tasks)
    ↓
Knowledge Synthesis
    ↓
Formulation Generation
    ↓
Outcome Evaluation
    ↓
Memory Extraction & Update
```

---

## 6. Implementation Roadmap

### Phase 1: Core Framework (Week 1-2)

**Deliverables**:
- [ ] `MemoryItem` dataclass
- [ ] `ReasoningBank` with basic CRUD operations
- [ ] Embedding-based retrieval using OpenAI embeddings
- [ ] JSON-based persistence

**Tasks**:
1. Implement `src/agent/reasoningbank/memory.py`
2. Implement `src/agent/reasoningbank/memory_manager.py`
3. Implement `src/agent/reasoningbank/retriever.py`
4. Write unit tests

**Acceptance Criteria**:
- Can add/retrieve/save/load memory items
- Retrieval returns semantically similar items
- Pass all unit tests

### Phase 2: Memory Extraction (Week 3)

**Deliverables**:
- [ ] LLM-as-a-judge for success/failure evaluation
- [ ] Memory extractor with prompts
- [ ] Domain-specific prompts for DES tasks

**Tasks**:
1. Design extraction prompts (successful trajectory)
2. Design extraction prompts (failed trajectory)
3. Implement `src/agent/reasoningbank/judge.py`
4. Implement `src/agent/reasoningbank/extractor.py`
5. Test with mock trajectories

**Acceptance Criteria**:
- Judge correctly classifies outcomes
- Extractor produces valid memory items
- Memory content is domain-appropriate

### Phase 3: DES Agent Integration (Week 4-5)

**Deliverables**:
- [ ] DESAgent class with ReasoningBank
- [ ] CoreRAG client wrapper
- [ ] LargeRAG client wrapper (placeholder initially)
- [ ] End-to-end workflow

**Tasks**:
1. Implement `src/agent/des_agent.py`
2. Create wrapper for CoreRAG query interface
3. Create placeholder for LargeRAG (mocked initially)
4. Implement agent's reasoning loop
5. Add memory injection into system prompts

**Acceptance Criteria**:
- Agent can solve a simple DES task
- Memory is correctly retrieved and used
- New memories are extracted and stored
- Integrates with CoreRAG successfully

### Phase 4: MaTTS Implementation (Week 6)

**Deliverables**:
- [ ] Parallel scaling implementation
- [ ] Sequential scaling implementation
- [ ] Self-contrast mechanism
- [ ] Best-of-N selection

**Tasks**:
1. Implement parallel trajectory generation
2. Implement self-contrast prompts
3. Implement sequential refinement
4. Add Best-of-N evaluation logic

**Acceptance Criteria**:
- Can generate multiple formulations for one task
- Self-contrast improves memory quality
- Sequential refinement works correctly

### Phase 5: Testing & Optimization (Week 7-8)

**Deliverables**:
- [ ] Comprehensive test suite
- [ ] Example tasks and expected outputs
- [ ] Performance benchmarks
- [ ] Documentation

**Tasks**:
1. Create 10+ diverse DES design tasks
2. Run agent and collect memory evolution data
3. Analyze memory quality and agent performance
4. Optimize prompts and retrieval parameters
5. Write usage documentation

**Acceptance Criteria**:
- Agent shows improvement over time
- Memory contains interpretable strategies
- Documentation is complete

---

## 7. Testing & Validation Strategy

### 7.1 Unit Tests

**Test Coverage**:
- `test_memory.py`: Memory item creation, serialization
- `test_retriever.py`: Embedding, similarity search
- `test_extractor.py`: Prompt formatting, extraction logic
- `test_judge.py`: Outcome evaluation accuracy

### 7.2 Integration Tests

**Scenarios**:
1. **Cold Start**: Agent with empty memory bank
2. **Warm Start**: Agent with 10 pre-seeded memories
3. **Cross-Task Transfer**: Test generalization across different materials

### 7.3 End-to-End Tests

**Test Tasks**:
```python
test_tasks = [
    {
        "id": "task_001",
        "target_material": "cellulose",
        "target_temperature": -20,
        "expected_hbd_category": "quaternary_ammonium"
    },
    {
        "id": "task_002",
        "target_material": "lignin",
        "target_temperature": 25,
        "expected_hba_category": "carboxylic_acid"
    },
    # ... more tasks
]
```

### 7.4 Memory Quality Metrics

**Metrics**:
1. **Diversity**: Number of unique memory titles
2. **Transfer Rate**: % of tasks where retrieved memory is helpful
3. **Precision**: % of extracted memories that are scientifically valid
4. **Coverage**: % of chemical concepts covered in memory bank

### 7.5 Agent Performance Metrics

**Metrics**:
1. **Success Rate**: % of tasks solved correctly
2. **Efficiency**: Average number of tool calls per task
3. **Improvement Over Time**: Success rate in first 10 vs last 10 tasks
4. **Explanation Quality**: Human evaluation of reasoning chains

---

## 8. Risks & Mitigation

### 8.1 Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Memory extraction quality | High | Medium | Iterative prompt engineering, human validation |
| CoreRAG API instability | Medium | Low | Add error handling, implement retry logic |
| LLM API costs | Medium | High | Use cost-effective models (GPT-4o-mini for extraction) |
| Embedding model changes | Low | Low | Abstract embedding interface for easy swapping |

### 8.2 Scientific Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| False positive memories | High | Medium | Add memory validation step, expert review |
| Overgeneralization | Medium | High | Use domain-specific constraints, literature validation |
| Bias from initial examples | Medium | Medium | Diverse training tasks, failure analysis |

### 8.3 Integration Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| CoreRAG query format mismatch | High | Low | Create adapter layer, version control |
| LargeRAG not ready | High | High | Use mock data, implement graceful degradation |
| ExpData tool delayed | Medium | High | Deprioritize, focus on CoreRAG + LargeRAG first |

---

## 9. Configuration

### 9.1 Model Configuration

```yaml
# config/reasoningbank_config.yaml

llm:
  provider: "openai"  # or "dashscope"
  model: "gpt-4o-mini"
  temperature: 0.7
  max_tokens: 2000

embedding:
  provider: "openai"
  model: "text-embedding-3-small"

memory:
  max_items: 1000
  retrieval_top_k: 3
  extraction_max_per_trajectory: 3
  persist_path: "data/memory/reasoningbank.json"

tools:
  corerag:
    endpoint: "src.tools.corerag"
    max_results: 5
  largerag:
    endpoint: "src.tools.largerag"
    max_results: 10

matts:
  enabled: false  # Enable after Phase 4
  parallel_k: 3
  sequential_steps: 2
```

### 9.2 Prompt Templates

Will be stored in `src/agent/prompts/` and loaded dynamically.

---

## 10. Success Criteria

### Minimum Viable Product (MVP)
- Agent can complete 10 diverse DES design tasks
- Memory bank accumulates >20 valid memory items
- At least 30% of tasks show memory utilization
- No critical bugs in core workflow

### Full Success
- Agent improves success rate by >15% after 50 tasks
- Memory transfer works across material categories
- MaTTS shows clear benefit in Pass@k metrics
- Human experts validate memory quality >80%

---

## 11. Next Steps

1. **Review & Approval**: Circulate this plan for feedback
2. **Environment Setup**: Configure API keys, dependencies
3. **Phase 1 Kickoff**: Begin core framework implementation
4. **Weekly Sync**: Track progress against roadmap

---

## Appendix A: Comparison with Original RL Plan

| Aspect | Original RL Approach | ReasoningBank Approach |
|--------|---------------------|------------------------|
| Training Data | Needs 50+ labeled experiments | No labeled data required |
| Learning Paradigm | Offline RL → Online RL | Test-time learning |
| Complexity | High (PPO, reward engineering) | Medium (prompt engineering) |
| Interpretability | Low (policy network) | High (memory items) |
| Cold Start | Poor without pre-training | Moderate (can seed memories) |
| Scalability | Requires retraining | Continuous accumulation |

**Recommendation**: Adopt ReasoningBank as **Phase 1 implementation**, revisit RL if needed in future.

---

## Appendix B: References

1. **ReasoningBank Paper**: Ouyang et al., "ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory", 2025
2. **DES Project CLAUDE.md**: `src/agent/ARCHITECTURE.md` (original RL design)
3. **CoreRAG Documentation**: `src/tools/corerag/README.md`
4. **LargeRAG Design**: `src/tools/largerag/README.md` (placeholder)

---

**Document Version**: 1.0
**Last Updated**: 2025-10-14
**Status**: Draft for Review
