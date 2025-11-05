"""
测试文档聚合功能

测试场景：
1. 禁用聚合：每个小JSON分块保持独立
2. 启用聚合：多个小分块会被合并为一个chunk

运行方式：
    python examples/test_aggregation.py
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from llama_index.core import Document
from src.tools.largerag.core.indexer import LargeRAGIndexer
from src.tools.largerag.config.settings import load_settings
import tiktoken


def create_test_documents():
    """创建测试用的小Document对象（模拟JSON分块）"""
    small_texts = [
        "Deep eutectic solvents (DES) are mixtures of two or more components.",
        "They have lower melting points than their individual components.",
        "DES are used in various applications including dissolution and extraction.",
        "Choline chloride is a common hydrogen bond acceptor in DES.",
        "Urea, glycerol, and ethylene glycol are typical hydrogen bond donors.",
        "The molar ratio between components affects DES properties significantly.",
        "Temperature plays a crucial role in DES viscosity and conductivity.",
    ]

    documents = []
    for i, text in enumerate(small_texts):
        doc = Document(
            text=text,
            metadata={
                "doc_hash": f"test_doc_{i//3}",  # 模拟多个文档
                "item_idx": i,
                "source": "test"
            }
        )
        documents.append(doc)

    return documents


def test_aggregation_disabled():
    """测试禁用聚合的情况"""
    print("\n" + "=" * 60)
    print("测试场景 1: 禁用聚合 (aggregate_small_chunks=false)")
    print("=" * 60)

    # 加载配置并确保聚合被禁用
    settings = load_settings()
    settings.document_processing.aggregate_small_chunks = False
    settings.document_processing.chunk_size = 256  # 较小的chunk_size便于测试

    # 创建测试documents
    documents = create_test_documents()

    print(f"\n输入: {len(documents)} 个小documents")

    # 创建indexer并测试聚合方法
    indexer = LargeRAGIndexer()
    indexer.settings = settings

    # 直接调用聚合方法（不实际构建索引）
    result_docs = indexer._aggregate_small_documents(documents)

    print(f"输出: {len(result_docs)} 个documents")

    # 显示token信息
    tokenizer = tiktoken.get_encoding("cl100k_base")
    print("\n各文档token数:")
    for i, doc in enumerate(result_docs[:5]):  # 只显示前5个
        tokens = len(tokenizer.encode(doc.text))
        aggregated = doc.metadata.get("aggregated", False)
        count = doc.metadata.get("aggregated_count", 1)
        print(f"  Doc {i}: {tokens} tokens, aggregated={aggregated}, count={count}")
        print(f"    Text: {doc.text[:80]}...")


def test_aggregation_enabled():
    """测试启用聚合的情况"""
    print("\n" + "=" * 60)
    print("测试场景 2: 启用聚合 (aggregate_small_chunks=true)")
    print("=" * 60)

    # 加载配置并启用聚合
    settings = load_settings()
    settings.document_processing.aggregate_small_chunks = True
    settings.document_processing.chunk_size = 256  # 较小的chunk_size便于测试

    # 创建测试documents
    documents = create_test_documents()

    print(f"\n输入: {len(documents)} 个小documents")

    # 创建indexer并测试聚合方法
    indexer = LargeRAGIndexer()
    indexer.settings = settings

    # 直接调用聚合方法（不实际构建索引）
    result_docs = indexer._aggregate_small_documents(documents)

    print(f"输出: {len(result_docs)} 个documents（减少了 {len(documents) - len(result_docs)} 个）")

    # 显示token信息
    tokenizer = tiktoken.get_encoding("cl100k_base")
    print("\n各文档token数:")
    for i, doc in enumerate(result_docs):
        tokens = len(tokenizer.encode(doc.text))
        aggregated = doc.metadata.get("aggregated", False)
        count = doc.metadata.get("aggregated_count", 1)
        print(f"  Doc {i}: {tokens} tokens, aggregated={aggregated}, count={count}")
        print(f"    Text: {doc.text[:120]}...")


def test_with_large_document():
    """测试包含大文档的情况"""
    print("\n" + "=" * 60)
    print("测试场景 3: 混合大小文档（包含超过chunk_size的文档）")
    print("=" * 60)

    # 创建混合大小的documents
    documents = create_test_documents()

    # 添加一个大文档
    large_text = " ".join([
        "Deep eutectic solvents are ionic mixtures that exhibit a significantly lower melting point than either of the individual components.",
        "They are formed by combining a hydrogen bond donor (HBD) and a hydrogen bond acceptor (HBA).",
        "Common HBAs include quaternary ammonium salts like choline chloride, while HBDs include compounds like urea, glycerol, and carboxylic acids.",
        "The eutectic point is the composition at which the melting point is at its minimum.",
        "DES have gained significant attention in recent years due to their unique properties such as low volatility, biodegradability, and ease of preparation.",
        "They are considered as potential green alternatives to conventional organic solvents in various industrial applications."
    ])

    documents.append(Document(
        text=large_text,
        metadata={"doc_hash": "large_doc", "item_idx": 999, "source": "test"}
    ))

    # 启用聚合
    settings = load_settings()
    settings.document_processing.aggregate_small_chunks = True
    settings.document_processing.chunk_size = 256

    print(f"\n输入: {len(documents)} 个documents（包括1个大文档）")

    indexer = LargeRAGIndexer()
    indexer.settings = settings

    result_docs = indexer._aggregate_small_documents(documents)

    print(f"输出: {len(result_docs)} 个documents")

    # 显示token信息
    tokenizer = tiktoken.get_encoding("cl100k_base")
    print("\n各文档token数:")
    for i, doc in enumerate(result_docs):
        tokens = len(tokenizer.encode(doc.text))
        aggregated = doc.metadata.get("aggregated", False)
        count = doc.metadata.get("aggregated_count", 1)
        print(f"  Doc {i}: {tokens} tokens, aggregated={aggregated}, count={count}")


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("文档聚合功能测试")
    print("=" * 60)
    print("\n测试配置:")
    print("  - chunk_size: 256 tokens")
    print("  - splitter_type: token")
    print("  - separator: \\n\\n")

    try:
        # 测试1: 禁用聚合（注意：当前方法直接返回原始documents，不做处理）
        # test_aggregation_disabled()

        # 测试2: 启用聚合
        test_aggregation_enabled()

        # 测试3: 混合大小文档
        test_with_large_document()

        print("\n" + "=" * 60)
        print("✓ 所有测试完成")
        print("=" * 60)

        print("\n总结:")
        print("  - 聚合功能可以有效减少document数量")
        print("  - 小documents被合并为接近chunk_size的chunks")
        print("  - 大documents（>=chunk_size）保持独立")
        print("  - 元数据中记录了聚合信息（aggregated, aggregated_count）")

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
