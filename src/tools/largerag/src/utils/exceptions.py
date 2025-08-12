"""
LargeRAG异常类定义

定义了LargeRAG系统中使用的自定义异常类层次结构。
"""


class LargeRAGError(Exception):
    """LargeRAG基础异常类"""
    
    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.message = message
        self.details = details
    
    def __str__(self):
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class ConfigurationError(LargeRAGError):
    """配置相关错误"""
    pass


class DocumentProcessingError(LargeRAGError):
    """文档处理错误"""
    pass


class IndexingError(LargeRAGError):
    """索引操作错误"""
    pass


class QueryError(LargeRAGError):
    """查询执行错误"""
    pass


class VectorStoreError(LargeRAGError):
    """向量存储错误"""
    pass


class EmbeddingError(LargeRAGError):
    """嵌入生成错误"""
    pass