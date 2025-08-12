"""
LargeRAG主接口类

基于LlamaIndex的大规模文献RAG系统主接口，提供文档索引和查询功能。
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from .config.settings import LargeRAGSettings, LARGERAG_SETTINGS


class LargeRAG:
    """
    LargeRAG主接口类
    
    提供基于LlamaIndex的大规模文献RAG功能，包括：
    - 从JSON数据索引文档
    - 语义相似性查询
    - 配置管理
    - 错误处理和日志记录
    """
    
    def __init__(self, config: Optional[LargeRAGSettings] = None, config_path: Optional[str] = None):
        """
        初始化LargeRAG系统
        
        Args:
            config: 配置对象，如果为None则使用默认配置
            config_path: 配置文件路径，如果指定则从文件加载配置
        """
        # 加载配置
        if config_path:
            self.config = LargeRAGSettings.from_yaml(config_path)
        elif config:
            self.config = config
        else:
            self.config = LARGERAG_SETTINGS
            
        # 验证配置
        self.config.validate()
        
        # 确保必要目录存在
        self.config.ensure_directories()
        
        # 设置日志
        self._setup_logging()
        
        # 初始化组件（将在后续任务中实现）
        self.index = None
        self.query_engine = None
        
        self.logger.info("LargeRAG系统初始化完成")
    
    def _setup_logging(self):
        """设置日志系统"""
        self.logger = logging.getLogger("LargeRAG")
        self.logger.setLevel(getattr(logging, self.config.logging.level))
        
        # 如果已有处理器，先清除
        if self.logger.handlers:
            self.logger.handlers.clear()
            
        # 创建格式器
        formatter = logging.Formatter(self.config.logging.format)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（如果配置了文件路径）
        if self.config.logging.file_path:
            from logging.handlers import RotatingFileHandler
            
            # 解析文件大小
            max_bytes = self._parse_size(self.config.logging.max_file_size)
            
            file_handler = RotatingFileHandler(
                self.config.logging.file_path,
                maxBytes=max_bytes,
                backupCount=self.config.logging.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def _parse_size(self, size_str: str) -> int:
        """解析大小字符串为字节数"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def index_documents_from_json(self, json_data: List[Dict[str, Any]]) -> bool:
        """
        从JSON数据索引文档集合
        
        Args:
            json_data: JSON格式的文档数据列表，每个元素包含text字段和其他元数据
            
        Returns:
            bool: 索引是否成功
            
        Raises:
            ValueError: 如果输入数据格式不正确
            RuntimeError: 如果索引过程失败
        """
        self.logger.info(f"开始索引 {len(json_data)} 个文档")
        
        try:
            # 验证输入数据
            if not json_data:
                raise ValueError("输入数据不能为空")
                
            for i, doc in enumerate(json_data):
                if not isinstance(doc, dict):
                    raise ValueError(f"文档 {i} 不是字典格式")
                if 'text' not in doc:
                    raise ValueError(f"文档 {i} 缺少 'text' 字段")
            
            # TODO: 在后续任务中实现实际的索引逻辑
            # 这里只是占位符实现
            self.logger.info("文档索引功能将在后续任务中实现")
            
            return True
            
        except ValueError:
            # 重新抛出验证错误，不包装
            raise
        except Exception as e:
            self.logger.error(f"文档索引失败: {e}")
            raise RuntimeError(f"文档索引失败: {e}") from e
    
    def query(self, query_text: str, **kwargs) -> str:
        """
        执行查询并返回结果
        
        Args:
            query_text: 查询文本
            **kwargs: 额外的查询参数，如top_k等
            
        Returns:
            str: 查询结果
            
        Raises:
            ValueError: 如果索引未初始化或查询文本为空
            RuntimeError: 如果查询过程失败
        """
        if not query_text.strip():
            raise ValueError("查询文本不能为空")
            
        if self.index is None:
            raise ValueError("索引未初始化，请先调用 index_documents_from_json")
        
        self.logger.info(f"执行查询: {query_text[:100]}...")
        
        try:
            # TODO: 在后续任务中实现实际的查询逻辑
            # 这里只是占位符实现
            self.logger.info("查询功能将在后续任务中实现")
            
            return f"查询结果占位符: {query_text}"
            
        except Exception as e:
            self.logger.error(f"查询失败: {e}")
            raise RuntimeError(f"查询失败: {e}") from e
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态信息
        
        Returns:
            Dict[str, Any]: 系统状态信息
        """
        return {
            "index_initialized": self.index is not None,
            "config_loaded": True,
            "vector_store_type": self.config.vector_store.type,
            "embedding_model": self.config.embedding.model,
            "llm_model": self.config.llm.model,
            "data_directory": self.config.system.data_directory,
            "cache_enabled": self.config.performance.enable_caching,
        }
    
    def reload_config(self, config_path: Optional[str] = None):
        """
        重新加载配置
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.logger.info("重新加载配置")
        
        try:
            if config_path:
                self.config = LargeRAGSettings.from_yaml(config_path)
            else:
                # 重新加载默认配置
                default_config_path = Path(__file__).parent / "config" / "settings.yaml"
                self.config = LargeRAGSettings.from_yaml(str(default_config_path))
            
            # 验证新配置
            self.config.validate()
            
            # 确保目录存在
            self.config.ensure_directories()
            
            # 重新设置日志
            self._setup_logging()
            
            self.logger.info("配置重新加载完成")
            
        except Exception as e:
            self.logger.error(f"配置重新加载失败: {e}")
            raise RuntimeError(f"配置重新加载失败: {e}") from e