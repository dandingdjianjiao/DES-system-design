# 使用其他LLM服务指南

## 🎯 概述

LargeRAG工具支持通过修改API基础URL来使用各种OpenAI兼容的LLM服务。系统具备智能LLM类选择功能，会根据API基础URL自动选择最优的LLM实现类，确保最佳的兼容性和性能。

## 🚀 智能LLM类选择

系统会根据配置的API基础URL自动选择合适的LLM类：

1. **专用LLM类优先**：如检测到DashScope服务，优先使用`llama_index.llms.dashscope.DashScope`类
2. **自动回退机制**：如专用类不可用，自动回退到OpenAI兼容模式
3. **透明切换**：用户无需手动选择，系统自动处理兼容性问题

**支持的智能选择**：
- **通义千问**: 
  - LLM自动使用DashScope专用类，回退到OpenAI兼容模式
  - 嵌入模型自动使用DashScopeEmbedding专用类，回退到OpenAI兼容模式
- **其他服务**: 使用OpenAI兼容模式，确保广泛兼容性

## ✅ 完全兼容的服务

### 1. 通义千问 (Qwen) ⭐

**智能特性**：系统自动检测DashScope服务，优先使用专用LLM类，确保最佳性能。

**配置方法：**
```env
# .env文件
OPENAI_API_KEY=your_dashscope_api_key
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
```

**settings.yaml修改：**
```yaml
llm:
  model: "qwen-turbo"  # 或 qwen-plus, qwen-max, qwen3-30b-a3b-instruct-2507
  api_key_env: "OPENAI_API_KEY"
  api_base_env: "OPENAI_API_BASE"

# 嵌入模型可以使用DashScope或OpenAI
embedding:
  model: "text-embedding-v1"  # DashScope嵌入模型，系统会自动选择合适的类
  api_key_env: "OPENAI_API_KEY"
  api_base_env: "OPENAI_API_BASE"
  
# 或者继续使用OpenAI嵌入（推荐混合使用）
# embedding:
#   model: "text-embedding-ada-002"
#   api_key_env: "OPENAI_EMBEDDING_KEY"  # 单独的OpenAI密钥
```

**自动LLM类选择**：
- 优先使用：`llama_index.llms.dashscope.DashScope`
- 回退模式：`llama_index.llms.openai.OpenAI`（兼容模式）

**自动嵌入模型类选择**：
- 优先使用：`llama_index.embeddings.dashscope.DashScopeEmbedding`
- 回退模式：`llama_index.embeddings.openai.OpenAIEmbedding`（兼容模式）

### 2. 智谱AI (GLM)

**配置方法：**
```env
# .env文件
OPENAI_API_KEY=your_zhipuai_api_key
OPENAI_API_BASE=https://open.bigmodel.cn/api/paas/v4
```

**settings.yaml修改：**
```yaml
llm:
  model: "glm-4"  # 或 glm-3-turbo
  api_key_env: "OPENAI_API_KEY"
  api_base_env: "OPENAI_API_BASE"
```

### 3. 月之暗面 (Kimi)

**配置方法：**
```env
# .env文件
OPENAI_API_KEY=your_moonshot_api_key
OPENAI_API_BASE=https://api.moonshot.cn/v1
```

**settings.yaml修改：**
```yaml
llm:
  model: "moonshot-v1-8k"  # 或 moonshot-v1-32k, moonshot-v1-128k
  api_key_env: "OPENAI_API_KEY"
  api_base_env: "OPENAI_API_BASE"
```

## ⚠️ 重要注意事项

### 1. 嵌入模型兼容性问题

**问题：** LlamaIndex对嵌入模型名称有严格验证，大多数第三方服务的嵌入模型名称不被识别。

**解决方案：**

#### 方案A：混合使用（推荐）
```yaml
# LLM使用第三方服务
llm:
  model: "qwen-turbo"
  api_key_env: "QWEN_API_KEY"
  api_base_env: "QWEN_API_BASE"

# 嵌入模型继续使用OpenAI
embedding:
  model: "text-embedding-ada-002"
  api_key_env: "OPENAI_API_KEY"
  # 不设置api_base_env，使用默认OpenAI服务
```

#### 方案B：使用本地嵌入模型
```bash
pip install sentence-transformers
```

然后修改代码使用HuggingFace嵌入模型：
```python
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embedding = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-zh-v1.5"  # 中文嵌入模型
)
```

### 2. 模型名称映射

不同服务的模型名称不同，需要在配置中正确设置：

