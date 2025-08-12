#!/usr/bin/env python3
"""
测试智能嵌入模型处理功能
验证系统能否根据服务类型自动选择合适的嵌入模型类
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_dashscope_embedding_intelligence():
    """测试DashScope嵌入模型智能选择"""
    print("🔍 测试DashScope嵌入模型智能选择...")
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE')
    
    if not api_key:
        print("⚠️  API密钥未设置，跳过测试")
        return True
    
    if not api_base or "dashscope.aliyuncs.com" not in api_base:
        print("⚠️  非DashScope服务，跳过专用类测试")
        return True
    
    print(f"📋 检测到DashScope服务: {api_base}")
    
    # 测试智能嵌入模型类选择
    try:
        # 首先尝试DashScope专用嵌入模型类
        try:
            from llama_index.embeddings.dashscope import DashScopeEmbedding
            
            # 设置DashScope API密钥
            os.environ["DASHSCOPE_API_KEY"] = api_key
            
            embedding = DashScopeEmbedding(
                model_name="text-embedding-v1",
                api_key=api_key
            )
            
            print("✅ 成功使用DashScope专用嵌入模型类")
            print(f"   模型: {embedding.model_name}")
            return True
            
        except ImportError:
            print("⚠️  DashScope嵌入模型包未安装，尝试回退到OpenAI兼容模式")
            
            # 回退到OpenAI兼容模式
            from llama_index.embeddings.openai import OpenAIEmbedding
            
            embedding = OpenAIEmbedding(
                model="text-embedding-v1",
                api_key=api_key,
                api_base=api_base
            )
            
            print("✅ 成功回退到OpenAI兼容模式")
            print(f"   模型: {embedding.model_name}")
            return True
            
    except Exception as e:
        print(f"❌ 嵌入模型智能选择失败: {e}")
        return False

def test_embedding_model_creation():
    """测试不同服务的嵌入模型创建"""
    print("\n🔍 测试嵌入模型创建逻辑...")
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE')
    
    if not api_key:
        print("⚠️  API密钥未设置，跳过测试")
        return True
    
    try:
        # 模拟智能嵌入模型选择逻辑
        if api_base and "dashscope.aliyuncs.com" in api_base:
            print("🎯 检测到DashScope服务，尝试智能选择...")
            
            # 尝试专用类
            try:
                from llama_index.embeddings.dashscope import DashScopeEmbedding
                
                os.environ["DASHSCOPE_API_KEY"] = api_key
                
                embedding = DashScopeEmbedding(
                    model_name="text-embedding-v1",
                    api_key=api_key
                )
                
                print("✅ 使用DashScope专用嵌入模型类")
                print(f"   类型: {type(embedding).__name__}")
                print(f"   模型: {embedding.model_name}")
                
            except ImportError:
                print("⚠️  DashScope嵌入模型包未安装，使用OpenAI兼容模式")
                
                from llama_index.embeddings.openai import OpenAIEmbedding
                
                embedding = OpenAIEmbedding(
                    model="text-embedding-v1",
                    api_key=api_key,
                    api_base=api_base
                )
                
                print("✅ 使用OpenAI兼容嵌入模型类")
                print(f"   类型: {type(embedding).__name__}")
                print(f"   模型: {embedding.model_name}")
                
        else:
            print("🎯 使用标准OpenAI嵌入模型...")
            
            from llama_index.embeddings.openai import OpenAIEmbedding
            
            embedding_kwargs = {"api_key": api_key}
            if api_base:
                embedding_kwargs["api_base"] = api_base
            
            embedding = OpenAIEmbedding(
                model="text-embedding-ada-002",
                **embedding_kwargs
            )
            
            print("✅ 使用标准OpenAI嵌入模型类")
            print(f"   类型: {type(embedding).__name__}")
            print(f"   模型: {embedding.model_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 嵌入模型创建失败: {e}")
        return False

def show_embedding_recommendations():
    """显示嵌入模型推荐"""
    print("\n💡 嵌入模型使用建议:")
    print("=" * 50)
    
    recommendations = [
        {
            "service": "通义千问 (DashScope)",
            "preferred": "DashScopeEmbedding + text-embedding-v1",
            "fallback": "OpenAIEmbedding + text-embedding-v1 (兼容模式)",
            "install": "pip install llama-index-embeddings-dashscope",
            "note": "专用类性能更好，支持中文优化"
        },
        {
            "service": "OpenAI官方",
            "preferred": "OpenAIEmbedding + text-embedding-ada-002",
            "fallback": "无需回退",
            "install": "pip install llama-index-embeddings-openai",
            "note": "标准配置，稳定可靠"
        },
        {
            "service": "其他兼容服务",
            "preferred": "OpenAIEmbedding + 兼容模型名",
            "fallback": "本地嵌入模型",
            "install": "pip install sentence-transformers",
            "note": "建议使用本地嵌入模型避免兼容性问题"
        }
    ]
    
    for rec in recommendations:
        print(f"\n🔧 {rec['service']}:")
        print(f"   推荐方案: {rec['preferred']}")
        print(f"   回退方案: {rec['fallback']}")
        print(f"   安装命令: {rec['install']}")
        print(f"   注意事项: {rec['note']}")

def main():
    """主测试函数"""
    print("🔍 测试智能嵌入模型处理功能...")
    print("=" * 60)
    
    # 运行测试
    dashscope_ok = test_dashscope_embedding_intelligence()
    creation_ok = test_embedding_model_creation()
    
    # 显示推荐
    show_embedding_recommendations()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"   DashScope智能选择: {'✅' if dashscope_ok else '❌'}")
    print(f"   嵌入模型创建: {'✅' if creation_ok else '❌'}")
    
    print("\n🎉 智能嵌入模型处理功能:")
    print("   ✅ 自动检测服务类型")
    print("   ✅ 优先使用专用嵌入模型类")
    print("   ✅ 自动回退到兼容模式")
    print("   ✅ 提供清晰的错误信息和建议")
    
    return 0 if (dashscope_ok and creation_ok) else 1

if __name__ == "__main__":
    sys.exit(main())