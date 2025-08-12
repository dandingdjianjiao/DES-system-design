#!/usr/bin/env python3
"""
验证LargeRAG工具依赖包安装和导入
"""

import sys
import importlib
from typing import List, Tuple

def verify_import(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """验证模块导入"""
    try:
        importlib.import_module(module_name)
        return True, f"✅ {package_name or module_name} - 导入成功"
    except ImportError as e:
        return False, f"❌ {package_name or module_name} - 导入失败: {e}"
    except Exception as e:
        return False, f"❌ {package_name or module_name} - 其他错误: {e}"

def main():
    """主验证函数"""
    print("🔍 验证LargeRAG工具依赖包...")
    print("=" * 60)
    
    # 定义需要验证的包
    dependencies = [
        # LlamaIndex核心包
        ("llama_index", "llama-index"),
        ("llama_index.core", "llama-index-core"),
        
        # 嵌入模型支持
        ("llama_index.embeddings.openai", "llama-index-embeddings-openai"),
        ("openai", "openai"),
        
        # LLM支持
        ("llama_index.llms.openai", "llama-index-llms-openai"),
        
        # 向量数据库支持
        ("llama_index.vector_stores.chroma", "llama-index-vector-stores-chroma"),
        ("chromadb", "chromadb"),
        
        # 文档处理
        ("llama_index.readers.file", "llama-index-readers-file"),
        
        # 配置管理
        ("yaml", "pyyaml"),
        ("dotenv", "python-dotenv"),
        
        # 数据处理
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        
        # 日志
        ("structlog", "structlog"),
        
        # 类型提示
        ("typing_extensions", "typing-extensions"),
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for module_name, package_name in dependencies:
        success, message = verify_import(module_name, package_name)
        print(message)
        if success:
            success_count += 1
    
    print("=" * 60)
    print(f"📊 验证结果: {success_count}/{total_count} 包成功导入")
    
    if success_count == total_count:
        print("🎉 所有依赖包安装和导入成功！")
        return 0
    else:
        print("⚠️  部分依赖包存在问题，请检查安装")
        return 1

if __name__ == "__main__":
    sys.exit(main())