"""
基本工作流集成测试

测试LargeRAG的基本工作流程。
"""

import os
import tempfile
from pathlib import Path

from src.tools.largerag.src.largerag import LargeRAG
from src.tools.largerag.src.config.settings import LargeRAGSettings


def test_basic_initialization_workflow():
    """测试基本初始化工作流"""
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建配置
            settings = LargeRAGSettings()
            settings.vector_store.persist_directory = os.path.join(temp_dir, "indexes")
            settings.system.data_directory = os.path.join(temp_dir, "data")
            settings.system.temp_directory = os.path.join(temp_dir, "temp")
            settings.performance.cache_directory = os.path.join(temp_dir, "cache")
            settings.logging.file_path = ""  # 不使用文件日志
            
            # 初始化系统
            rag = LargeRAG(config=settings)
            
            # 验证目录创建
            assert Path(settings.vector_store.persist_directory).exists()
            assert Path(settings.system.data_directory).exists()
            assert Path(settings.system.temp_directory).exists()
            assert Path(settings.performance.cache_directory).exists()
            
            # 验证系统状态
            status = rag.get_system_status()
            assert status["config_loaded"] == True
            assert status["index_initialized"] == False
            
            # 测试有效的JSON数据格式（不会实际索引，但会通过验证）
            test_data = [
                {
                    "text": "深共熔溶剂（DES）是一种新型绿色溶剂",
                    "type": "text",
                    "title": "DES介绍"
                },
                {
                    "text": "DES具有低毒性、可生物降解等优点",
                    "type": "text",
                    "title": "DES优点"
                }
            ]
            
            # 验证数据格式正确（目前只是占位符实现）
            result = rag.index_documents_from_json(test_data)
            assert result == True
            
            # 清理日志处理器
            for handler in rag.logger.handlers[:]:
                handler.close()
                rag.logger.removeHandler(handler)
            
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


def test_config_reload():
    """测试配置重新加载"""
    os.environ["OPENAI_API_KEY"] = "test_key"
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建自定义配置文件
            # 使用正斜杠避免YAML转义问题
            temp_dir_normalized = temp_dir.replace('\\', '/')
            config_content = f"""
document_processing:
  chunk_size: 2000
  chunk_overlap: 400

embedding:
  model: "test-embedding-model"

vector_store:
  type: "test-vector-store"
  persist_directory: "{temp_dir_normalized}/indexes"

system:
  data_directory: "{temp_dir_normalized}/data"

logging:
  level: "DEBUG"
  file_path: ""
"""
            
            config_path = os.path.join(temp_dir, "test_config.yaml")
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            # 使用自定义配置初始化
            rag = LargeRAG(config_path=config_path)
            
            # 验证配置加载
            assert rag.config.document_processing.chunk_size == 2000
            assert rag.config.document_processing.chunk_overlap == 400
            assert rag.config.embedding.model == "test-embedding-model"
            assert rag.config.vector_store.type == "test-vector-store"
            assert rag.config.logging.level == "DEBUG"
            
            # 清理日志处理器
            for handler in rag.logger.handlers[:]:
                handler.close()
                rag.logger.removeHandler(handler)
            
    finally:
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]


if __name__ == "__main__":
    # 简单的测试运行器
    test_basic_initialization_workflow()
    print("✓ test_basic_initialization_workflow 通过")
    
    test_config_reload()
    print("✓ test_config_reload 通过")
    
    print("所有集成测试通过！")