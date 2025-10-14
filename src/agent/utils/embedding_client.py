"""
Embedding Client using OpenAI-compatible API

Supports:
- OpenAI Embeddings API
- DashScope (Aliyun) Embeddings API via OpenAI-compatible endpoint
- Any OpenAI-compatible embedding service
"""

import os
import logging
from typing import List, Optional, Dict, Any
from openai import OpenAI
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingClient:
    """
    Universal embedding client using OpenAI-compatible API.

    Supports multiple providers:
    - OpenAI (text-embedding-3-small, text-embedding-3-large)
    - DashScope/Aliyun (text-embedding-v3, etc.)
    - Custom OpenAI-compatible endpoints

    Attributes:
        client: OpenAI client instance
        model: Embedding model name
        dimension: Embedding dimension (if supported)
    """

    def __init__(
        self,
        provider: str = "dashscope",
        model: str = "text-embedding-v3",
        dimension: Optional[int] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize embedding client.

        Args:
            provider: "openai", "dashscope", or "custom"
            model: Model name
            dimension: Output dimension (if model supports it)
            api_key: API key (if None, read from env)
            base_url: Custom base URL
        """
        self.provider = provider
        self.model = model
        self.dimension = dimension

        # Determine API key and base URL
        if provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.base_url = base_url or "https://api.openai.com/v1"

        elif provider == "dashscope":
            self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
            self.base_url = base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1"

        else:  # custom
            self.api_key = api_key or os.getenv("EMBEDDING_API_KEY")
            if not base_url:
                raise ValueError("base_url is required for custom provider")
            self.base_url = base_url

        if not self.api_key:
            raise ValueError(
                f"API key not found for provider '{provider}'. "
                f"Set {provider.upper()}_API_KEY in environment or .env file."
            )

        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        logger.info(
            f"Initialized Embedding client: provider={provider}, model={model}, "
            f"dimension={dimension or 'default'}"
        )

    def embed(
        self,
        text: str,
        **kwargs
    ) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text
            **kwargs: Additional parameters

        Returns:
            Embedding vector as list of floats
        """
        return self.embed_batch([text], **kwargs)[0]

    def embed_batch(
        self,
        texts: List[str],
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of input texts
            **kwargs: Additional parameters

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        # Prepare parameters
        params = {
            "model": self.model,
            "input": texts,
            **kwargs
        }

        # Add dimension if specified and supported
        if self.dimension and self.provider == "openai":
            params["dimensions"] = self.dimension

        # Make API call
        try:
            response = self.client.embeddings.create(**params)

            # Extract embeddings
            embeddings = [item.embedding for item in response.data]

            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Embedding API call failed: {e}")
            raise

    def __call__(self, text: str, **kwargs) -> List[float]:
        """
        Shorthand for embed() method.

        Args:
            text: Input text
            **kwargs: Additional parameters

        Returns:
            Embedding vector
        """
        return self.embed(text, **kwargs)

    def cosine_similarity(
        self,
        vec1: List[float],
        vec2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity (0 to 1)
        """
        v1 = np.array(vec1)
        v2 = np.array(vec2)

        # Handle zero vectors
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Cosine similarity
        similarity = np.dot(v1, v2) / (norm1 * norm2)

        # Clamp to [0, 1]
        return max(0.0, min(1.0, float(similarity)))


def create_embedding_client_from_config(config: Dict[str, Any]) -> EmbeddingClient:
    """
    Create embedding client from configuration dictionary.

    Args:
        config: Configuration dict with keys:
            - provider: "openai" or "dashscope"
            - model: Model name
            - dimension (optional): Output dimension
            - api_key (optional): API key
            - base_url (optional): Custom base URL

    Returns:
        Configured EmbeddingClient instance
    """
    return EmbeddingClient(
        provider=config.get("provider", "dashscope"),
        model=config.get("model", "text-embedding-v3"),
        dimension=config.get("dimension"),
        api_key=config.get("api_key"),
        base_url=config.get("base_url")
    )


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Example 1: DashScope (Aliyun)
    try:
        client = EmbeddingClient(
            provider="dashscope",
            model="text-embedding-v3"
        )

        # Single text
        embedding = client.embed("Deep Eutectic Solvent")
        print(f"DashScope embedding dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")

        # Batch
        texts = [
            "Hydrogen bond donor",
            "Hydrogen bond acceptor",
            "Choline chloride"
        ]
        embeddings = client.embed_batch(texts)
        print(f"\nGenerated {len(embeddings)} embeddings")

        # Similarity
        sim = client.cosine_similarity(embeddings[0], embeddings[1])
        print(f"Similarity between HBD and HBA: {sim:.4f}")

    except Exception as e:
        print(f"Error: {e}")

    # Example 2: OpenAI
    try:
        client = EmbeddingClient(
            provider="openai",
            model="text-embedding-3-small",
            dimension=512  # Reduce dimension
        )

        embedding = client("Test embedding")
        print(f"\nOpenAI embedding dimension: {len(embedding)}")

    except Exception as e:
        print(f"Error: {e}")
