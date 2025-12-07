class ValidationException(Exception):
    """Custom validation exception for feedback processing.

    Attributes:
        message: Human-readable error message
        field: Optional field name associated with the error
        index: Optional index (e.g., row index in measurements list)
    """

    def __init__(self, message: str, field: str = None, index: int = None):
        super().__init__(message)
        self.field = field
        self.index = index
        self.message = message
