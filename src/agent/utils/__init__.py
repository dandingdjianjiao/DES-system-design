"""
Utility modules for DES Agent

Provides:
- LLMClient: OpenAI-compatible LLM client supporting DashScope and OpenAI
- EmbeddingClient: OpenAI-compatible embedding client supporting DashScope and OpenAI
"""

from .llm_client import LLMClient, create_llm_client_from_config
from .embedding_client import EmbeddingClient, create_embedding_client_from_config

__all__ = [
    "LLMClient",
    "EmbeddingClient",
    "create_llm_client_from_config",
    "create_embedding_client_from_config",
]
