"""清除 LargeRAG 缓存的工具脚本"""
import sys
from pathlib import Path
import shutil

# 添加项目根目录到 sys.path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from src.tools.largerag.config.settings import SETTINGS

def clear_cache():
    """清除所有缓存"""
    cache_dir = Path(SETTINGS.cache.local_cache_dir)

    if not cache_dir.exists():
        print(f"✓ 缓存目录不存在，无需清除: {cache_dir}")
        return

    print(f"正在清除缓存目录: {cache_dir}")

    # 统计缓存文件
    cache_files = list(cache_dir.rglob("*.pkl"))
    total_size = sum(f.stat().st_size for f in cache_files if f.is_file())

    print(f"\n找到:")
    print(f"  - {len(cache_files)} 个缓存文件")
    print(f"  - 总大小: {total_size / (1024 * 1024):.2f} MB")

    # 确认
    response = input("\n确认删除所有缓存？(y/N): ")
    if response.lower() != 'y':
        print("已取消")
        return

    # 删除
    try:
        shutil.rmtree(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n✅ 缓存已清除！")
    except Exception as e:
        print(f"\n❌ 清除失败: {e}")

if __name__ == "__main__":
    print("=" * 80)
    print("LargeRAG 缓存清除工具")
    print("=" * 80)
    print("\n提示: 清除缓存后，下次索引构建将重新计算所有 embeddings")
    print("      这会增加时间和 API 调用次数，但确保使用最新配置\n")

    clear_cache()
