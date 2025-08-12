# LargeRAG工具 LLM集成指南

## 问题诊断

通过Context7文档查询和实际测试，我们发现了LlamaIndex与通义千问集成的关键问题：

### 核心问题
1. **模型名称验证**: LlamaIndex的OpenAI类对模型名称有严格验证，不接受非OpenAI的模型名称
2. **API兼容性**: 虽然通义千问提供OpenAI兼容的API，但LlamaIndex的实现有额外限制

### 解决方案

#### 方案1: 使用专用DashScope集成包 (推荐)
```bash
pip install llama-index-llms-dashscope
pip install llama-index-embeddings-dashscope
```

**优势:**
- 完全兼容通义千问的所有模型
- 性能更好，功能更完整
- 支持流式输出和异步调用
- 无模型名称限制

**配置示例:**
```python
from llama_index.llms.dashscope import DashScope
from llama_index.embeddings.dashscope import DashScopeEmbedding

# 设置API密钥
os.environ["DASHSCOPE_API_KEY"] = "your_api_key"

# 创建LLM实例
llm = DashScope(
    model_name="qwen-turbo",
    api_key=api_key,
    temperature=0.1,
    max_tokens=4000
)

# 创建嵌入模型实例
embedding = DashScopeEmbedding(
    model_name="text-embedding-v1",
    api_key=api_key
)
```

#### 方案2: OpenAI兼容模式 (不推荐)
由于LlamaIndex的严格验证，此方案目前不可行。

## 配置更新

### settings.yaml
```yaml
# LLM配置
llm:
  model: "qwen-turbo"  # 使用DashScope支持的模型名称
  api_key_env: "OPENAI_API_KEY"  # 或者使用 DASHSCOPE_API_KEY
  api_base_env: "OPENAI_API_BASE"
  temperature: 0.1
  max_tokens: 4000
  streaming: false
  use_dashscope: true  # 标记使用专用集成包

# 嵌入模型配置
embedding:
  model: "text-embedding-v1"
  api_key_env: "OPENAI_API_KEY"
  api_base_env: "OPENAI_API_BASE"
  batch_size: 100
  max_retries: 3
```

### .env文件
```bash
# 通义千问API配置
OPENAI_API_KEY=sk-your-dashscope-api-key
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# 或者使用专用环境变量
DASHSCOPE_API_KEY=sk-your-dashscope-api-key
```

## 测试结果

### 成功案例
- ✅ **DashScope LLM**: qwen-turbo模型完全正常工作
- ✅ **DashScope嵌入**: text-embedding-v1模型正常工作
- ✅ **模型响应**: 生成高质量的中文回答
- ✅ **嵌入生成**: 1536维向量，支持批量处理
- ✅ **API调用**: 稳定可靠

### 失败案例
- ❌ **OpenAI兼容模式**: 模型名称验证失败
- ❌ **OpenAI兼容嵌入**: 嵌入模型名称不被接受

### 关键发现
1. **必须使用专用包**: LlamaIndex对OpenAI模型名称有严格验证
2. **嵌入模型同样需要专用包**: 不能通过OpenAI兼容模式使用
3. **配置一致性**: LLM和嵌入模型都需要使用相同的API密钥

## 其他LLM服务集成

### 智谱AI (GLM)
```bash
pip install llama-index-llms-zhipuai
```

### 月之暗面 (Kimi)
```bash
# 使用OpenAI兼容模式，但需要注意模型名称限制
```

## 最佳实践

1. **优先使用专用集成包**: 避免兼容性问题
2. **正确设置环境变量**: 确保API密钥正确配置
3. **使用正确的模型名称**: 参考官方文档
4. **测试配置**: 使用提供的测试脚本验证配置
5. **混合使用**: 不同服务可能需要不同的嵌入模型

## 测试脚本

使用以下脚本测试配置:
```bash
python test_alternative_llms.py
python test_qwen_integration.py
```

## 总结

通过使用DashScope专用集成包，我们成功解决了通义千问与LlamaIndex的集成问题。这种方案提供了最佳的兼容性和性能，是推荐的解决方案。