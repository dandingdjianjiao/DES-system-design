"""
Complete CoreRAG Initialization Diagnosis Script

This script performs step-by-step diagnosis of CoreRAG adapter initialization
to identify the exact failure point.
"""
import sys
from pathlib import Path
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=" * 80)
print("CoreRAG Initialization Diagnosis")
print("=" * 80)

# Step 1: Environment check
print("\n[Step 1] Environment Variables")
print("-" * 80)
print(f"PROJECT_ROOT: {os.environ.get('PROJECT_ROOT', '(not set)')}")
print(f"OPENAI_API_KEY: {'✓ set' if os.environ.get('OPENAI_API_KEY') else '✗ not set'}")
print(f"DASHSCOPE_API_KEY: {'✓ set' if os.environ.get('DASHSCOPE_API_KEY') else '✗ not set'}")

# Step 2: Path setup
print("\n[Step 2] Path Setup")
print("-" * 80)
sys.path.insert(0, str(Path(__file__).parent.parent))
print(f"Added to sys.path: {Path(__file__).parent.parent}")

from dotenv import load_dotenv
load_dotenv()
print("✓ Loaded .env file")

# Step 3: Import corerag_adapter
print("\n[Step 3] Import CoreRAG Adapter Module")
print("-" * 80)
try:
    from tools.corerag_adapter import CoreRAGAdapter, CORERAG_AVAILABLE
    print(f"✓ Import successful")
    print(f"CORERAG_AVAILABLE: {CORERAG_AVAILABLE}")

    if not CORERAG_AVAILABLE:
        print("\n⚠️  CORERAG_AVAILABLE = False")
        print("This means CoreRAG dependencies could not be imported.")
        print("\nPossible reasons:")
        print("  1. config.settings import failed")
        print("  2. QueryManager import failed")
        print("  3. owlready2 not installed")
        print("\nTrying manual imports to identify the issue...")

        # Try importing each component
        print("\n  Testing: import config.settings")
        try:
            # Add corerag to path first
            corerag_path = Path(__file__).parent.parent.parent / "tools" / "corerag"
            sys.path.insert(0, str(corerag_path))
            os.environ['PROJECT_ROOT'] = str(corerag_path) + os.sep

            from config.settings import ONTOLOGY_SETTINGS
            print(f"    ✓ config.settings imported")
            print(f"    ONTOLOGY_SETTINGS type: {type(ONTOLOGY_SETTINGS)}")
            print(f"    ontology_file_name: {ONTOLOGY_SETTINGS.ontology_file_name}")
        except Exception as e:
            print(f"    ✗ FAILED: {e}")

        print("\n  Testing: import QueryManager")
        try:
            from autology_constructor.idea.query_team.query_manager import QueryManager
            print(f"    ✓ QueryManager imported")
        except Exception as e:
            print(f"    ✗ FAILED: {e}")

        sys.exit(1)

except ImportError as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Create adapter instance
print("\n[Step 4] Create CoreRAG Adapter Instance")
print("-" * 80)
try:
    print("Creating adapter with max_workers=1...")
    adapter = CoreRAGAdapter(max_workers=1)
    print("✓ Adapter instance created")
    print(f"  initialized: {adapter.initialized}")
    print(f"  manager: {adapter.manager}")

    if not adapter.initialized:
        print("\n⚠️  Adapter created but not initialized")
        print("Check logs above for initialization errors")

except Exception as e:
    print(f"✗ Adapter creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Check status
print("\n[Step 5] Check Adapter Status")
print("-" * 80)
try:
    status = adapter.get_status()
    print(f"Status: {status}")

    if status["status"] == "ready":
        print("\n✅ SUCCESS: CoreRAG adapter is ready!")
    elif status["status"] == "not_initialized":
        print("\n❌ FAILED: Adapter not initialized")
        print(f"Message: {status.get('message', 'N/A')}")
        print("\nDebugging info:")
        print(f"  adapter.initialized: {adapter.initialized}")
        print(f"  adapter.manager: {adapter.manager}")
    else:
        print(f"\n⚠️  Unexpected status: {status['status']}")
        print(f"Message: {status.get('message', 'N/A')}")

except Exception as e:
    print(f"✗ Status check failed: {e}")
    import traceback
    traceback.print_exc()

# Step 6: Detailed diagnostics if failed
if not adapter.initialized:
    print("\n[Step 6] Detailed Diagnostics")
    print("-" * 80)

    print("\n1. Check if ONTOLOGY_SETTINGS was loaded:")
    try:
        corerag_path = Path(__file__).parent.parent.parent / "tools" / "corerag"
        sys.path.insert(0, str(corerag_path))
        os.environ['PROJECT_ROOT'] = str(corerag_path) + os.sep

        from config.settings import ONTOLOGY_SETTINGS
        print(f"  ✓ ONTOLOGY_SETTINGS loaded")
        print(f"  directory_path: {ONTOLOGY_SETTINGS.directory_path}")
        print(f"  ontology_file_name: {ONTOLOGY_SETTINGS.ontology_file_name}")

        # Check if file exists
        ontology_file = Path(ONTOLOGY_SETTINGS.directory_path) / ONTOLOGY_SETTINGS.ontology_file_name
        print(f"  ontology file exists: {ontology_file.exists()}")
        if ontology_file.exists():
            print(f"  ontology file size: {ontology_file.stat().st_size / 1024 / 1024:.2f} MB")

    except Exception as e:
        print(f"  ✗ FAILED: {e}")

    print("\n2. Try creating QueryManager manually:")
    try:
        from autology_constructor.idea.query_team.query_manager import QueryManager
        from config.settings import ONTOLOGY_SETTINGS

        print("  Creating QueryManager...")
        manager = QueryManager(
            max_workers=1,
            ontology_settings=ONTOLOGY_SETTINGS,
            staggered_start=False
        )
        print("  ✓ QueryManager created")

        print("  Starting QueryManager...")
        manager.start()
        print("  ✓ QueryManager started")

        print("\n✅ Manual QueryManager creation succeeded!")
        print("This means the issue is in the CoreRAGAdapter.__init__() exception handling.")

        manager.stop()

    except Exception as e:
        print(f"  ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()

        print("\n📋 Root cause identified:")
        print(f"  {type(e).__name__}: {str(e)}")

print("\n" + "=" * 80)
print("Diagnosis Complete")
print("=" * 80)
