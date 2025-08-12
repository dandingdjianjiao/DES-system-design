#!/usr/bin/env python3
"""
验证LargeRAG工具配置
"""

import os
import sys
from pathlib import Path
import yaml
from dotenv import load_dotenv

def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent / "src" / "config" / "settings.yaml"
    
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print(f"✅ 配置文件加载成功: {config_path}")
        return config
    except Exception as e:
        print(f"❌ 配置文件加载失败: {e}")
        return None

def verify_openai_config(config):
    """验证OpenAI配置"""
    print("\n🔍 验证OpenAI配置...")
    
    # 检查配置中的API密钥环境变量
    embedding_api_key_env = config.get('embedding', {}).get('api_key_env')
    llm_api_key_env = config.get('llm', {}).get('api_key_env')
    
    if not embedding_api_key_env:
        print("❌ 嵌入模型API密钥环境变量未配置")
        return False
    
    if not llm_api_key_env:
        print("❌ LLM API密钥环境变量未配置")
        return False
    
    print(f"✅ 嵌入模型API密钥环境变量: {embedding_api_key_env}")
    print(f"✅ LLM API密钥环境变量: {llm_api_key_env}")
    
    # 检查环境变量是否设置
    load_dotenv()  # 加载.env文件
    
    embedding_api_key = os.getenv(embedding_api_key_env)
    llm_api_key = os.getenv(llm_api_key_env)
    
    if not embedding_api_key:
        print(f"⚠️  环境变量 {embedding_api_key_env} 未设置")
        print("   请在.env文件中设置或通过环境变量设置")
        return False
    
    if not llm_api_key:
        print(f"⚠️  环境变量 {llm_api_key_env} 未设置")
        print("   请在.env文件中设置或通过环境变量设置")
        return False
    
    print(f"✅ {embedding_api_key_env} 已设置")
    print(f"✅ {llm_api_key_env} 已设置")
    
    return True

def verify_chroma_config(config):
    """验证Chroma配置"""
    print("\n🔍 验证Chroma向量数据库配置...")
    
    vector_store_config = config.get('vector_store', {})
    
    if vector_store_config.get('type') != 'chroma':
        print("❌ 向量存储类型不是chroma")
        return False
    
    persist_directory = vector_store_config.get('persist_directory')
    collection_name = vector_store_config.get('collection_name')
    
    if not persist_directory:
        print("❌ Chroma持久化目录未配置")
        return False
    
    if not collection_name:
        print("❌ Chroma集合名称未配置")
        return False
    
    print(f"✅ 向量存储类型: {vector_store_config.get('type')}")
    print(f"✅ 持久化目录: {persist_directory}")
    print(f"✅ 集合名称: {collection_name}")
    print(f"✅ 距离度量: {vector_store_config.get('distance_metric', 'cosine')}")
    
    return True

def verify_directories(config):
    """验证目录配置"""
    print("\n🔍 验证目录配置...")
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent.parent
    
    directories_to_check = [
        ('data_directory', config.get('system', {}).get('data_directory')),
        ('temp_directory', config.get('system', {}).get('temp_directory')),
        ('cache_directory', config.get('performance', {}).get('cache_directory')),
        ('persist_directory', config.get('vector_store', {}).get('persist_directory')),
    ]
    
    all_good = True
    
    for dir_name, dir_path in directories_to_check:
        if not dir_path:
            print(f"❌ {dir_name} 未配置")
            all_good = False
            continue
        
        # 替换${PROJECT_ROOT}占位符
        if '${PROJECT_ROOT}' in dir_path:
            actual_path = Path(dir_path.replace('${PROJECT_ROOT}', str(project_root)))
        else:
            actual_path = Path(dir_path)
        
        print(f"✅ {dir_name}: {actual_path}")
        
        # 创建目录（如果不存在）
        try:
            actual_path.mkdir(parents=True, exist_ok=True)
            print(f"   📁 目录已创建/存在")
        except Exception as e:
            print(f"   ❌ 无法创建目录: {e}")
            all_good = False
    
    return all_good

def main():
    """主验证函数"""
    print("🔍 验证LargeRAG工具配置...")
    print("=" * 60)
    
    # 加载配置
    config = load_config()
    if not config:
        return 1
    
    # 验证各个组件
    openai_ok = verify_openai_config(config)
    chroma_ok = verify_chroma_config(config)
    dirs_ok = verify_directories(config)
    
    print("\n" + "=" * 60)
    print("📊 配置验证结果:")
    print(f"   OpenAI配置: {'✅' if openai_ok else '❌'}")
    print(f"   Chroma配置: {'✅' if chroma_ok else '❌'}")
    print(f"   目录配置: {'✅' if dirs_ok else '❌'}")
    
    if openai_ok and chroma_ok and dirs_ok:
        print("\n🎉 所有配置验证成功！")
        return 0
    else:
        print("\n⚠️  部分配置存在问题，请检查")
        return 1

if __name__ == "__main__":
    sys.exit(main())