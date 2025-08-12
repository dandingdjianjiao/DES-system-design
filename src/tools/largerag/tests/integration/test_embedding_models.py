#!/usr/bin/env python3
"""
测试嵌入模型集成
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_dashscope_embedding():
    """测试DashScope嵌入模型"""
    print("🔍 测试DashScope嵌入模型...")
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ API密钥未设置")
        return False
    
    try:
        from llama_index.embeddings.dashscope import DashScopeEmbedding
        
        # 设置DashScope API密钥
        os.environ["DASHSCOPE_API_KEY"] = api_key
        
        # 创建DashScope嵌入模型实例
        embedding = DashScopeEmbedding(
            model_name="text-embedding-v1",
            api_key=api_key
        )
        
        # 测试嵌入生成
        test_text = "深共熔溶剂是一种绿色溶剂"
        print(f"📝 测试文本: {test_text}")
        
        embedding_vector = embedding.get_text_embedding(test_text)
        print(f"✅ DashScope嵌入生成成功:")
        print(f"   向量维度: {len(embedding_vector)}")
        print(f"   向量预览: {embedding_vector[:5]}")
        
        return True
        
    except ImportError:
        print("⚠️  DashScope嵌入包未安装")
        return False
    except Exception as e:
        print(f"❌ DashScope嵌入测试失败: {e}")
        return False

def test_openai_compatible_embedding():
    """测试OpenAI兼容嵌入模型"""
    print("\n🔍 测试OpenAI兼容嵌入模型...")
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE')
    
    if not api_key:
        print("❌ API密钥未设置")
        return False
    
    try:
        from llama_index.embeddings.openai import OpenAIEmbedding
        
        # 尝试使用OpenAI兼容的嵌入模型
        embedding = OpenAIEmbedding(
            model="text-embedding-v1",  # 通义千问的嵌入模型名
            api_key=api_key,
            api_base=api_base
        )
        
        # 测试嵌入生成
        test_text = "深共熔溶剂是一种绿色溶剂"
        print(f"📝 测试文本: {test_text}")
        
        embedding_vector = embedding.get_text_embedding(test_text)
        print(f"✅ OpenAI兼容嵌入生成成功:")
        print(f"   向量维度: {len(embedding_vector)}")
        print(f"   向量预览: {embedding_vector[:5]}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI兼容嵌入测试失败: {e}")
        return False

def test_batch_embedding():
    """测试批量嵌入生成"""
    print("\n🔍 测试批量嵌入生成...")
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ API密钥未设置")
        return False
    
    try:
        from llama_index.embeddings.dashscope import DashScopeEmbedding
        
        # 设置DashScope API密钥
        os.environ["DASHSCOPE_API_KEY"] = api_key
        
        # 创建DashScope嵌入模型实例
        embedding = DashScopeEmbedding(
            model_name="text-embedding-v1",
            api_key=api_key
        )
        
        # 测试批量嵌入生成
        test_texts = [
            "深共熔溶剂是一种绿色溶剂",
            "DES具有低毒性和可生物降解性",
            "氢键供体和氢键受体形成共熔混合物"
        ]
        print(f"📝 测试文本数量: {len(test_texts)}")
        
        embedding_vectors = embedding.get_text_embedding_batch(test_texts)
        print(f"✅ 批量嵌入生成成功:")
        print(f"   向量数量: {len(embedding_vectors)}")
        print(f"   向量维度: {len(embedding_vectors[0])}")
        
        return True
        
    except ImportError:
        print("⚠️  DashScope嵌入包未安装")
        return False
    except Exception as e:
        print(f"❌ 批量嵌入测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔍 测试嵌入模型集成...")
    print("=" * 50)
    
    # 测试DashScope嵌入模型
    dashscope_ok = test_dashscope_embedding()
    
    # 测试OpenAI兼容嵌入模型
    openai_compatible_ok = test_openai_compatible_embedding()
    
    # 测试批量嵌入
    batch_ok = test_batch_embedding()
    
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"   DashScope嵌入模型: {'✅' if dashscope_ok else '❌'}")
    print(f"   OpenAI兼容嵌入模型: {'✅' if openai_compatible_ok else '❌'}")
    print(f"   批量嵌入生成: {'✅' if batch_ok else '❌'}")
    
    if not dashscope_ok:
        print("\n💡 安装DashScope嵌入包:")
        print("   pip install llama-index-embeddings-dashscope")
    
    return 0 if (dashscope_ok or openai_compatible_ok) else 1

if __name__ == "__main__":
    sys.exit(main())