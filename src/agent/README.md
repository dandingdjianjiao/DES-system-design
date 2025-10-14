# ReasoningBank for DES Formulation Design

**Status:** ✅ Phase 1-3 Implemented (Core Framework + Agent Integration)

This directory contains the implementation of **ReasoningBank**, a memory-augmented agent framework for Deep Eutectic Solvent (DES) formulation design. The system learns from past experiences to continuously improve its design strategies.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Components](#components)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Development Roadmap](#development-roadmap)

---

## 🎯 Overview

ReasoningBank is inspired by the paper ["ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory"](2509.25140v1.pdf) and adapted for DES formulation design.

### Key Features

- **Memory-Driven Learning**: Extracts generalizable reasoning strategies from successful and failed attempts
- **Test-Time Learning**: No labeled data required; learns from self-judged outcomes
- **Tool Integration**: Combines CoreRAG (theory), LargeRAG (literature), and experimental data
- **Continuous Improvement**: Agent becomes more capable over time

### Design Philosophy

Unlike traditional RL approaches that require extensive training data, ReasoningBank:
- ✅ Works with **zero labeled examples** (test-time learning)
- ✅ Learns from **both successes and failures**
- ✅ Stores **reasoning strategies**, not raw trajectories
- ✅ Provides **interpretable** memory items

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     DES Agent                            │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  (1) Memory Retrieval                          │    │
│  │      - Query ReasoningBank                     │    │
│  │      - Retrieve top-k relevant strategies      │    │
│  └────────────────────────────────────────────────┘    │
│                         ↓                                 │
│  ┌────────────────────────────────────────────────┐    │
│  │  (2) Tool Interaction                          │    │
│  │      - CoreRAG: Theoretical principles         │    │
│  │      - LargeRAG: Literature precedents         │    │
│  └────────────────────────────────────────────────┘    │
│                         ↓                                 │
│  ┌────────────────────────────────────────────────┐    │
│  │  (3) Formulation Generation                    │    │
│  │      - Synthesize knowledge                    │    │
│  │      - Propose DES formulation                 │    │
│  └────────────────────────────────────────────────┘    │
│                         ↓                                 │
│  ┌────────────────────────────────────────────────┐    │
│  │  (4) Outcome Evaluation (LLM-as-a-Judge)       │    │
│  │      - Evaluate success/failure                │    │
│  └────────────────────────────────────────────────┘    │
│                         ↓                                 │
│  ┌────────────────────────────────────────────────┐    │
│  │  (5) Memory Extraction & Consolidation         │    │
│  │      - Extract reasoning strategies            │    │
│  │      - Update ReasoningBank                    │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.9+
pip install pyyaml numpy

# Optional: For actual LLM integration
pip install openai  # or dashscope for Aliyun
```

### Basic Usage

```python
from agent.reasoningbank import ReasoningBank, MemoryRetriever, MemoryExtractor, LLMJudge
from agent.des_agent import DESAgent

# 1. Initialize components
bank = ReasoningBank(embedding_func=your_embedding_func)
retriever = MemoryRetriever(bank, embedding_func=your_embedding_func)
extractor = MemoryExtractor(llm_client=your_llm_client)
judge = LLMJudge(llm_client=your_llm_client)

# 2. Create agent
agent = DESAgent(
    llm_client=your_llm_client,
    reasoning_bank=bank,
    retriever=retriever,
    extractor=extractor,
    judge=judge,
    corerag_client=your_corerag,
    largerag_client=your_largerag
)

# 3. Solve a task
task = {
    "task_id": "task_001",
    "description": "Design DES for dissolving cellulose at 25°C",
    "target_material": "cellulose",
    "target_temperature": 25,
    "constraints": {"viscosity": "< 500 cP"}
}

result = agent.solve_task(task)
print(result["formulation"])
```

### Run Example

```bash
cd src/agent/examples
python example_des_task.py
```

---

## 📦 Components

### 1. `reasoningbank/` - Core Memory System

#### `memory.py`
Data structures for memory items and trajectories:
- **`MemoryItem`**: Structured reasoning strategy (title, description, content)
- **`Trajectory`**: Agent's interaction history for one task
- **`MemoryQuery`**: Query specification for retrieval

#### `memory_manager.py`
**`ReasoningBank`** - Central memory storage:
- Add/remove/filter memories
- Automatic capacity management
- JSON persistence
- Statistics tracking

#### `retriever.py`
**`MemoryRetriever`** - Semantic search:
- Embedding-based similarity (cosine)
- Metadata filtering
- Top-k retrieval with thresholds

#### `extractor.py`
**`MemoryExtractor`** - Strategy extraction:
- Extract from successful trajectories
- Learn from failed trajectories
- Parallel extraction (MaTTS support)

#### `judge.py`
**`LLMJudge`** - Outcome evaluation:
- LLM-based success/failure classification
- No ground-truth labels required
- Provides reasoning for decisions

### 2. `des_agent.py` - Main Agent

**`DESAgent`** orchestrates the entire workflow:
- Retrieves relevant memories
- Queries CoreRAG and LargeRAG
- Generates DES formulations
- Evaluates outcomes
- Extracts and consolidates new memories

### 3. `prompts/` - LLM Prompts

Carefully designed prompts for:
- Memory extraction (success/failure)
- Outcome judging
- Parallel extraction (MaTTS)

### 4. `config/` - Configuration

**`reasoningbank_config.yaml`**:
- LLM settings (model, temperature, etc.)
- Memory parameters (max_items, top_k, etc.)
- Tool configurations
- MaTTS settings (for future)

---

## ⚙️ Configuration

Edit `config/reasoningbank_config.yaml`:

```yaml
# LLM Configuration
llm:
  provider: "openai"
  model: "gpt-4o-mini"
  temperature: 0.7

# Memory Configuration
memory:
  max_items: 1000
  retrieval_top_k: 3
  persist_path: "data/memory/des_reasoningbank.json"
  auto_save: true

# Tool Integration
tools:
  corerag:
    enabled: true
  largerag:
    enabled: true
```

**Environment Variables:**

```bash
# Set OpenAI API key
export OPENAI_API_KEY="your_key_here"

# Or for Aliyun DashScope
export DASHSCOPE_API_KEY="your_key_here"
```

---

## 📚 Usage Examples

### Example 1: Solve a Single Task

```python
task = {
    "task_id": "task_cellulose_25C",
    "description": "Design DES to dissolve 5% cellulose at 25°C",
    "target_material": "cellulose",
    "target_temperature": 25,
    "constraints": {
        "viscosity": "< 500 cP",
        "toxicity": "low"
    }
}

result = agent.solve_task(task)

# Access results
print(f"Status: {result['status']}")
print(f"HBD: {result['formulation']['HBD']}")
print(f"HBA: {result['formulation']['HBA']}")
print(f"Molar Ratio: {result['formulation']['molar_ratio']}")
print(f"Reasoning: {result['reasoning']}")
print(f"Confidence: {result['confidence']}")
```

### Example 2: Batch Processing

```python
tasks = [
    {...},  # Task 1
    {...},  # Task 2
    {...},  # Task 3
]

for task in tasks:
    result = agent.solve_task(task)
    # Agent learns from each task automatically
    print(f"{task['task_id']}: {result['status']}")

# View memory growth
stats = agent.memory.get_statistics()
print(f"Total memories: {stats['total_memories']}")
```

### Example 3: Inspect Memory

```python
# Get all memories
memories = agent.memory.get_all_memories()

for mem in memories:
    print(mem.to_detailed_string())

# Filter by criteria
success_memories = agent.memory.filter_memories({"is_from_success": True})
cellulose_memories = agent.memory.filter_memories({"metadata.target_material": "cellulose"})
```

### Example 4: Save/Load Memory Bank

```python
# Save after session
agent.memory.save("data/memory/session_2025_10_14.json")

# Load for next session
new_agent = ...  # Initialize new agent
new_agent.memory.load("data/memory/session_2025_10_14.json")
```

---

## 🧪 Testing

### Run Unit Tests

```bash
cd src/agent/tests
python -m pytest test_reasoningbank.py -v
```

### Test Coverage

- ✅ MemoryItem creation and validation
- ✅ ReasoningBank CRUD operations
- ✅ Memory persistence (save/load)
- ✅ Retrieval with filtering
- ✅ Trajectory serialization

### Manual Testing

```bash
# Run example with mock LLM
python examples/example_des_task.py

# Expected output: 3 tasks solved, ~6-9 memories extracted
```

---

## 🗺️ Development Roadmap

### ✅ Phase 1: Core Framework (COMPLETED)
- [x] MemoryItem, ReasoningBank, MemoryRetriever
- [x] JSON persistence
- [x] Embedding-based retrieval

### ✅ Phase 2: Memory Extraction (COMPLETED)
- [x] LLMJudge for success/failure
- [x] MemoryExtractor with prompts
- [x] Domain-specific DES prompts

### ✅ Phase 3: Agent Integration (COMPLETED)
- [x] DESAgent with full workflow
- [x] CoreRAG/LargeRAG integration stubs
- [x] Configuration system
- [x] Example usage script

### 🚧 Phase 4: MaTTS (Next Steps)
- [ ] Parallel scaling implementation
- [ ] Sequential refinement
- [ ] Self-contrast extraction
- [ ] Best-of-N selection

### 📋 Phase 5: Production (Future)
- [ ] Real CoreRAG integration
- [ ] LargeRAG vector DB setup
- [ ] Experimental data tool
- [ ] Performance optimization
- [ ] Comprehensive evaluation

---

## 📖 Documentation

### Key Documents

1. **[Implementation Plan](REASONINGBANK_IMPLEMENTATION_PLAN.md)** - Detailed design document
2. **[Original Paper](2509.25140v1.pdf)** - ReasoningBank research paper
3. **[Project CLAUDE.md](../../CLAUDE.md)** - Overall system architecture

### API Reference

See inline docstrings in each module:
- `reasoningbank/memory.py` - Data structures
- `reasoningbank/memory_manager.py` - ReasoningBank class
- `reasoningbank/retriever.py` - MemoryRetriever class
- `reasoningbank/extractor.py` - MemoryExtractor class
- `reasoningbank/judge.py` - LLMJudge class
- `des_agent.py` - DESAgent class

---

## 🤝 Integration with DES System

### CoreRAG Integration

```python
# CoreRAG client should implement:
class CoreRAGClient:
    def query(self, query_dict) -> dict:
        """
        Query ontology for theoretical knowledge

        Args:
            query_dict: {"query": str, "focus": List[str]}

        Returns:
            dict with theory, key_factors, recommendations
        """
        pass
```

### LargeRAG Integration

```python
# LargeRAG client should implement:
class LargeRAGClient:
    def query(self, query_dict) -> dict:
        """
        Query literature database

        Args:
            query_dict: {
                "query": str,
                "filters": dict,
                "top_k": int
            }

        Returns:
            dict with papers, common_formulations
        """
        pass
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"
```bash
# Ensure you're in the correct directory
cd src/agent
export PYTHONPATH="${PYTHONPATH}:$(pwd)/../.."
```

### Issue: "Embedding computation fails"
- Check that your embedding function returns List[float]
- Ensure vector dimensions are consistent

### Issue: "Memory not persisting"
- Check write permissions for `data/memory/` directory
- Verify `auto_save` is enabled in config

---

## 📄 License

Part of the DES-system-design project.

---

## 🙏 Acknowledgments

- **ReasoningBank Paper**: Ouyang et al., "ReasoningBank: Scaling Agent Self-Evolving with Reasoning Memory", 2025
- **DES Project**: CoreRAG ontology-based RAG system
- **Framework**: LangChain, LlamaIndex inspiration

---

**Last Updated:** 2025-10-14
**Version:** 0.1.0
**Status:** Phase 1-3 Complete, Ready for Integration Testing
