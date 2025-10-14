"""
Quick test script to check if CoreRAG adapter initializes correctly
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

print("Testing CoreRAG Adapter Initialization...")
print("=" * 60)

try:
    from tools.corerag_adapter import CoreRAGAdapter

    print("\n✓ Import successful")

    print("\nCreating adapter...")
    adapter = CoreRAGAdapter(max_workers=1)

    print("✓ Adapter created")

    status = adapter.get_status()
    print(f"\n✓ Status: {status}")

    if status["status"] == "ready":
        print("\n✅ SUCCESS: CoreRAG adapter is ready!")
    else:
        print(f"\n⚠️  PARTIAL: CoreRAG initialized but status is: {status['status']}")
        print(f"   Message: {status.get('message', 'N/A')}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\nTest complete!")
