#!/usr/bin/env python3
"""
测试LargeRAG工具对不同LLM服务的兼容性
"""

import os
import sys
import yaml
from pathlib import Path
from dotenv import load_dotenv

def load_settings():
    """加载settings.yaml配置文件"""
    settings_path = Path(__file__).parent / "src" / "config" / "settings.yaml"
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ 无法加载配置文件: {e}")
        return None

def test_openai_compatible_service():
    """测试OpenAI兼容服务配置"""
    print("🔍 测试OpenAI兼容服务配置...")
    
    # 加载环境变量
    load_dotenv()
    
    # 加载配置文件
    settings = load_settings()
    if not settings:
        return False
    
    # 从配置文件获取模型信息
    llm_config = settings.get('llm', {})
    embedding_config = settings.get('embedding', {})
    
    llm_model = llm_config.get('model', 'gpt-3.5-turbo')
    embedding_model = embedding_config.get('model', 'text-embedding-ada-002')
    
    # 获取API配置
    api_key_env = llm_config.get('api_key_env', 'OPENAI_API_KEY')
    api_base_env = llm_config.get('api_base_env', 'OPENAI_API_BASE')
    
    api_key = os.getenv(api_key_env)
    api_base = os.getenv(api_base_env)
    
    if not api_key:
        print(f"⚠️  {api_key_env}未设置，跳过测试")
        return True
    
    print(f"📋 配置文件中的模型设置:")
    print(f"   LLM模型: {llm_model}")
    print(f"   嵌入模型: {embedding_model}")
    print(f"   温度: {llm_config.get('temperature', 0.1)}")
    print(f"   最大令牌: {llm_config.get('max_tokens', 4000)}")
    
    try:
        from llama_index.llms.openai import OpenAI
        from llama_index.embeddings.openai import OpenAIEmbedding
        
        # 配置参数（使用配置文件中的值）
        llm_kwargs = {
            "api_key": api_key,
            "temperature": llm_config.get('temperature', 0.1),
            "max_tokens": llm_config.get('max_tokens', 4000),
        }
        
        embedding_kwargs = {
            "api_key": api_key,
        }
        
        # 如果设置了自定义API基础URL
        if api_base:
            llm_kwargs["api_base"] = api_base
            embedding_kwargs["api_base"] = api_base
            print(f"✅ 使用自定义API基础URL: {api_base}")
        else:
            print("✅ 使用默认OpenAI API")
        
        # 根据API基础URL推断服务类型
        service_info = detect_service_type(api_base)
        print(f"✅ 检测到服务类型: {service_info['name']}")
        
        # 创建LLM实例（使用配置文件中的模型）
        try:
            llm = OpenAI(
                model=llm_model,
                **llm_kwargs
            )
            print(f"✅ LLM实例创建成功: {llm.model}")
        except Exception as e:
            print(f"⚠️  LLM实例创建失败: {e}")
            print("   可能需要调整模型名称或使用专用的LLM集成包")
        
        # 创建嵌入模型实例
        try:
            # 根据API基础URL选择合适的嵌入模型类
            if api_base and "dashscope.aliyuncs.com" in api_base:
                # 使用DashScope专用的嵌入模型类
                try:
                    from llama_index.embeddings.dashscope import DashScopeEmbedding
                    
                    # 设置DashScope API密钥
                    os.environ["DASHSCOPE_API_KEY"] = api_key
                    
                    embedding = DashScopeEmbedding(
                        model_name=embedding_model,
                        api_key=api_key
                    )
                    print(f"✅ DashScope嵌入模型实例创建成功: {embedding_model}")
                    
                except ImportError:
                    print("⚠️  DashScope嵌入模型包未安装，尝试使用OpenAI兼容模式")
                    embedding = OpenAIEmbedding(
                        model=embedding_model,
                        **embedding_kwargs
                    )
                    print(f"✅ 嵌入模型实例创建成功: {embedding.model_name}")
            else:
                # 使用标准OpenAI嵌入模型
                embedding = OpenAIEmbedding(
                    model=embedding_model,
                    **embedding_kwargs
                )
                print(f"✅ 嵌入模型实例创建成功: {embedding.model_name}")
                
        except Exception as e:
            print(f"⚠️  嵌入模型创建失败: {e}")
            print("   建议: 使用DashScope专用嵌入包或调整模型名称")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def detect_service_type(api_base):
    """根据API基础URL检测服务类型"""
    if not api_base:
        return {
            "name": "OpenAI官方",
            "llm_models": ["gpt-4", "gpt-3.5-turbo"],
            "embedding_models": ["text-embedding-ada-002", "text-embedding-3-small"]
        }
    
    api_base = api_base.lower()
    
    if "dashscope.aliyuncs.com" in api_base:
        return {
            "name": "通义千问 (Qwen)",
            "llm_models": ["qwen-turbo", "qwen-plus", "qwen-max"],
            "embedding_models": ["text-embedding-v1"]
        }
    elif "bigmodel.cn" in api_base:
        return {
            "name": "智谱AI (GLM)",
            "llm_models": ["glm-4", "glm-3-turbo"],
            "embedding_models": ["embedding-2"]
        }
    elif "moonshot.cn" in api_base:
        return {
            "name": "月之暗面 (Kimi)",
            "llm_models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
            "embedding_models": []  # Kimi主要提供对话模型
        }
    elif "localhost" in api_base or "127.0.0.1" in api_base:
        return {
            "name": "本地部署服务",
            "llm_models": ["local-model"],  # 需要根据实际部署的模型调整
            "embedding_models": ["local-embedding"]
        }
    else:
        return {
            "name": "未知兼容服务",
            "llm_models": ["gpt-3.5-turbo"],  # 使用通用模型名
            "embedding_models": ["text-embedding-ada-002"]
        }

