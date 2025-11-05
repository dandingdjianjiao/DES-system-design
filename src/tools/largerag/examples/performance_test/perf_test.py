"""
LargeRAG 性能测试脚本
====================================

测试内容：
1. 对 rag_performance_test 文件夹中的10篇文献建立索引
2. 使用 question.txt 中的10个问题测试RAG性能
3. 记录每个问题的答案、检索性能和LLM生成质量

运行方式：
    # 基本运行
    python examples/performance_test/perf_test.py              # 加载已有索引
    python examples/performance_test/perf_test.py --rebuild    # 强制重建索引

    # 查看帮助
    python examples/performance_test/perf_test.py --help       # 查看所有可用参数

    # 覆盖配置参数（测试不同配置的性能）
    python examples/performance_test/perf_test.py --similarity-top-k 30 --rerank-top-n 15
    python examples/performance_test/perf_test.py --llm-model qwen-max --llm-temperature 0.2
    python examples/performance_test/perf_test.py --chunk-size 1024 --chunk-overlap 100
    python examples/performance_test/perf_test.py --no-rerank  # 禁用 Reranker

可覆盖的配置参数：
    检索配置：
      --similarity-top-k N           向量检索召回数量
      --rerank-top-n N               Reranker 最终返回数量
      --similarity-threshold F       向量检索相似度阈值 (0-1)
      --rerank-threshold F           Reranker 分数阈值
      --no-rerank                    禁用 Reranker

    LLM 配置：
      --llm-model MODEL              LLM 模型名称
      --llm-temperature F            LLM 温度参数 (0-1)
      --llm-max-tokens N             LLM 最大生成 tokens

    文档处理配置：
      --splitter-type TYPE           分块策略 (token/semantic/sentence)
      --chunk-size N                 文档分块大小
      --chunk-overlap N              文档分块重叠大小
      --separator STR                分块分隔符
      --aggregate-small-chunks       聚合JSON文件内的所有片段
      --semantic-breakpoint-threshold F  语义断点阈值 (0-1)
      --semantic-buffer-size N       语义缓冲区大小

    向量存储配置：
      --vector-store-type TYPE       向量存储类型
      --persist-directory PATH       持久化目录
      --collection-name NAME         集合名称
      --distance-metric METRIC       距离度量 (cosine/l2/ip)

数据结构：
    src/tools/largerag/data/rag_performance_test/
    ├── 1/ ... 10/  (10篇文献文件夹)
    └── question.txt (10个测试问题)
"""

import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

# 添加项目根目录到sys.path
# perf_test.py → performance_test → examples → largerag → tools → src → PROJECT_ROOT
project_root = Path(__file__).resolve().parents[5]  # 往上5级
sys.path.insert(0, str(project_root))

from src.tools.largerag import LargeRAG
from src.tools.largerag.config.settings import SETTINGS


