"""
LargeRAG配置管理系统

基于YAML配置文件的设置管理，支持环境变量替换和配置验证。
参考CoreRAG的配置模式实现。
"""

import os
import re
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 路径和键值替换的正则表达式
path_matcher = re.compile(r'\$\{([^}^{]+)\}')
key_matcher = re.compile(r'\{\{([^}^{]+)\}\}')

def path_constructor(loader, node):
    """YAML路径构造器，支持环境变量替换"""
    value = node.value
    match = path_matcher.match(value)
    if match:
        env_var = match.group()[2:-1]
        project_root = os.environ.get(env_var, '')
        return os.path.join(project_root, value[match.end():])
    return value

def resolve_key_references(yaml_dict):
    """解析YAML中的键值引用"""
    def _resolve_value(value, current_level_dict):
        if isinstance(value, str):
            match = key_matcher.search(value)
            if match:
                key = match.group(1).strip()
                if key in current_level_dict:
                    return value.replace(match.group(0), str(current_level_dict[key]))
                elif key in yaml_dict:
                    return value.replace(match.group(0), str(yaml_dict[key]))
        return value

    resolved_dict = {}
    for key, value in yaml_dict.items():
        if isinstance(value, dict):
            resolved_dict[key] = resolve_key_references(value)
        else:
            resolved_dict[key] = _resolve_value(value, yaml_dict)
    return resolved_dict

# 注册YAML构造器
yaml.SafeLoader.add_implicit_resolver('!path', path_matcher, None)
yaml.SafeLoader.add_constructor('!path', path_constructor)