def show_configuration_examples():
    """显示不同服务的配置示例"""
    print("\n📋 不同服务配置示例:")
    print("=" * 60)
    
    examples = [
        {
            "name": "通义千问 (Qwen)",
            "api_key": "your_dashscope_api_key",
            "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "llm_model": "qwen-turbo",
            "embedding_model": "text-embedding-v1",
            "notes": "需要在阿里云控制台获取API密钥"
        },
        {
            "name": "智谱AI (GLM)",
            "api_key": "your_zhipuai_api_key",
            "api_base": "https://open.bigmodel.cn/api/paas/v4",
            "llm_model": "glm-4",
            "embedding_model": "embedding-2",
            "notes": "需要在智谱AI开放平台注册获取密钥"
        },
        {
            "name": "月之暗面 (Kimi)",
            "api_key": "your_moonshot_api_key",
            "api_base": "https://api.moonshot.cn/v1",
            "llm_model": "moonshot-v1-8k",
            "embedding_model": "需要其他服务",
            "notes": "主要提供对话模型，嵌入需要配合其他服务"
        }
    ]
    
    for example in examples:
        print(f"\n🔧 {example['name']}:")
        print(f"   API密钥: {example['api_key']}")
        print(f"   API基础URL: {example['api_base']}")
        print(f"   推荐LLM模型: {example['llm_model']}")
        print(f"   推荐嵌入模型: {example['embedding_model']}")
        print(f"   注意事项: {example['notes']}")

def test_model_functionality():
    """测试模型的实际功能"""
    print("\n🧪 测试模型实际功能...")
    
    # 加载环境变量和配置
    load_dotenv()
    settings = load_settings()
    if not settings:
        return False
    
    llm_config = settings.get('llm', {})
    api_key = os.getenv(llm_config.get('api_key_env', 'OPENAI_API_KEY'))
    api_base = os.getenv(llm_config.get('api_base_env', 'OPENAI_API_BASE'))
    
    if not api_key:
        print("⚠️  API密钥未设置，跳过功能测试")
        return True
    
    try:
        # 根据API基础URL选择合适的LLM类
        if api_base and "dashscope.aliyuncs.com" in api_base:
            # 使用DashScope专用的LLM类
            try:
                from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
                
                # 设置DashScope API密钥
                os.environ["DASHSCOPE_API_KEY"] = api_key
                
                # 创建DashScope LLM实例
                llm = DashScope(
                    model_name=llm_config.get('model', 'qwen-turbo'),
                    api_key=api_key,
                    temperature=llm_config.get('temperature', 0.1),
                    max_tokens=500
                )
                
                print("✅ 使用DashScope专用LLM类")
                
            except ImportError:
                print("⚠️  DashScope LLM类未安装，尝试使用OpenAI兼容模式")
                # 回退到OpenAI兼容模式
                from llama_index.llms.openai import OpenAI
                
                llm = OpenAI(
                    model=llm_config.get('model', 'qwen-turbo'),
                    api_key=api_key,
                    api_base=api_base,
                    temperature=llm_config.get('temperature', 0.1),
                    max_tokens=500
                )
        else:
            # 使用标准OpenAI LLM类
            from llama_index.llms.openai import OpenAI
            
            llm_kwargs = {
                "api_key": api_key,
                "temperature": llm_config.get('temperature', 0.1),
                "max_tokens": 500,
            }
            
            if api_base:
                llm_kwargs["api_base"] = api_base
            
            llm = OpenAI(
                model=llm_config.get('model', 'gpt-3.5-turbo'),
                **llm_kwargs
            )
        
        # 测试简单的文本生成
        test_prompt = "请简单介绍一下深共熔溶剂(Deep Eutectic Solvent)的基本概念。"
        print(f"📝 测试提示: {test_prompt}")
        
        response = llm.complete(test_prompt)
        print(f"✅ 模型响应成功:")
        print(f"   响应长度: {len(response.text)} 字符")
        print(f"   响应预览: {response.text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型功能测试失败: {e}")
        print(f"   建议: 检查模型名称是否正确，或考虑安装对应的LLM集成包")
        return False

