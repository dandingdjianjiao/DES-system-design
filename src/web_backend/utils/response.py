"""
Response utilities for API endpoints

Provides helper functions for creating standardized API responses.
"""

from typing import Any, Dict, List, Optional
from models.schemas import BaseResponse, ErrorResponse, ErrorDetail


def success_response(
    data: Any,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a success response.

    Args:
        data: Response data
        message: Optional success message

    Returns:
        Dict with status="success" and data
    """
    response = {
        "status": "success",
        "data": data
    }
    if message:
        response["message"] = message
    return response


def error_response(
    message: str,
    errors: Optional[List[Dict[str, str]]] = None,
    status_code: int = 400,
    field: Optional[str] = None,
    index: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create an error response.

    Args:
        message: Error message
        errors: Optional list of field-specific errors
        status_code: HTTP status code

    Returns:
        Dict with status="error" and error details
    """
    response: Dict[str, Any] = {
        "status": "error",
        "message": message
    }

    # Primary field/index (single error)
    if field is not None:
        response["field"] = field
    if index is not None:
        response["index"] = index

    # Optional structured errors list
    if errors:
        # Preserve any extra keys such as index
        response["errors"] = [
            {
                "field": e.get("field", "unknown"),
                "message": e.get("message", ""),
                **({"index": e.get("index")} if "index" in e else {})
            }
            for e in errors
        ]
    return response