def print_section(title: str):
    """打印分隔线"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subsection(title: str):
    """打印子标题"""
    print(f"\n--- {title} ---")


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='LargeRAG 性能测试',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基本运行
  python perf_test.py

  # 强制重建索引
  python perf_test.py --rebuild

  # 禁用缓存（测试配置变化时推荐）
  python perf_test.py --rebuild --no-cache

  # 覆盖检索配置
  python perf_test.py --similarity-top-k 30 --rerank-top-n 15
  python perf_test.py --similarity-threshold 0.7 --rerank-threshold 0.5

  # 覆盖 LLM 配置
  python perf_test.py --llm-model qwen-max --llm-temperature 0.2

  # 覆盖文档处理配置
  python perf_test.py --chunk-size 1024 --chunk-overlap 100
  python perf_test.py --splitter-type semantic --semantic-breakpoint-threshold 0.6
  python perf_test.py --separator "\\n\\n\\n"
  python perf_test.py --aggregate-small-chunks  # 聚合JSON片段

  # 覆盖向量存储配置
  python perf_test.py --collection-name test_collection --distance-metric l2
  python perf_test.py --persist-directory /path/to/db

  # 组合多个参数
  python perf_test.py --chunk-size 768 --similarity-top-k 50 --llm-temperature 0.15

  # 禁用 Reranker
  python perf_test.py --no-rerank
        """
    )

    # 基本选项
    parser.add_argument('--rebuild', action='store_true',
                       help='强制重建索引（即使已存在）')
    parser.add_argument('--no-cache', action='store_true',
                       help='禁用缓存（确保使用最新配置重建）')

    # 检索配置参数
    retrieval_group = parser.add_argument_group('检索配置参数')
    retrieval_group.add_argument('--similarity-top-k', type=int, metavar='N',
                                help='向量检索召回数量（默认: 20）')
    retrieval_group.add_argument('--rerank-top-n', type=int, metavar='N',
                                help='Reranker 最终返回数量（默认: 10）')
    retrieval_group.add_argument('--similarity-threshold', type=float, metavar='FLOAT',
                                help='向量检索相似度阈值 0-1（0=禁用，默认: 0.8）')
    retrieval_group.add_argument('--rerank-threshold', type=float, metavar='FLOAT',
                                help='Reranker 分数阈值（0=禁用，默认: 0.0）')

    # Reranker 配置
    reranker_group = parser.add_argument_group('Reranker 配置')
    reranker_group.add_argument('--no-rerank', action='store_true',
                               help='禁用 Reranker（默认启用）')

    # LLM 配置参数
    llm_group = parser.add_argument_group('LLM 配置参数')
    llm_group.add_argument('--llm-model', type=str, metavar='MODEL',
                          help='LLM 模型名称（默认: qwen-plus）')
    llm_group.add_argument('--llm-temperature', type=float, metavar='FLOAT',
                          help='LLM 温度参数 0-1（默认: 0.1）')
    llm_group.add_argument('--llm-max-tokens', type=int, metavar='N',
                          help='LLM 最大生成 tokens（默认: 3000）')

    # 文档处理配置
    doc_group = parser.add_argument_group('文档处理配置')
    doc_group.add_argument('--splitter-type', type=str, metavar='TYPE',
                          choices=['token', 'semantic', 'sentence'],
                          help='分块策略: token/semantic/sentence（默认: token）')
    doc_group.add_argument('--chunk-size', type=int, metavar='N',
                          help='文档分块大小（默认: 512）')
    doc_group.add_argument('--chunk-overlap', type=int, metavar='N',
                          help='文档分块重叠大小（默认: 50）')
    doc_group.add_argument('--separator', type=str, metavar='STR',
                          help='分块分隔符（默认: \\n\\n）')
    doc_group.add_argument('--semantic-breakpoint-threshold', type=float, metavar='FLOAT',
                          help='语义断点阈值 0-1（默认: 0.5 → 50%%，值越高越保守，仅semantic模式）')
    doc_group.add_argument('--semantic-buffer-size', type=int, metavar='N',
                          help='语义缓冲区大小（默认: 1，仅semantic模式）')
    doc_group.add_argument('--aggregate-small-chunks', action='store_true',
                          help='聚合JSON文件内的所有片段为一个Document（默认: false）')

    # 向量存储配置
    vector_group = parser.add_argument_group('向量存储配置')
    vector_group.add_argument('--vector-store-type', type=str, metavar='TYPE',
                             help='向量存储类型（默认: chroma）')
    vector_group.add_argument('--persist-directory', type=str, metavar='PATH',
                             help='向量数据库持久化目录')
    vector_group.add_argument('--collection-name', type=str, metavar='NAME',
                             help='集合名称（默认: des_literature_v1）')
    vector_group.add_argument('--distance-metric', type=str, metavar='METRIC',
                             choices=['cosine', 'l2', 'ip'],
                             help='距离度量: cosine/l2/ip（默认: cosine）')

    args = parser.parse_args()

    # ============================================================
    # 应用命令行参数覆盖到 SETTINGS
    # ============================================================
    overrides_applied = []

    # 检索配置
    if args.similarity_top_k is not None:
        SETTINGS.retrieval.similarity_top_k = args.similarity_top_k
        overrides_applied.append(f"retrieval.similarity_top_k = {args.similarity_top_k}")

    if args.rerank_top_n is not None:
        SETTINGS.retrieval.rerank_top_n = args.rerank_top_n
        overrides_applied.append(f"retrieval.rerank_top_n = {args.rerank_top_n}")

    if args.similarity_threshold is not None:
        SETTINGS.retrieval.similarity_threshold = args.similarity_threshold
        overrides_applied.append(f"retrieval.similarity_threshold = {args.similarity_threshold}")

    if args.rerank_threshold is not None:
        SETTINGS.retrieval.rerank_threshold = args.rerank_threshold
        overrides_applied.append(f"retrieval.rerank_threshold = {args.rerank_threshold}")

    # Reranker 配置
    if args.no_rerank:
        SETTINGS.reranker.enabled = False
        overrides_applied.append(f"reranker.enabled = False")

    # 缓存配置
    if args.no_cache:
        SETTINGS.cache.enabled = False
        overrides_applied.append(f"cache.enabled = False")

    # LLM 配置
    if args.llm_model is not None:
        SETTINGS.llm.model = args.llm_model
        overrides_applied.append(f"llm.model = {args.llm_model}")

    if args.llm_temperature is not None:
        SETTINGS.llm.temperature = args.llm_temperature
        overrides_applied.append(f"llm.temperature = {args.llm_temperature}")

    if args.llm_max_tokens is not None:
        SETTINGS.llm.max_tokens = args.llm_max_tokens
        overrides_applied.append(f"llm.max_tokens = {args.llm_max_tokens}")

    # 文档处理配置
    if args.splitter_type is not None:
        SETTINGS.document_processing.splitter_type = args.splitter_type
        overrides_applied.append(f"document_processing.splitter_type = {args.splitter_type}")

    if args.chunk_size is not None:
        SETTINGS.document_processing.chunk_size = args.chunk_size
        overrides_applied.append(f"document_processing.chunk_size = {args.chunk_size}")

    if args.chunk_overlap is not None:
        SETTINGS.document_processing.chunk_overlap = args.chunk_overlap
        overrides_applied.append(f"document_processing.chunk_overlap = {args.chunk_overlap}")

    if args.separator is not None:
        SETTINGS.document_processing.separator = args.separator
        overrides_applied.append(f"document_processing.separator = {args.separator}")

    if args.semantic_breakpoint_threshold is not None:
        SETTINGS.document_processing.semantic_breakpoint_threshold = args.semantic_breakpoint_threshold
        overrides_applied.append(f"document_processing.semantic_breakpoint_threshold = {args.semantic_breakpoint_threshold}")

    if args.semantic_buffer_size is not None:
        SETTINGS.document_processing.semantic_buffer_size = args.semantic_buffer_size
        overrides_applied.append(f"document_processing.semantic_buffer_size = {args.semantic_buffer_size}")

    if args.aggregate_small_chunks:
        SETTINGS.document_processing.aggregate_small_chunks = True
        overrides_applied.append(f"document_processing.aggregate_small_chunks = True")

    # 向量存储配置
    if args.vector_store_type is not None:
        SETTINGS.vector_store.type = args.vector_store_type
        overrides_applied.append(f"vector_store.type = {args.vector_store_type}")

    if args.persist_directory is not None:
        SETTINGS.vector_store.persist_directory = args.persist_directory
        overrides_applied.append(f"vector_store.persist_directory = {args.persist_directory}")

    if args.collection_name is not None:
        SETTINGS.vector_store.collection_name = args.collection_name
        overrides_applied.append(f"vector_store.collection_name = {args.collection_name}")

    if args.distance_metric is not None:
        SETTINGS.vector_store.distance_metric = args.distance_metric
        overrides_applied.append(f"vector_store.distance_metric = {args.distance_metric}")

    print_section("LargeRAG 性能测试 - 10篇文献 + 10个问题")

    # 显示参数覆盖信息
    if overrides_applied:
        print("\n⚙️  检测到命令行参数覆盖:")
        for override in overrides_applied:
            print(f"  ✓ {override}")
        print()

    # ============================================================
    # 1. 设置测试参数
    # ============================================================
    print_section("步骤 1: 初始化测试环境")

    # 测试数据路径
    test_data_dir = Path(__file__).parent.parent.parent / "data" / "rag_performance_test"
    question_file = test_data_dir / "question.txt"

    # 使用配置中的 collection 名称（可通过命令行参数覆盖）
    # 如果用户未指定，使用默认值 "rag_perf_test_10papers"
    if not args.collection_name:
        # 用户未通过命令行指定，使用测试专用的 collection 名称
        SETTINGS.vector_store.collection_name = "rag_perf_test_10papers"
    collection_name = SETTINGS.vector_store.collection_name

    print(f"\n测试数据目录: {test_data_dir}")
    print(f"问题文件: {question_file}")
    print(f"Collection 名称: {collection_name}")

    # 检查测试数据是否存在
    if not test_data_dir.exists():
        print(f"\n✗ 错误: 测试数据目录不存在: {test_data_dir}")
        return False

    if not question_file.exists():
        print(f"\n✗ 错误: 问题文件不存在: {question_file}")
        return False

    # 统计文献数量
    literature_folders = [d for d in test_data_dir.iterdir() if d.is_dir()]
    print(f"\n✓ 检测到 {len(literature_folders)} 个文献文件夹")

    # ============================================================
    # 2. 初始化 LargeRAG（使用自定义 collection）
    # ============================================================
    print_section("步骤 2: 初始化 LargeRAG")

    print(f"\n使用自定义 collection: {collection_name}")
    print("(这样不会影响其他已有的索引)")

    start_time = time.time()
    rag = LargeRAG(collection_name=collection_name)
    init_time = time.time() - start_time

    print(f"\n✓ LargeRAG 初始化完成 (耗时: {init_time:.2f}秒)")

    # 获取当前配置参数（用于测试）
    retrieval_top_k = SETTINGS.retrieval.rerank_top_n  # 最终返回给用户的文档数
    print(f"\n当前配置参数:")
    print(f"  - 向量检索召回数: {SETTINGS.retrieval.similarity_top_k}")
    print(f"  - Reranker返回数: {SETTINGS.retrieval.rerank_top_n}")
    print(f"  - Reranker启用:   {SETTINGS.reranker.enabled}")
    print(f"  - LLM模型:        {SETTINGS.llm.model}")
    print(f"  - 温度:           {SETTINGS.llm.temperature}")
    print(f"  - 最大tokens:     {SETTINGS.llm.max_tokens}")

    # ============================================================
    # 3. 构建索引（或加载已有索引）
    # ============================================================
    print_section("步骤 3: 构建/加载索引")

    # 检查是否需要重建索引
    need_rebuild = args.rebuild  # 用户明确要求重建

    if not need_rebuild and rag.query_engine is not None:
        # 有索引，检查是否为空
        stats_temp = rag.get_stats()
        index_count = stats_temp['index_stats'].get('document_count', 0)
        if index_count == 0:
            print("\n⚠️  检测到索引为空（可能之前构建失败），将强制重建...")
            need_rebuild = True
        else:
            print(f"\n✓ 检测到已有索引（{index_count} 个节点），跳过构建步骤")
            print("  提示: 使用 --rebuild 参数可强制重建索引")

    if need_rebuild or rag.query_engine is None:
        if need_rebuild:
            print("\n🔄 强制重建索引...")
        else:
            print("\n未检测到已有索引，开始构建...")

        print(f"文献数量: {len(literature_folders)}")

        start_time = time.time()
        success = rag.index_from_folders(str(test_data_dir))
        index_time = time.time() - start_time

        if not success:
            print("\n✗ 索引构建失败")
            return False

        print(f"\n✓ 索引构建成功 (耗时: {index_time:.2f}秒 / {index_time/60:.2f}分钟)")

    # 显示索引统计信息
    stats = rag.get_stats()
    index_stats = stats['index_stats']
    doc_stats = stats['doc_processing_stats']

    print_subsection("索引统计信息")
    print(f"  Collection: {index_stats.get('collection_name', 'N/A')}")
    print(f"  索引节点数: {index_stats.get('document_count', 0)}")
    print(f"  处理文档数: {doc_stats.get('processed', 0)}")

    # ============================================================
    # 4. 读取测试问题
    # ============================================================
    print_section("步骤 4: 读取测试问题")

    with open(question_file, 'r', encoding='utf-8') as f:
        questions = [line.strip() for line in f.readlines() if line.strip()]

    print(f"\n✓ 读取到 {len(questions)} 个问题\n")

    for i, q in enumerate(questions, 1):
        print(f"  Q{i}: {q}")

    # ============================================================
    # 5. 执行测试 - 对每个问题进行查询
    # ============================================================
    print_section("步骤 5: 执行性能测试")

    results = []
    total_query_time = 0
    total_retrieval_time = 0

    print("\n开始测试...\n")

    for i, question in enumerate(questions, 1):
        print_subsection(f"问题 {i}/{len(questions)}")
        print(f"问题: {question}\n")

        # 5.1 检索相似文档（不使用LLM）
        print("  [1/2] 检索相似文档...")
        start_time = time.time()
        similar_docs = rag.get_similar_docs(question, top_k=retrieval_top_k)
        retrieval_time = time.time() - start_time
        total_retrieval_time += retrieval_time

        print(f"  ✓ 检索完成 (耗时: {retrieval_time:.2f}秒)")
        print(f"  检索到 {len(similar_docs)} 个相关文档")

        # 显示检索的文档分数
        if similar_docs:
            print(f"  相似度分数范围: {similar_docs[0]['score']:.4f} ~ {similar_docs[-1]['score']:.4f}")

        # 5.2 生成回答（使用LLM）
        print("\n  [2/2] 生成回答...")
        start_time = time.time()
        answer = rag.query(question)
        query_time = time.time() - start_time
        total_query_time += query_time

        print(f"  ✓ 回答生成完成 (耗时: {query_time:.2f}秒)")

        # 显示回答（前200字符）
        answer_preview = answer[:200] + "..." if len(answer) > 200 else answer
        print(f"\n  回答:\n  {answer_preview}\n")

        # 记录结果
        result = {
            "question_id": i,
            "question": question,
            "answer": answer,
            "retrieval_time_sec": round(retrieval_time, 2),
            "query_time_sec": round(query_time, 2),
            "num_retrieved_docs": len(similar_docs),
            "similarity_scores": [round(doc['score'], 4) for doc in similar_docs],
            "top_doc_sources": [
                {
                    "doc_hash": doc['metadata'].get('doc_hash', 'N/A')[:16],
                    "page_idx": doc['metadata'].get('page_idx', 'N/A'),
                    "score": round(doc['score'], 4)
                }
                for doc in similar_docs[:3]  # 只记录前3个文档来源
            ]
        }
        results.append(result)

    # ============================================================
    # 6. 统计测试结果
    # ============================================================
    print_section("步骤 6: 测试结果统计")

    avg_retrieval_time = total_retrieval_time / len(questions)
    avg_query_time = total_query_time / len(questions)

    print("\n📊 性能统计:")
    print(f"  总问题数:           {len(questions)}")
    print(f"  平均检索时间:       {avg_retrieval_time:.2f}秒")
    print(f"  平均查询时间:       {avg_query_time:.2f}秒")
    print(f"  总检索时间:         {total_retrieval_time:.2f}秒")
    print(f"  总查询时间:         {total_query_time:.2f}秒")

    print("\n📊 索引统计:")
    print(f"  文献数量:           {len(literature_folders)}")
    print(f"  索引节点数:         {index_stats.get('document_count', 0)}")
    print(f"  Collection:         {collection_name}")

    # ============================================================
    # 7. 保存测试结果到 JSON
    # ============================================================
    print_section("步骤 7: 保存测试结果")

    # 创建输出目录
    output_dir = Path(__file__).parent / "test_results"
    output_dir.mkdir(exist_ok=True)

    # 生成文件名（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"perf_test_{timestamp}.json"

    # 整合所有结果
    full_results = {
        "test_info": {
            "timestamp": timestamp,
            "test_data_dir": str(test_data_dir),
            "collection_name": collection_name,
            "num_literature": len(literature_folders),
            "num_questions": len(questions),
        },
        "config_parameters": asdict(SETTINGS),  # 保存所有配置参数
        "performance_summary": {
            "avg_retrieval_time_sec": round(avg_retrieval_time, 2),
            "avg_query_time_sec": round(avg_query_time, 2),
            "total_retrieval_time_sec": round(total_retrieval_time, 2),
            "total_query_time_sec": round(total_query_time, 2),
        },
        "index_stats": index_stats,
        "questions_and_answers": results,
    }

    # 保存到 JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 测试结果已保存到: {output_file}")

    # ============================================================
    # 8. 完成
    # ============================================================
    print_section("测试完成！")

    print("\n✅ 所有测试已完成")
    print(f"\n测试结果文件: {output_file}")
    print("\n可以查看 JSON 文件获取详细结果，包括:")
    print("  - 每个问题的完整回答")
    print("  - 检索性能指标（时间、相似度分数）")
    print("  - 文档来源信息（doc_hash, page_idx）")

    print("\n" + "=" * 80 + "\n")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
