"""
LargeRAG主类单元测试

测试LargeRAG主接口类的基本功能。
"""

import os
import tempfile
import pytest
from pathlib import Path

from src.tools.largerag.src.largerag import LargeRAG
from src.tools.largerag.src.config.settings import LargeRAGSettings


def test_largerag_initialization():
    """测试LargeRAG初始化"""
    # 设置环境变量
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试配置
            settings = LargeRAGSettings()
            settings.vector_store.persist_directory = os.path.join(temp_dir, "indexes")
            settings.system.data_directory = os.path.join(temp_dir, "data")
            # 不设置文件日志，避免文件锁定问题
            settings.logging.file_path = ""
            
            # 初始化LargeRAG
            rag = LargeRAG(config=settings)
            
            # 验证初始化状态
            assert rag.config is not None
            assert rag.index is None
            assert rag.query_engine is None
            assert rag.logger is not None
            
            # 清理日志处理器
            for handler in rag.logger.handlers[:]:
                handler.close()
                rag.logger.removeHandler(handler)
            
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_system_status():
    """测试系统状态获取"""
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = LargeRAGSettings()
            settings.vector_store.persist_directory = os.path.join(temp_dir, "indexes")
            settings.system.data_directory = os.path.join(temp_dir, "data")
            
            rag = LargeRAG(config=settings)
            status = rag.get_system_status()
            
            assert isinstance(status, dict)
            assert "index_initialized" in status
            assert "config_loaded" in status
            assert "vector_store_type" in status
            assert status["index_initialized"] == False
            assert status["config_loaded"] == True
            
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_index_documents_validation():
    """测试文档索引输入验证"""
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = LargeRAGSettings()
            settings.vector_store.persist_directory = os.path.join(temp_dir, "indexes")
            settings.system.data_directory = os.path.join(temp_dir, "data")
            settings.logging.file_path = ""  # 不使用文件日志
            
            rag = LargeRAG(config=settings)
            
            # 测试空数据
            with pytest.raises(ValueError, match="输入数据不能为空"):
                rag.index_documents_from_json([])
            
            # 测试无效格式
            with pytest.raises(ValueError, match="不是字典格式"):
                rag.index_documents_from_json(["invalid"])
            
            # 测试缺少text字段
            with pytest.raises(ValueError, match="缺少 'text' 字段"):
                rag.index_documents_from_json([{"title": "test"}])
            
            # 清理日志处理器
            for handler in rag.logger.handlers[:]:
                handler.close()
                rag.logger.removeHandler(handler)
                
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_query_validation():
    """测试查询输入验证"""
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = LargeRAGSettings()
            settings.vector_store.persist_directory = os.path.join(temp_dir, "indexes")
            settings.system.data_directory = os.path.join(temp_dir, "data")
            settings.logging.file_path = ""  # 不使用文件日志
            
            rag = LargeRAG(config=settings)
            
            # 测试空查询
            with pytest.raises(ValueError, match="查询文本不能为空"):
                rag.query("")
            
            # 测试未初始化索引
            with pytest.raises(ValueError, match="索引未初始化"):
                rag.query("test query")
            
            # 清理日志处理器
            for handler in rag.logger.handlers[:]:
                handler.close()
                rag.logger.removeHandler(handler)
                
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


if __name__ == "__main__":
    # 简单的测试运行器
    test_largerag_initialization()
    print("✓ test_largerag_initialization 通过")
    
    test_system_status()
    print("✓ test_system_status 通过")
    
    test_index_documents_validation()
    print("✓ test_index_documents_validation 通过")
    
    test_query_validation()
    print("✓ test_query_validation 通过")
    
    print("所有测试通过！")