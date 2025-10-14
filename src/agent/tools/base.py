"""
Tool Interface Protocol for DESAgent

Defines the standard interface that all DESAgent tools must implement.
Uses typing.Protocol for structural subtyping (duck typing with type checking).
"""

from typing import Protocol, Dict, Optional, Any


class ToolStatus:
    """
    Standard status codes for tools.
    """
    READY = "ready"           # Tool is initialized and ready to use
    ERROR = "error"           # Tool encountered an error
    NO_DATA = "no_data"       # Tool has no data loaded (e.g., no index, no database)
    NOT_INITIALIZED = "not_initialized"  # Tool is not initialized


class DESToolProtocol(Protocol):
    """
    Protocol defining the interface for DES formulation tools.

    All tools (CoreRAG, LargeRAG, ExperimentalData) should implement:
    - query(query_dict) -> Optional[Dict]
    - get_status() -> Dict

    Using Protocol allows structural subtyping without requiring inheritance.
    Tools just need to implement these methods to be compatible.

    Example:
        # Tool implementation (no inheritance needed)
        class MyTool:
            def query(self, query_dict: Dict[str, Any]) -> Optional[Dict]:
                return {"result": "..."}

            def get_status(self) -> Dict[str, Any]:
                return {"status": "ready"}

        # Type checking works
        def use_tool(tool: DESToolProtocol):
            result = tool.query({"query": "test"})

        my_tool = MyTool()
        use_tool(my_tool)  # ✓ Type checks pass
    """

    def query(self, query_dict: Dict[str, Any]) -> Optional[Dict]:
        """
        Query the tool for information.

        Args:
            query_dict: Query parameters. Common keys:
                - query (str): Query text (required)
                - top_k (int): Number of results to return
                - filters (dict): Metadata filters
                - ... (tool-specific parameters)

        Returns:
            Dict containing query results, or None if query fails.
            Common keys in return dict:
                - query (str): Original query text
                - num_results (int): Number of results found
                - formatted_text (str): Human-readable formatted results
                - ... (tool-specific fields)

        Example:
            query_dict = {
                "query": "DES for cellulose",
                "top_k": 5,
                "filters": {"temperature_range": [20, 30]}
            }
            result = tool.query(query_dict)
        """
        ...

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the tool.

        Returns:
            Dict with status information:
                - status (str): One of ToolStatus constants
                - message (str): Human-readable status message (optional)
                - stats (dict): Tool-specific statistics (optional)

        Example:
            status = tool.get_status()
            if status["status"] == ToolStatus.READY:
                # Tool is ready to use
                result = tool.query(...)
        """
        ...


# Type alias for convenience
DESTool = DESToolProtocol


def validate_tool_interface(tool: Any) -> bool:
    """
    Validate that an object implements the DESToolProtocol interface.

    Args:
        tool: Object to validate

    Returns:
        True if tool implements the required interface, False otherwise

    Example:
        if validate_tool_interface(my_tool):
            agent = DESAgent(..., largerag_client=my_tool, ...)
        else:
            raise ValueError("Tool does not implement DESToolProtocol")
    """
    required_methods = ["query", "get_status"]

    for method_name in required_methods:
        if not hasattr(tool, method_name):
            return False
        if not callable(getattr(tool, method_name)):
            return False

    return True


# ============================================================
# Standard Query Result Format (Recommendation)
# ============================================================

class StandardQueryResult:
    """
    Recommended structure for tool query results.

    This is not enforced, but provides a common structure for consistency.
    Tools can extend this with additional fields.
    """

    @staticmethod
    def create(
        query: str,
        formatted_text: str,
        num_results: int = 0,
        raw_data: Optional[Any] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Create a standard query result dict.

        Args:
            query: Original query text
            formatted_text: Formatted result text for LLM prompt
            num_results: Number of results found
            raw_data: Raw data from tool (optional)
            metadata: Additional metadata (optional)

        Returns:
            Standardized result dict
        """
        result = {
            "query": query,
            "formatted_text": formatted_text,
            "num_results": num_results,
        }

        if raw_data is not None:
            result["raw_data"] = raw_data

        if metadata is not None:
            result["metadata"] = metadata

        return result


# ============================================================
# Example Usage (for documentation)
# ============================================================

if __name__ == "__main__":
    """
    Example showing how to implement and use DESToolProtocol.
    """

    # Example implementation
    class ExampleTool:
        def query(self, query_dict: Dict[str, Any]) -> Optional[Dict]:
            query_text = query_dict.get("query", "")
            return StandardQueryResult.create(
                query=query_text,
                formatted_text=f"Results for: {query_text}",
                num_results=3
            )

        def get_status(self) -> Dict[str, Any]:
            return {
                "status": ToolStatus.READY,
                "message": "Tool is ready"
            }

    # Validate interface
    tool = ExampleTool()
    print(f"Tool implements DESToolProtocol: {validate_tool_interface(tool)}")

    # Use tool
    result = tool.query({"query": "test"})
    print(f"Query result: {result}")

    status = tool.get_status()
    print(f"Tool status: {status}")
