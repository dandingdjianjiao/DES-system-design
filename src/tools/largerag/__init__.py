"""
LargeRAG工具包

基于LlamaIndex的大规模文献RAG系统，专门设计用于处理大规模科学文献集合（10,000+篇论文）。
该系统提供高效的文档索引、向量检索和查询功能，为DES配方预测提供全面的文献支持。

主要功能：
- 大规模文档处理和索引
- 基于向量相似性的高效检索
- 配置驱动的系统管理
- 与项目其他工具的标准化接口
"""

__version__ = "0.1.0"
__author__ = "DES System Design Team"

from .src.largerag import LargeRAG
from .src.config.settings import LargeRAGSettings

__all__ = ["LargeRAG", "LargeRAGSettings"]