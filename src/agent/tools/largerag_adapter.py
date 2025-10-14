"""
LargeRAG Adapter for DESAgent

This module adapts the LargeRAG interface to match what DESAgent expects.

Implements: DESToolProtocol
    - query(query_dict) -> Optional[Dict]
    - get_status() -> Dict

DESAgent expects:
    largerag_client.query(query_dict) -> Dict
    where query_dict contains: query, filters, top_k

LargeRAG provides:
    largerag.get_similar_docs(query_text, top_k) -> List[Dict]

This adapter bridges the gap and follows the standard tool interface.
"""

from typing import Dict, Optional, Any
import logging
import sys
from pathlib import Path

# Add largerag to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from largerag import LargeRAG

logger = logging.getLogger(__name__)


class LargeRAGAdapter:
    """
    Adapter class to make LargeRAG compatible with DESAgent interface.

    Usage:
        from agent.tools.largerag_adapter import LargeRAGAdapter

        # Initialize adapter
        largerag_client = LargeRAGAdapter()

        # Use in DESAgent
        agent = DESAgent(
            ...,
            largerag_client=largerag_client,
            ...
        )
    """

    def __init__(self):
        """
        Initialize LargeRAG adapter.

        Automatically loads existing index if available.
        If no index exists, will log a warning.
        """
        try:
            self.rag = LargeRAG()

            if self.rag.query_engine is None:
                logger.warning(
                    "LargeRAG index not loaded. "
                    "Please build index first: "
                    "python src/tools/largerag/examples/1_build_index.py"
                )
            else:
                logger.info("LargeRAG adapter initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize LargeRAG: {e}")
            self.rag = None

    def query(self, query_dict: Dict[str, Any]) -> Optional[Dict]:
        """
        Query LargeRAG for literature information.

        Args:
            query_dict: Query parameters with keys:
                - query (str): Query text
                - top_k (int, optional): Number of documents to retrieve (default: 5)
                - filters (dict, optional): Metadata filters (not yet implemented)

        Returns:
            Dict containing:
                - documents: List of retrieved documents
                - num_results: Number of documents found
                - query: Original query text

            Returns None if RAG is not initialized or query fails.

        Example:
            query_dict = {
                "query": "DES formulations for cellulose at 25°C",
                "top_k": 10,
                "filters": {"material_type": "polymer"}
            }
            result = adapter.query(query_dict)
        """
        if self.rag is None or self.rag.query_engine is None:
            logger.error("LargeRAG not initialized. Cannot query.")
            return None

        try:
            # Extract parameters
            query_text = query_dict.get("query", "")
            top_k = query_dict.get("top_k", 5)
            filters = query_dict.get("filters", {})

            if not query_text:
                logger.warning("Empty query text provided")
                return None

            # TODO: Implement filter support in LargeRAG
            if filters:
                logger.debug(f"Filters provided but not yet implemented: {filters}")

            # Query LargeRAG
            logger.debug(f"Querying LargeRAG: '{query_text}' (top_k={top_k})")
            documents = self.rag.get_similar_docs(query_text, top_k=top_k)

            # Format result for DESAgent
            result = {
                "documents": documents,
                "num_results": len(documents),
                "query": query_text,
                "formatted_text": self._format_documents(documents)
            }

            logger.info(f"Retrieved {len(documents)} documents from LargeRAG")
            return result

        except Exception as e:
            logger.error(f"LargeRAG query failed: {e}", exc_info=True)
            return None

    def _format_documents(self, documents: list) -> str:
        """
        Format retrieved documents for display in agent prompt.

        Args:
            documents: List of document dicts from LargeRAG

        Returns:
            Formatted string suitable for LLM context
        """
        if not documents:
            return "No relevant documents found."

        formatted_parts = []

        for i, doc in enumerate(documents, 1):
            # Extract metadata
            metadata = doc.get('metadata', {})
            doc_hash = metadata.get('doc_hash', 'unknown')[:8]
            page = metadata.get('page_idx', 'N/A')
            score = doc.get('score', 0.0)

            # Extract text
            text = doc.get('text', '')

            # Truncate long texts
            if len(text) > 400:
                text = text[:400] + "..."

            # Format this document
            doc_text = f"""
Document {i} (Score: {score:.3f}, Source: {doc_hash}..., Page: {page}):
{text}
""".strip()

            formatted_parts.append(doc_text)

        return "\n\n---\n\n".join(formatted_parts)

    def get_status(self) -> Dict[str, Any]:
        """
        Get status information about the LargeRAG system.

        Returns:
            Dict with status information
        """
        if self.rag is None:
            return {"status": "error", "message": "LargeRAG not initialized"}

        if self.rag.query_engine is None:
            return {"status": "no_index", "message": "Index not loaded"}

        try:
            stats = self.rag.get_stats()
            return {
                "status": "ready",
                "stats": stats
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Convenience function
def create_largerag_adapter() -> LargeRAGAdapter:
    """
    Convenience function to create a LargeRAG adapter.

    Returns:
        LargeRAGAdapter instance

    Usage:
        from agent.tools.largerag_adapter import create_largerag_adapter

        largerag_client = create_largerag_adapter()
        agent = DESAgent(..., largerag_client=largerag_client, ...)
    """
    return LargeRAGAdapter()


# For testing
if __name__ == "__main__":
    # Import validation function
    try:
        from base import validate_tool_interface
    except ImportError:
        # Fallback if running directly
        def validate_tool_interface(tool):
            return hasattr(tool, 'query') and hasattr(tool, 'get_status')

    logging.basicConfig(level=logging.INFO)

    # Test adapter
    print("Testing LargeRAG Adapter...")
    print("="*60)

    adapter = LargeRAGAdapter()

    # Validate interface
    print(f"\n✓ Implements DESToolProtocol: {validate_tool_interface(adapter)}")

    # Check status
    status = adapter.get_status()
    print(f"\n✓ Status: {status}")

    if status["status"] == "ready":
        # Test query
        query_dict = {
            "query": "Deep eutectic solvent for cellulose dissolution",
            "top_k": 3
        }

        print(f"\nTest query: {query_dict['query']}")
        result = adapter.query(query_dict)

        if result:
            print(f"\nRetrieved {result['num_results']} documents")
            print("\nFormatted output:")
            print(result['formatted_text'])
        else:
            print("\nQuery failed")
    else:
        print("\nLargeRAG not ready. Please build index first:")
        print("  python src/tools/largerag/examples/1_build_index.py")
