#!/usr/bin/env python3
"""
测试LargeRAG工具基本功能
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_llama_index_imports():
    """测试LlamaIndex导入"""
    print("🔍 测试LlamaIndex核心功能导入...")
    
    try:
        from llama_index.core import Document, VectorStoreIndex
        from llama_index.core.node_parser import SimpleNodeParser
        from llama_index.embeddings.openai import OpenAIEmbedding
        from llama_index.llms.openai import OpenAI
        from llama_index.vector_stores.chroma import ChromaVectorStore
        
        print("✅ LlamaIndex核心组件导入成功")
        return True
    except ImportError as e:
        print(f"❌ LlamaIndex导入失败: {e}")
        return False

def test_chroma_basic():
    """测试Chroma基本功能"""
    print("\n🔍 测试Chroma向量数据库基本功能...")
    
    try:
        import chromadb
        from chromadb.config import Settings
        
        # 创建临时内存数据库进行测试
        client = chromadb.Client(Settings(
            is_persistent=False,
            anonymized_telemetry=False
        ))
        
        # 创建集合
        collection = client.create_collection(
            name="test_collection",
            metadata={"description": "测试集合"}
        )
        
        # 添加测试文档
        collection.add(
            documents=["这是一个测试文档", "这是另一个测试文档"],
            metadatas=[{"source": "test1"}, {"source": "test2"}],
            ids=["doc1", "doc2"]
        )
        
        # 查询测试
        results = collection.query(
            query_texts=["测试"],
            n_results=1
        )
        
        print("✅ Chroma基本功能测试成功")
        print(f"   查询结果数量: {len(results['documents'][0])}")
        return True
        
    except Exception as e:
        print(f"❌ Chroma测试失败: {e}")
        return False

def test_document_processing():
    """测试文档处理功能"""
    print("\n🔍 测试文档处理功能...")
    
    try:
        from llama_index.core import Document
        from llama_index.core.node_parser import SimpleNodeParser
        
        # 创建测试文档
        documents = [
            Document(text="这是第一个测试文档，包含一些示例内容。"),
            Document(text="这是第二个测试文档，用于测试文档处理功能。"),
        ]
        
        # 创建节点解析器
        parser = SimpleNodeParser.from_defaults(
            chunk_size=100,
            chunk_overlap=20
        )
        
        # 解析文档为节点
        nodes = parser.get_nodes_from_documents(documents)
        
        print("✅ 文档处理功能测试成功")
        print(f"   原始文档数量: {len(documents)}")
        print(f"   解析节点数量: {len(nodes)}")
        return True
        
    except Exception as e:
        print(f"❌ 文档处理测试失败: {e}")
        return False

def test_openai_config():
    """测试OpenAI配置（不实际调用API）"""
    print("\n🔍 测试OpenAI配置...")
    
    # 加载环境变量
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️  OPENAI_API_KEY未设置，跳过OpenAI配置测试")
        print("   请在.env文件中设置API密钥以启用完整功能")
        return True
    
    try:
        from llama_index.embeddings.openai import OpenAIEmbedding
        from llama_index.llms.openai import OpenAI
        
        # 创建嵌入模型实例（不实际调用）
        embedding = OpenAIEmbedding(
            model="text-embedding-ada-002",
            api_key=api_key
        )
        
        # 创建LLM实例（不实际调用）
        llm = OpenAI(
            model="gpt-4",
            api_key=api_key,
            temperature=0.1
        )
        
        print("✅ OpenAI配置测试成功")
        print(f"   嵌入模型: {embedding.model_name}")
        print(f"   LLM模型: {llm.model}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI配置测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔍 测试LargeRAG工具基本功能...")
    print("=" * 60)
    
    # 运行各项测试
    tests = [
        test_llama_index_imports,
        test_chroma_basic,
        test_document_processing,
        test_openai_config,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试执行失败: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    
    test_names = [
        "LlamaIndex导入",
        "Chroma基本功能",
        "文档处理",
        "OpenAI配置"
    ]
    
    success_count = 0
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅" if result else "❌"
        print(f"   {status} {name}")
        if result:
            success_count += 1
    
    print(f"\n📈 成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    if success_count == len(results):
        print("🎉 所有基本功能测试通过！")
        return 0
    else:
        print("⚠️  部分功能测试失败，请检查配置和依赖")
        return 1

if __name__ == "__main__":
    sys.exit(main())