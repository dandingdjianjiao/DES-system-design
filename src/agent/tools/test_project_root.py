"""
Test script to verify PROJECT_ROOT setting timing
"""
import sys
from pathlib import Path
import os

print("=" * 60)
print("Testing PROJECT_ROOT Environment Variable Timing")
print("=" * 60)

# Step 1: Calculate corerag_path
corerag_path = Path(__file__).parent.parent.parent / "tools" / "corerag"
print(f"\nStep 1: Calculate corerag_path")
print(f"  corerag_path: {corerag_path}")
print(f"  exists: {corerag_path.exists()}")

# Step 2: Add to sys.path
sys.path.insert(0, str(corerag_path))
print(f"\nStep 2: Add to sys.path")
print(f"  Added: {corerag_path}")

# Step 3: Set PROJECT_ROOT BEFORE importing
os.environ['PROJECT_ROOT'] = str(corerag_path) + os.sep
print(f"\nStep 3: Set PROJECT_ROOT environment variable")
print(f"  PROJECT_ROOT: {os.environ['PROJECT_ROOT']}")

# Step 4: Now try to import
print(f"\nStep 4: Import config.settings")
try:
    from config.settings import ONTOLOGY_SETTINGS
    print(f"  ✓ SUCCESS!")
    print(f"  ONTOLOGY_SETTINGS type: {type(ONTOLOGY_SETTINGS)}")
    print(f"  directory_path: {ONTOLOGY_SETTINGS.directory_path}")
    print(f"  ontology_file_name: {ONTOLOGY_SETTINGS.ontology_file_name}")

    # Check if ontology file exists
    full_path = Path(ONTOLOGY_SETTINGS.directory_path) / ONTOLOGY_SETTINGS.ontology_file_name
    print(f"  Full ontology path: {full_path}")
    print(f"  File exists: {full_path.exists()}")

except Exception as e:
    print(f"  ✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
