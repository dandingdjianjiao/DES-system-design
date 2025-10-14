"""
Agent Tools Package

This package contains adapters and wrappers for external tools used by DESAgent.

All tools follow the DESToolProtocol interface:
    - query(query_dict: Dict) -> Optional[Dict]
    - get_status() -> Dict

Available tools:
    - LargeRAGAdapter: Literature retrieval from 10,000+ papers (✅ implemented)
    - CoreRAGAdapter: Theoretical knowledge from ontology (🚧 template ready)
    - (ExperimentalData: Numerical experiment data - future)
"""

from .base import (
    DESToolProtocol,
    DESTool,
    ToolStatus,
    StandardQueryResult,
    validate_tool_interface
)
from .largerag_adapter import LargeRAGAdapter, create_largerag_adapter
from .corerag_adapter import CoreRAGAdapter, create_corerag_adapter

__all__ = [
    # Protocol and base classes
    "DESToolProtocol",
    "DESTool",
    "ToolStatus",
    "StandardQueryResult",
    "validate_tool_interface",
    # Tool implementations
    "LargeRAGAdapter",
    "create_largerag_adapter",
    "CoreRAGAdapter",
    "create_corerag_adapter",
]
