"""
测试 reranker 过滤配置参数
验证 filter_by_rerank_score 参数的作用
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(project_root / "src" / "tools" / "largerag"))

from config.settings import SETTINGS

def test_config_loading():
    """测试配置加载"""
    print("=" * 60)
    print("配置加载测试")
    print("=" * 60)

    print(f"\n检索配置:")
    print(f"  - similarity_top_k: {SETTINGS.retrieval.similarity_top_k}")
    print(f"  - rerank_top_n: {SETTINGS.retrieval.rerank_top_n}")
    print(f"  - similarity_threshold: {SETTINGS.retrieval.similarity_threshold}")
    print(f"  - rerank_threshold: {SETTINGS.retrieval.rerank_threshold}")

    print(f"\nReranker 配置:")
    print(f"  - enabled: {SETTINGS.reranker.enabled}")
    print(f"  - model: {SETTINGS.reranker.model}")

    print("\n" + "=" * 60)
    print("过滤策略解释:")
    print("=" * 60)

    has_vector_filter = SETTINGS.retrieval.similarity_threshold > 0
    has_rerank_filter = SETTINGS.retrieval.rerank_threshold > 0

    if has_vector_filter:
        print(f"\n✓ 向量检索阶段: 过滤 cosine 相似度 < {SETTINGS.retrieval.similarity_threshold} 的文档")
    else:
        print(f"\n✗ 向量检索阶段: 不过滤（similarity_threshold = 0）")

    if SETTINGS.reranker.enabled:
        if has_rerank_filter:
            print(f"✓ Reranker 阶段: 过滤 reranker 分数 < {SETTINGS.retrieval.rerank_threshold} 的文档")
        else:
            print(f"✗ Reranker 阶段: 不过滤（rerank_threshold = 0）")
    else:
        print(f"✗ Reranker: 未启用")

    # 总结
    filter_count = sum([has_vector_filter, has_rerank_filter and SETTINGS.reranker.enabled])
    if filter_count == 0:
        print("\n=> 总计: 不进行任何过滤")
    elif filter_count == 1:
        if has_vector_filter:
            print("\n=> 总计: 一次过滤（仅向量检索）")
        else:
            print("\n=> 总计: 一次过滤（仅 Reranker）")
    else:
        print("\n=> 总计: 两次过滤（向量检索 + Reranker）")
        print(f"   - 向量检索阈值: {SETTINGS.retrieval.similarity_threshold}")
        print(f"   - Reranker 阈值: {SETTINGS.retrieval.rerank_threshold}")

    print("\n" + "=" * 60)
    print("使用建议:")
    print("=" * 60)
    print("""
1. 严格质量控制（宁缺毋滥）:
   - similarity_threshold: 0.7-0.8
   - rerank_threshold: 0.5-0.7
   - 效果: 两次过滤，返回最高质量的结果

2. 充分利用 Reranker 重排能力（推荐）:
   - similarity_threshold: 0.6-0.7  (较宽松)
   - rerank_threshold: 0.0          (不过滤)
   - 效果: 向量召回足够多候选，Reranker 重排后返回 top_n

3. 只信任 Reranker:
   - similarity_threshold: 0.0      (不过滤)
   - rerank_threshold: 0.5-0.7
   - 效果: 最大向量召回，Reranker 过滤低质量结果

4. 最大召回（不过滤）:
   - similarity_threshold: 0.0
   - rerank_threshold: 0.0
   - 效果: 只依赖 top_k 和 rerank_top_n 控制数量

注意: Reranker 分数范围通常与 cosine 相似度不同，建议设置不同的阈值
    """)


if __name__ == "__main__":
    test_config_loading()