@dataclass
class DocumentProcessingSettings:
    """文档处理配置"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_documents_per_batch: int = 100

@dataclass
class EmbeddingSettings:
    """嵌入模型配置"""
    model: str = "text-embedding-ada-002"
    api_key_env: str = "OPENAI_API_KEY"
    batch_size: int = 100
    max_retries: int = 3
    
    @property
    def api_key(self) -> str:
        """获取API密钥"""
        return os.getenv(self.api_key_env, "")

@dataclass
class VectorStoreSettings:
    """向量存储配置"""
    type: str = "chroma"
    persist_directory: str = ""
    collection_name: str = "des_literature"
    distance_metric: str = "cosine"

@dataclass
class RetrievalSettings:
    """检索配置"""
    top_k: int = 10
    similarity_threshold: float = 0.7
    rerank_enabled: bool = False
    rerank_top_k: int = 20

@dataclass
class LLMSettings:
    """LLM配置"""
    model: str = "gpt-4"
    api_key_env: str = "OPENAI_API_KEY"
    temperature: float = 0.1
    max_tokens: int = 4000
    streaming: bool = False
    
    @property
    def api_key(self) -> str:
        """获取API密钥"""
        return os.getenv(self.api_key_env, "")

@dataclass
class LoggingSettings:
    """日志配置"""
    level: str = "INFO"
    file_path: str = ""
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_file_size: str = "10MB"
    backup_count: int = 5

@dataclass
class PerformanceSettings:
    """性能配置"""
    enable_caching: bool = True
    cache_directory: str = ""
    max_cache_size: str = "1GB"
    parallel_processing: bool = True
    max_workers: int = 4

@dataclass
class SystemSettings:
    """系统配置"""
    data_directory: str = ""
    temp_directory: str = ""
    enable_metrics: bool = True
    metrics_file: str = ""

@dataclass
class LargeRAGSettings:
    """LargeRAG主配置类"""
    document_processing: DocumentProcessingSettings = field(default_factory=DocumentProcessingSettings)
    embedding: EmbeddingSettings = field(default_factory=EmbeddingSettings)
    vector_store: VectorStoreSettings = field(default_factory=VectorStoreSettings)
    retrieval: RetrievalSettings = field(default_factory=RetrievalSettings)
    llm: LLMSettings = field(default_factory=LLMSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    performance: PerformanceSettings = field(default_factory=PerformanceSettings)
    system: SystemSettings = field(default_factory=SystemSettings)
    
    @classmethod
    def from_yaml(cls, config_path: Optional[str] = None) -> 'LargeRAGSettings':
        """从YAML文件加载配置"""
        if config_path is None:
            config_path = Path(__file__).parent / "settings.yaml"
        else:
            config_path = Path(config_path)
            
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
            
        with open(config_path, "r", encoding='utf-8') as f:
            yaml_settings = yaml.safe_load(f)
            
        # 设置PROJECT_ROOT环境变量（如果存在）
        if 'PROJECT_ROOT' in os.environ:
            yaml_settings['PROJECT_ROOT'] = os.environ['PROJECT_ROOT']
            
        # 解析键值引用
        yaml_settings = resolve_key_references(yaml_settings)
        
        # 创建配置对象
        return cls._create_from_dict(yaml_settings)
    
    @classmethod
    def _create_from_dict(cls, config_dict: Dict[str, Any]) -> 'LargeRAGSettings':
        """从字典创建配置对象"""
        settings = cls()
        
        # 文档处理配置
        if 'document_processing' in config_dict:
            settings.document_processing = DocumentProcessingSettings(**config_dict['document_processing'])
            
        # 嵌入配置
        if 'embedding' in config_dict:
            settings.embedding = EmbeddingSettings(**config_dict['embedding'])
            
        # 向量存储配置
        if 'vector_store' in config_dict:
            settings.vector_store = VectorStoreSettings(**config_dict['vector_store'])
            
        # 检索配置
        if 'retrieval' in config_dict:
            settings.retrieval = RetrievalSettings(**config_dict['retrieval'])
            
        # LLM配置
        if 'llm' in config_dict:
            settings.llm = LLMSettings(**config_dict['llm'])
            
        # 日志配置
        if 'logging' in config_dict:
            settings.logging = LoggingSettings(**config_dict['logging'])
            
        # 性能配置
        if 'performance' in config_dict:
            settings.performance = PerformanceSettings(**config_dict['performance'])
            
        # 系统配置
        if 'system' in config_dict:
            settings.system = SystemSettings(**config_dict['system'])
            
        return settings
    
    def validate(self) -> bool:
        """验证配置有效性"""
        errors = []
        
        # 验证必要的目录路径
        if not self.vector_store.persist_directory:
            errors.append("vector_store.persist_directory 不能为空")
            
        if not self.system.data_directory:
            errors.append("system.data_directory 不能为空")
            
        # 验证API密钥
        if not self.embedding.api_key:
            errors.append(f"环境变量 {self.embedding.api_key_env} 未设置")
            
        if not self.llm.api_key:
            errors.append(f"环境变量 {self.llm.api_key_env} 未设置")
            
        # 验证数值范围
        if self.document_processing.chunk_size <= 0:
            errors.append("document_processing.chunk_size 必须大于0")
            
        if self.retrieval.top_k <= 0:
            errors.append("retrieval.top_k 必须大于0")
            
        if self.retrieval.similarity_threshold < 0 or self.retrieval.similarity_threshold > 1:
            errors.append("retrieval.similarity_threshold 必须在0-1之间")
            
        if errors:
            raise ValueError(f"配置验证失败:\n" + "\n".join(f"- {error}" for error in errors))
            
        return True
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.vector_store.persist_directory,
            self.system.data_directory,
            self.system.temp_directory,
            self.performance.cache_directory,
        ]
        
        for directory in directories:
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)
                
        # 确保日志文件目录存在
        if self.logging.file_path:
            Path(self.logging.file_path).parent.mkdir(parents=True, exist_ok=True)
            
        # 确保指标文件目录存在
        if self.system.metrics_file:
            Path(self.system.metrics_file).parent.mkdir(parents=True, exist_ok=True)

# 加载默认配置
try:
    config_path = Path(__file__).parent / "settings.yaml"
    with open(config_path, "r", encoding='utf-8') as f:
        yaml_settings = yaml.safe_load(f)
        if 'PROJECT_ROOT' in os.environ:
            yaml_settings['PROJECT_ROOT'] = os.environ['PROJECT_ROOT']
        yaml_settings = resolve_key_references(yaml_settings)
    
    # 创建全局配置实例
    LARGERAG_SETTINGS = LargeRAGSettings._create_from_dict(yaml_settings)
    
except Exception as e:
    print(f"警告: 加载LargeRAG配置失败: {e}")
    # 使用默认配置
    LARGERAG_SETTINGS = LargeRAGSettings()