def show_current_config():
    """显示当前配置信息"""
    print("\n📋 当前配置信息:")
    print("=" * 60)
    
    settings = load_settings()
    if not settings:
        return
    
    llm_config = settings.get('llm', {})
    embedding_config = settings.get('embedding', {})
    
    print(f"LLM配置:")
    print(f"  模型: {llm_config.get('model', '未设置')}")
    print(f"  API密钥环境变量: {llm_config.get('api_key_env', '未设置')}")
    print(f"  API基础URL环境变量: {llm_config.get('api_base_env', '未设置')}")
    print(f"  温度: {llm_config.get('temperature', '未设置')}")
    print(f"  最大令牌: {llm_config.get('max_tokens', '未设置')}")
    
    print(f"\n嵌入模型配置:")
    print(f"  模型: {embedding_config.get('model', '未设置')}")
    print(f"  API密钥环境变量: {embedding_config.get('api_key_env', '未设置')}")
    print(f"  API基础URL环境变量: {embedding_config.get('api_base_env', '未设置')}")
    print(f"  批处理大小: {embedding_config.get('batch_size', '未设置')}")

def show_installation_suggestions():
    """显示安装建议"""
    print("\n� 推荐安装的L示LM集成包:")
    print("=" * 60)
    
    suggestions = [
        {
            "service": "通义千问 (DashScope)",
            "packages": [
                "pip install llama-index-llms-dashscope",
                "pip install llama-index-embeddings-dashscope"
            ],
            "env_vars": ["DASHSCOPE_API_KEY"],
            "notes": "专用集成包，性能更好，功能更完整"
        },
        {
            "service": "智谱AI (GLM)",
            "packages": [
                "pip install llama-index-llms-zhipuai"
            ],
            "env_vars": ["ZHIPUAI_API_KEY"],
            "notes": "专用集成包，支持GLM系列模型"
        },
        {
            "service": "OpenAI兼容服务",
            "packages": [
                "pip install llama-index-llms-openai"
            ],
            "env_vars": ["OPENAI_API_KEY", "OPENAI_API_BASE"],
            "notes": "通用兼容方式，但可能有模型名称限制"
        }
    ]
    
    for suggestion in suggestions:
        print(f"\n🔧 {suggestion['service']}:")
        print("   安装命令:")
        for package in suggestion['packages']:
            print(f"     {package}")
        print(f"   环境变量: {', '.join(suggestion['env_vars'])}")
        print(f"   说明: {suggestion['notes']}")

def show_yaml_config_example():
    """显示YAML配置文件修改示例"""
    print("\n📝 配置文件修改示例:")
    print("=" * 60)
    
    yaml_example = """
# 使用通义千问的配置示例
llm:
  model: "qwen-turbo"  # 改为qwen模型
  api_key_env: "OPENAI_API_KEY"
  api_base_env: "OPENAI_API_BASE"
  temperature: 0.1
  max_tokens: 4000

embedding:
  model: "text-embedding-v1"  # 改为qwen嵌入模型
  api_key_env: "OPENAI_API_KEY"
  api_base_env: "OPENAI_API_BASE"
  batch_size: 100
"""
    
    print(yaml_example)

def main():
    """主测试函数"""
    print("🔍 测试LargeRAG工具对不同LLM服务的兼容性...")
    print("=" * 60)
    
    # 显示当前配置
    show_current_config()
    
    # 测试配置兼容性
    config_ok = test_openai_compatible_service()
    
    # 测试模型功能（如果配置正确）
    functionality_ok = True
    if config_ok:
        functionality_ok = test_model_functionality()
    
    # 显示配置示例
    show_configuration_examples()
    show_yaml_config_example()
    show_installation_suggestions()
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"   配置兼容性: {'✅' if config_ok else '❌'}")
    print(f"   模型功能性: {'✅' if functionality_ok else '❌'}")
    
    print("\n💡 使用建议:")
    print("1. 优先使用专用的LLM集成包，而不是OpenAI兼容模式")
    print("2. 根据需要修改.env文件中的API密钥和基础URL")
    print("3. 在settings.yaml中调整model参数为对应服务的模型名")
    print("4. 注意不同服务的模型名称和参数可能有差异")
    print("5. 某些服务可能不支持嵌入模型，需要混合使用")
    print("6. 如果测试失败，考虑安装对应的专用集成包")
    
    return 0 if (config_ok and functionality_ok) else 1

if __name__ == "__main__":
    sys.exit(main())