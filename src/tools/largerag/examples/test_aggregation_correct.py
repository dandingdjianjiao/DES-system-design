"""
测试aggregate_small_chunks参数的正确行为

验证：
1. 不聚合：保留JSON原始分块点（每个text条目一个Document）
2. 聚合：消除JSON分块点（一个JSON文件所有text合并为一个Document）
3. Splitter如何处理这些Documents

运行方式：
    python examples/test_aggregation_correct.py
"""

import os
import sys
from pathlib import Path

# 设置项目根目录和路径
script_dir = Path(__file__).parent
largerag_dir = script_dir.parent

os.environ['PROJECT_ROOT'] = str(largerag_dir.parent.parent.parent) + os.sep
sys.path.insert(0, str(largerag_dir))

from core.document_processor import DocumentProcessor
from config.settings import load_settings

PROJECT_ROOT = Path(os.environ['PROJECT_ROOT'])


def test_document_aggregation():
    """测试DocumentProcessor的聚合功能"""

    print("=" * 80)
    print("测试: DocumentProcessor聚合功能")
    print("=" * 80)

    # 测试数据目录（使用实际文献数据）
    literature_dir = PROJECT_ROOT / "src/tools/largerag/data/literature"

    if not literature_dir.exists():
        print(f"\n错误: 找不到测试数据目录 {literature_dir}")
        return

    # 只测试一个文件夹
    test_folder = None
    for folder in literature_dir.iterdir():
        if folder.is_dir():
            test_folder = folder
            break

    if not test_folder:
        print("\n错误: 没有找到测试文件夹")
        return

    print(f"\n测试文件夹: {test_folder.name}")

    # ========== 测试1: 不聚合 ==========
    print("\n" + "-" * 80)
    print("测试1: 不聚合 (aggregate_small_chunks=False)")
    print("-" * 80)

    processor_no_agg = DocumentProcessor(
        aggregate_small_chunks=False,
        separator="\n\n"
    )

    # 测试单个JSON文件
    content_file = test_folder / "content_list_process.json"
    if content_file.exists():
        docs_no_agg = processor_no_agg._load_from_content_list(content_file, test_folder.name)

        print(f"\n结果: 生成了 {len(docs_no_agg)} 个Documents")
        print("\n前3个Documents的信息:")
        for i, doc in enumerate(docs_no_agg[:3]):
            print(f"  Doc {i}:")
            print(f"    - Text长度: {len(doc.text)} 字符")
            print(f"    - Aggregated: {doc.metadata.get('aggregated', 'N/A')}")
            print(f"    - Text预览: {doc.text[:80]}...")

    # ========== 测试2: 聚合 ==========
    print("\n" + "-" * 80)
    print("测试2: 聚合 (aggregate_small_chunks=True)")
    print("-" * 80)

    processor_agg = DocumentProcessor(
        aggregate_small_chunks=True,
        separator="\n\n"
    )

    if content_file.exists():
        docs_agg = processor_agg._load_from_content_list(content_file, test_folder.name)

        print(f"\n结果: 生成了 {len(docs_agg)} 个Documents")
        print("\nDocument信息:")
        for i, doc in enumerate(docs_agg):
            print(f"  Doc {i}:")
            print(f"    - Text长度: {len(doc.text)} 字符")
            print(f"    - Aggregated: {doc.metadata.get('aggregated', 'N/A')}")
            print(f"    - Num segments: {doc.metadata.get('num_segments', 'N/A')}")
            print(f"    - Text预览: {doc.text[:120]}...")

    # ========== 对比 ==========
    print("\n" + "=" * 80)
    print("对比总结")
    print("=" * 80)
    print(f"\n不聚合模式: {len(docs_no_agg)} 个Documents")
    print(f"聚合模式:   {len(docs_agg)} 个Documents")
    print(f"\n聚合减少了: {len(docs_no_agg) - len(docs_agg)} 个Documents")

    if len(docs_agg) > 0:
        total_chars_no_agg = sum(len(doc.text) for doc in docs_no_agg)
        total_chars_agg = sum(len(doc.text) for doc in docs_agg)

        print(f"\n总字符数:")
        print(f"  不聚合: {total_chars_no_agg} 字符")
        print(f"  聚合:   {total_chars_agg} 字符")
        print(f"  差异:   {abs(total_chars_no_agg - total_chars_agg)} 字符 "
              f"({'多了分隔符' if total_chars_agg > total_chars_no_agg else '相同'})")

    print("\n" + "=" * 80)
    print("✓ 测试完成")
    print("=" * 80)

    print("\n总结:")
    print("  1. 不聚合模式: 保留JSON原始分块点")
    print("     - 每个text条目 → 一个Document")
    print("     - 适合：需要保留文档结构时")
    print("")
    print("  2. 聚合模式: 消除JSON分块点")
    print("     - 整个JSON文件 → 一个Document")
    print("     - 适合：统一重新分块，不受JSON结构限制")
    print("")
    print("  3. 后续Splitter会根据chunk_size进一步处理这些Documents")
    print("     - token/sentence模式: 大Document会被分割")
    print("     - semantic模式: 根据语义边界分割")


def test_with_multiple_folders():
    """测试多个文件夹的聚合效果"""

    print("\n\n" + "=" * 80)
    print("测试: 多个文件夹的聚合效果")
    print("=" * 80)

    literature_dir = PROJECT_ROOT / "src/tools/largerag/data/literature"

    if not literature_dir.exists():
        print(f"\n错误: 找不到测试数据目录 {literature_dir}")
        return

    # 测试前3个文件夹
    test_folders = list(literature_dir.iterdir())[:3]

    print(f"\n测试 {len(test_folders)} 个文件夹")

    for mode, aggregate in [("不聚合", False), ("聚合", True)]:
        print(f"\n{mode}模式:")

        processor = DocumentProcessor(
            aggregate_small_chunks=aggregate,
            separator="\n\n"
        )

        total_docs = 0
        for folder in test_folders:
            if not folder.is_dir():
                continue

            content_file = folder / "content_list_process.json"
            if content_file.exists():
                docs = processor._load_from_content_list(content_file, folder.name)
                total_docs += len(docs)
                print(f"  {folder.name}: {len(docs)} documents")

        print(f"  总计: {total_docs} documents")


def main():
    """运行所有测试"""
    try:
        test_document_aggregation()
        test_with_multiple_folders()

        print("\n" + "=" * 80)
        print("✓ 所有测试完成")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
