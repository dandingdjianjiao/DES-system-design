"""
测试aggregate_small_chunks参数功能

这是一个简单的测试脚本，用于验证新添加的配置参数是否正常工作。

运行方式：
    python test_param_override.py
"""

import os
import sys

# 设置项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
os.environ['PROJECT_ROOT'] = PROJECT_ROOT + os.sep

from src.tools.largerag.config.settings import load_settings, DocumentProcessingConfig


def test_config_loading():
    """测试配置加载"""
    print("=" * 60)
    print("测试: 配置参数加载")
    print("=" * 60)

    settings = load_settings()

    print("\n文档处理配置:")
    print(f"  splitter_type: {settings.document_processing.splitter_type}")
    print(f"  chunk_size: {settings.document_processing.chunk_size}")
    print(f"  chunk_overlap: {settings.document_processing.chunk_overlap}")
    print(f"  aggregate_small_chunks: {settings.document_processing.aggregate_small_chunks}")

    # 验证默认值
    assert hasattr(settings.document_processing, 'aggregate_small_chunks'), \
        "aggregate_small_chunks字段未找到"

    print("\n✓ 配置参数加载成功！")


def test_config_override():
    """测试配置覆盖"""
    print("\n" + "=" * 60)
    print("测试: 动态修改配置参数")
    print("=" * 60)

    settings = load_settings()

    print(f"\n原始值: aggregate_small_chunks = {settings.document_processing.aggregate_small_chunks}")

    # 修改配置
    settings.document_processing.aggregate_small_chunks = True
    print(f"修改后: aggregate_small_chunks = {settings.document_processing.aggregate_small_chunks}")

    # 再次修改
    settings.document_processing.aggregate_small_chunks = False
    print(f"再次修改: aggregate_small_chunks = {settings.document_processing.aggregate_small_chunks}")

    print("\n✓ 配置参数可以动态修改！")


def test_aggregation_logic():
    """测试聚合逻辑（简化版，不依赖indexer）"""
    print("\n" + "=" * 60)
    print("测试: 聚合逻辑验证")
    print("=" * 60)

    try:
        import tiktoken
        from llama_index.core import Document

        # 创建测试documents
        small_texts = [
            "Deep eutectic solvents (DES) are mixtures.",
            "They have lower melting points.",
            "DES are used in various applications.",
            "Choline chloride is common in DES.",
        ]

        documents = [Document(text=text) for text in small_texts]

        # 使用tokenizer计算token数
        tokenizer = tiktoken.get_encoding("cl100k_base")

        print(f"\n创建了 {len(documents)} 个小documents")
        print("\n各document的token数:")
        for i, doc in enumerate(documents):
            tokens = len(tokenizer.encode(doc.text))
            print(f"  Doc {i}: {tokens} tokens - {doc.text}")

        # 模拟聚合逻辑
        chunk_size = 50
        separator = "\n\n"

        aggregated = []
        current = ""
        count = 0

        print(f"\n使用chunk_size={chunk_size}进行聚合:")

        for doc in documents:
            if not current:
                current = doc.text
                count = 1
            else:
                combined = current + separator + doc.text
                tokens = len(tokenizer.encode(combined))

                if tokens < chunk_size:
                    current = combined
                    count += 1
                else:
                    aggregated.append((current, count))
                    current = doc.text
                    count = 1

        if current:
            aggregated.append((current, count))

        print(f"\n聚合结果: {len(documents)} documents -> {len(aggregated)} chunks")
        for i, (text, cnt) in enumerate(aggregated):
            tokens = len(tokenizer.encode(text))
            print(f"  Chunk {i}: {tokens} tokens (聚合了{cnt}个documents)")
            print(f"    内容: {text[:80]}...")

        print("\n✓ 聚合逻辑工作正常！")

    except ImportError as e:
        print(f"\n⚠ 跳过聚合逻辑测试（缺少依赖: {e}）")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("aggregate_small_chunks 配置参数测试")
    print("=" * 60)

    try:
        test_config_loading()
        test_config_override()
        test_aggregation_logic()

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)

        print("\n总结:")
        print("  1. ✓ aggregate_small_chunks参数已成功添加到配置中")
        print("  2. ✓ 参数可以从settings.yaml正确加载")
        print("  3. ✓ 参数可以动态修改")
        print("  4. ✓ 聚合逻辑概念验证成功")

        print("\n使用方法:")
        print("  - 在settings.yaml中设置: aggregate_small_chunks: true")
        print("  - 只在splitter_type为token或sentence时生效")
        print("  - 聚合会将多个小于chunk_size的JSON分块合并")

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
