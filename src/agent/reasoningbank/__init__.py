"""
ReasoningBank: Memory-Augmented Agent Framework for DES Formulation Design

This package implements the ReasoningBank framework for storing and retrieving
reasoning strategies to guide DES (Deep Eutectic Solvent) formulation design.

Key Components:
- MemoryItem: Data structure for storing reasoning strategies
- ReasoningBank: Central memory management system
- MemoryRetriever: Embedding-based similarity search
- MemoryExtractor: Extract memories from trajectories
- LLMJudge: Evaluate trajectory outcomes
"""

from .memory import MemoryItem, MemoryQuery, Trajectory
from .memory_manager import ReasoningBank
from .retriever import MemoryRetriever, format_memories_for_prompt
from .extractor import MemoryExtractor
from .judge import LLMJudge

__version__ = "0.1.0"

__all__ = [
    "MemoryItem",
    "MemoryQuery",
    "Trajectory",
    "ReasoningBank",
    "MemoryRetriever",
    "MemoryExtractor",
    "LLMJudge",
    "format_memories_for_prompt",
]
