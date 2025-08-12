"""
配置系统单元测试

测试LargeRAG配置管理系统的功能。
"""

import os
import tempfile
import pytest
from pathlib import Path

from src.tools.largerag.src.config.settings import (
    LargeRAGSettings,
    DocumentProcessingSettings,
    EmbeddingSettings,
    VectorStoreSettings,
    RetrievalSettings,
    LLMSettings,
    LoggingSettings,
    PerformanceSettings,
    SystemSettings
)


def test_default_settings():
    """测试默认配置创建"""
    settings = LargeRAGSettings()
    
    assert settings.document_processing.chunk_size == 1000
    assert settings.embedding.model == "text-embedding-ada-002"
    assert settings.vector_store.type == "chroma"
    assert settings.retrieval.top_k == 10
    assert settings.llm.model == "gpt-4"


def test_settings_validation():
    """测试配置验证"""
    settings = LargeRAGSettings()
    
    # 设置必要的配置项
    settings.vector_store.persist_directory = "/tmp/test"
    settings.system.data_directory = "/tmp/test"
    
    # 设置环境变量
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    try:
        # 应该验证成功
        assert settings.validate() == True
    finally:
        # 清理环境变量
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_settings_validation_failure():
    """测试配置验证失败"""
    settings = LargeRAGSettings()
    
    # 不设置必要的配置项，应该验证失败
    with pytest.raises(ValueError):
        settings.validate()


def test_yaml_loading():
    """测试从YAML文件加载配置"""
    yaml_content = """
document_processing:
  chunk_size: 2000
  chunk_overlap: 400

embedding:
  model: "test-embedding-model"

vector_store:
  type: "test-vector-store"
  persist_directory: "/tmp/test"

system:
  data_directory: "/tmp/test"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        temp_path = f.name
    
    try:
        # 设置环境变量
        os.environ["OPENAI_API_KEY"] = "test_key"
        
        settings = LargeRAGSettings.from_yaml(temp_path)
        
        assert settings.document_processing.chunk_size == 2000
        assert settings.document_processing.chunk_overlap == 400
        assert settings.embedding.model == "test-embedding-model"
        assert settings.vector_store.type == "test-vector-store"
        
    finally:
        # 清理
        os.unlink(temp_path)
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_ensure_directories():
    """测试目录创建功能"""
    with tempfile.TemporaryDirectory() as temp_dir:
        settings = LargeRAGSettings()
        settings.vector_store.persist_directory = os.path.join(temp_dir, "indexes")
        settings.system.data_directory = os.path.join(temp_dir, "data")
        settings.system.temp_directory = os.path.join(temp_dir, "temp")
        settings.performance.cache_directory = os.path.join(temp_dir, "cache")
        settings.logging.file_path = os.path.join(temp_dir, "logs", "test.log")
        
        settings.ensure_directories()
        
        # 验证目录是否创建
        assert Path(settings.vector_store.persist_directory).exists()
        assert Path(settings.system.data_directory).exists()
        assert Path(settings.system.temp_directory).exists()
        assert Path(settings.performance.cache_directory).exists()
        assert Path(settings.logging.file_path).parent.exists()


if __name__ == "__main__":
    # 简单的测试运行器
    test_default_settings()
    print("✓ test_default_settings 通过")
    
    test_ensure_directories()
    print("✓ test_ensure_directories 通过")
    
    print("所有测试通过！")