| 服务 | 对话模型 | 嵌入模型 |
|------|----------|----------|
| OpenAI | gpt-4, gpt-3.5-turbo | text-embedding-ada-002 |
| 通义千问 | qwen-turbo, qwen-plus | ❌ 不兼容 |
| 智谱AI | glm-4, glm-3-turbo | ❌ 不兼容 |
| Kimi | moonshot-v1-8k | ❌ 不支持 |

### 3. 参数兼容性

某些参数可能不被所有服务支持：
- `temperature`: 大多数支持
- `max_tokens`: 大多数支持
- `top_p`: 部分支持
- `frequency_penalty`: 部分支持

## 🔧 实际配置示例

### 示例1：Qwen + OpenAI嵌入

**.env文件：**
```env
# Qwen对话模型
QWEN_API_KEY=your_dashscope_api_key
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1

# OpenAI嵌入模型
OPENAI_API_KEY=your_openai_api_key
```

**settings.yaml：**
```yaml
llm:
  model: "qwen-turbo"
  api_key_env: "QWEN_API_KEY"
  api_base_env: "QWEN_API_BASE"
  temperature: 0.1
  max_tokens: 4000

embedding:
  model: "text-embedding-ada-002"
  api_key_env: "OPENAI_API_KEY"
  # 不设置api_base_env，使用默认OpenAI
```

### 示例2：本地部署模型

**.env文件：**
```env
OPENAI_API_KEY=dummy_key  # 本地服务通常不需要真实密钥
OPENAI_API_BASE=http://localhost:8000/v1  # vLLM服务地址
```

**settings.yaml：**
```yaml
llm:
  model: "your-local-model-name"  # 根据实际部署的模型调整
  api_key_env: "OPENAI_API_KEY"
  api_base_env: "OPENAI_API_BASE"
```

## 🧪 测试配置

### 自动化测试工具

使用内置的测试工具验证配置：

```bash
# 进入LargeRAG工具目录
cd src/tools/largerag

# 运行多LLM兼容性测试
python test_alternative_llms.py
```

**测试功能**：
- 自动检测服务类型和推荐模型
- 智能LLM类选择验证
- 实际文本生成功能测试
- 配置示例和注意事项显示

### 手动测试脚本

创建测试脚本验证配置：

```python
import os
from dotenv import load_dotenv

load_dotenv()

# 系统会自动选择合适的LLM类
api_base = os.getenv("OPENAI_API_BASE")

if api_base and "dashscope.aliyuncs.com" in api_base:
    try:
        from llama_index.llms.dashscope import DashScope
        llm = DashScope(
            model_name="qwen-turbo",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1
        )
        print("✅ 使用DashScope专用LLM类")
    except ImportError:
        from llama_index.llms.openai import OpenAI
        llm = OpenAI(
            model="qwen-turbo",
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=api_base,
            temperature=0.1
        )
        print("✅ 回退到OpenAI兼容模式")
else:
    from llama_index.llms.openai import OpenAI
    llm = OpenAI(
        model="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.1
    )
    print("✅ 使用标准OpenAI LLM类")

print(f"LLM配置成功: {llm.model}")
```

## 💡 最佳实践

1. **使用自动化测试**：运行`test_alternative_llms.py`验证配置
2. **信任智能选择**：系统会自动选择最优LLM类，无需手动干预
3. **渐进式迁移**：先测试LLM，再处理嵌入模型
4. **混合使用**：LLM用第三方，嵌入用OpenAI或本地模型
5. **配置分离**：不同服务使用不同的环境变量
6. **实际功能测试**：不仅验证配置，还要测试实际文本生成能力

## 🚨 常见问题

**Q: 系统如何选择LLM类和嵌入模型类？**
A: 系统根据API基础URL自动检测服务类型，优先使用专用类（如DashScope的LLM和嵌入模型类），如不可用则自动回退到OpenAI兼容模式。

**Q: 嵌入模型现在可以直接切换了吗？**
A: 是的！系统现在支持智能嵌入模型处理。对于DashScope服务，系统会自动尝试使用`DashScopeEmbedding`专用类，如果不可用会回退到OpenAI兼容模式。其他服务仍建议使用混合配置。

**Q: 如何确认使用了哪种LLM类？**
A: 运行`test_alternative_llms.py`，系统会显示实际使用的LLM类类型。

**Q: 专用LLM类和嵌入模型类有什么优势？**
A: 专用类通常提供更好的性能优化、参数支持和错误处理，比通用兼容模式更稳定。对于DashScope，专用类还能更好地处理中文内容和特定的模型参数。

**Q: 如何处理不同服务的参数差异？**
A: 建议为不同服务创建不同的配置文件，或在代码中动态调整参数。

**Q: 本地模型如何配置？**
A: 使用vLLM、Ollama等工具部署本地模型，然后设置相应的API基础URL。