#!/usr/bin/env python3
"""
简单测试通义千问集成
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_qwen_with_dashscope():
    """测试使用DashScope专用包"""
    print("🔍 测试DashScope专用包...")
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ API密钥未设置")
        return False
    
    try:
        from llama_index.llms.dashscope import DashScope
        
        # 设置DashScope API密钥
        os.environ["DASHSCOPE_API_KEY"] = api_key
        
        # 创建DashScope LLM实例
        llm = DashScope(
            model_name="qwen-turbo",
            api_key=api_key,
            temperature=0.1,
            max_tokens=100
        )
        
        # 测试简单的文本生成
        test_prompt = "什么是深共熔溶剂？"
        print(f"📝 测试提示: {test_prompt}")
        
        response = llm.complete(test_prompt)
        print(f"✅ DashScope响应成功:")
        print(f"   响应: {response.text[:100]}...")
        
        return True
        
    except ImportError:
        print("⚠️  DashScope包未安装")
        return False
    except Exception as e:
        print(f"❌ DashScope测试失败: {e}")
        return False

def test_qwen_with_openai_compatible():
    """测试使用OpenAI兼容模式"""
    print("\n🔍 测试OpenAI兼容模式...")
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    api_base = os.getenv('OPENAI_API_BASE')
    
    if not api_key:
        print("❌ API密钥未设置")
        return False
    
    try:
        from llama_index.llms.openai import OpenAI
        
        # 创建OpenAI兼容的LLM实例
        llm = OpenAI(
            model="qwen-turbo",
            api_key=api_key,
            api_base=api_base,
            temperature=0.1,
            max_tokens=100
        )
        
        # 测试简单的文本生成
        test_prompt = "什么是深共熔溶剂？"
        print(f"📝 测试提示: {test_prompt}")
        
        response = llm.complete(test_prompt)
        print(f"✅ OpenAI兼容模式响应成功:")
        print(f"   响应: {response.text[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI兼容模式测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🔍 测试通义千问集成方式...")
    print("=" * 50)
    
    # 测试DashScope专用包
    dashscope_ok = test_qwen_with_dashscope()
    
    # 测试OpenAI兼容模式
    openai_compatible_ok = test_qwen_with_openai_compatible()
    
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"   DashScope专用包: {'✅' if dashscope_ok else '❌'}")
    print(f"   OpenAI兼容模式: {'✅' if openai_compatible_ok else '❌'}")
    
    if not dashscope_ok:
        print("\n💡 安装DashScope包:")
        print("   pip install llama-index-llms-dashscope")
    
    return 0 if (dashscope_ok or openai_compatible_ok) else 1

if __name__ == "__main__":
    sys.exit(main())