"""
Memory Retriever for ReasoningBank

This module implements embedding-based similarity search for retrieving
relevant memory items from the ReasoningBank.
"""

from typing import List, Tuple, Optional, Callable
import numpy as np
import logging

from .memory import MemoryItem, MemoryQuery
from .memory_manager import ReasoningBank

logger = logging.getLogger(__name__)


class MemoryRetriever:
    """
    Retrieves relevant memories from ReasoningBank using embedding-based similarity search.

    The retriever supports:
    - Cosine similarity search
    - Filtering by metadata
    - Minimum similarity thresholds
    - Configurable top-k retrieval

    Attributes:
        bank: ReasoningBank instance to retrieve from
        embedding_func: Function to compute query embeddings
    """

    def __init__(
        self,
        bank: ReasoningBank,
        embedding_func: Callable[[str], List[float]]
    ):
        """
        Initialize MemoryRetriever.

        Args:
            bank: ReasoningBank instance
            embedding_func: Function that takes text and returns embedding vector
        """
        self.bank = bank
        self.embedding_func = embedding_func
        logger.info("Initialized MemoryRetriever")

    def retrieve(self, query: MemoryQuery) -> List[MemoryItem]:
        """
        Retrieve top-k most relevant memories for a query.

        Args:
            query: MemoryQuery object specifying search criteria

        Returns:
            List of MemoryItem objects, ranked by relevance
        """
        # Get candidate memories (apply filters first)
        candidates = self._get_candidates(query.filters)

        if not candidates:
            logger.warning("No candidate memories found after filtering")
            return []

        # Compute query embedding
        try:
            query_embedding = self.embedding_func(query.query_text)
        except Exception as e:
            logger.error(f"Failed to compute query embedding: {e}")
            return []

        # Compute similarities
        scored_memories = self._score_memories(query_embedding, candidates)

        # Filter by minimum similarity
        if query.min_similarity > 0:
            scored_memories = [
                (mem, score) for mem, score in scored_memories
                if score >= query.min_similarity
            ]

        # Sort by score (descending) and return top-k
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        top_k_memories = [mem for mem, score in scored_memories[:query.top_k]]

        logger.info(
            f"Retrieved {len(top_k_memories)} memories for query "
            f"(candidates: {len(candidates)})"
        )

        return top_k_memories

    def retrieve_with_scores(
        self,
        query: MemoryQuery
    ) -> List[Tuple[MemoryItem, float]]:
        """
        Retrieve memories with their similarity scores.

        Args:
            query: MemoryQuery object

        Returns:
            List of (MemoryItem, score) tuples, ranked by relevance
        """
        candidates = self._get_candidates(query.filters)

        if not candidates:
            return []

        try:
            query_embedding = self.embedding_func(query.query_text)
        except Exception as e:
            logger.error(f"Failed to compute query embedding: {e}")
            return []

        scored_memories = self._score_memories(query_embedding, candidates)

        # Filter by minimum similarity
        if query.min_similarity > 0:
            scored_memories = [
                (mem, score) for mem, score in scored_memories
                if score >= query.min_similarity
            ]

        # Sort by score
        scored_memories.sort(key=lambda x: x[1], reverse=True)

        return scored_memories[:query.top_k]

    def _get_candidates(self, filters: dict) -> List[MemoryItem]:
        """
        Get candidate memories by applying filters.

        Args:
            filters: Dictionary of filter criteria

        Returns:
            List of candidate MemoryItem objects
        """
        if not filters:
            return self.bank.get_all_memories()

        return self.bank.filter_memories(filters)

    def _score_memories(
        self,
        query_embedding: List[float],
        candidates: List[MemoryItem]
    ) -> List[Tuple[MemoryItem, float]]:
        """
        Compute similarity scores for candidate memories.

        Args:
            query_embedding: Query embedding vector
            candidates: List of candidate MemoryItem objects

        Returns:
            List of (MemoryItem, score) tuples
        """
        scored = []
        query_vec = np.array(query_embedding)

        for memory in candidates:
            if memory.embedding is None:
                logger.warning(f"Memory '{memory.title}' has no embedding, skipping")
                continue

            memory_vec = np.array(memory.embedding)
            similarity = self._cosine_similarity(query_vec, memory_vec)
            scored.append((memory, float(similarity)))

        return scored

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score (0 to 1)
        """
        # Handle zero vectors
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Cosine similarity
        similarity = np.dot(vec1, vec2) / (norm1 * norm2)

        # Clamp to [0, 1] (sometimes numerical issues cause slight overflow)
        return max(0.0, min(1.0, similarity))


def format_memories_for_prompt(memories: List[MemoryItem]) -> str:
    """
    Format retrieved memories for injection into agent's system prompt.

    Args:
        memories: List of MemoryItem objects to format

    Returns:
        Formatted string suitable for LLM context
    """
    if not memories:
        return ""

    formatted = "## Relevant Past Experiences\n\n"
    formatted += (
        "Below are some insights from previous DES design tasks that may be helpful:\n\n"
    )

    for i, memory in enumerate(memories, 1):
        formatted += f"### Experience {i}: {memory.title}\n"
        formatted += f"{memory.content}\n\n"

    formatted += (
        "You may use these experiences to guide your reasoning, but adapt them to "
        "the current task as needed. Do not blindly copy strategies if they don't apply.\n"
    )

    return formatted


# Example usage
if __name__ == "__main__":
    import hashlib

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Mock embedding function
    def mock_embedding(text: str) -> List[float]:
        # Simple mock using text hash
        hash_val = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return [(hash_val >> i) % 100 / 100.0 for i in range(128)]

    # Create bank and add sample memories
    bank = ReasoningBank(embedding_func=mock_embedding)

    memories = [
        MemoryItem(
            title="Prioritize H-Bond Analysis",
            description="Analyze hydrogen bonding for polar materials",
            content="For polar polymers like cellulose, H-bond strength is key.",
            metadata={"domain": "polar_polymers"}
        ),
        MemoryItem(
            title="Check Viscosity at Low Temperature",
            description="DES viscosity increases at low temperatures",
            content="For sub-zero applications, prefer low molecular weight components.",
            metadata={"domain": "low_temperature"}
        ),
        MemoryItem(
            title="Avoid Acidic HBD with Quaternary Ammonium",
            description="This combination causes decomposition",
            content="Strong acids + quaternary ammonium salts can decompose.",
            is_from_success=False,
            metadata={"domain": "compatibility"}
        ),
    ]

    for mem in memories:
        bank.add_memory(mem, compute_embedding=True)

    # Create retriever
    retriever = MemoryRetriever(bank, embedding_func=mock_embedding)

    # Test retrieval
    query = MemoryQuery(
        query_text="Design DES for dissolving cellulose at room temperature",
        top_k=2,
        min_similarity=0.0
    )

    retrieved = retriever.retrieve_with_scores(query)

    print(f"\nQuery: {query.query_text}")
    print(f"\nRetrieved {len(retrieved)} memories:\n")

    for memory, score in retrieved:
        print(f"[Score: {score:.3f}] {memory.title}")
        print(f"  {memory.description}")
        print()

    # Test prompt formatting
    prompt = format_memories_for_prompt([mem for mem, _ in retrieved])
    print("="*60)
    print("FORMATTED FOR PROMPT:")
    print("="*60)
    print(prompt)
