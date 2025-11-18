"""
Debug script to test CoreRAG imports
"""
import sys
from pathlib import Path
import os

print("=" * 60)
print("Debugging CoreRAG Import Issue")
print("=" * 60)

# Show current working directory
print(f"\nCurrent working directory: {os.getcwd()}")

# Calculate corerag_path the same way as corerag_adapter.py
print(f"\n__file__ = {__file__}")
print(f"Path(__file__).parent = {Path(__file__).parent}")
print(f"Path(__file__).parent.parent = {Path(__file__).parent.parent}")
print(f"Path(__file__).parent.parent.parent = {Path(__file__).parent.parent.parent}")

corerag_path = Path(__file__).parent.parent.parent / "tools" / "corerag"
print(f"\nCalculated corerag_path: {corerag_path}")
print(f"corerag_path exists: {corerag_path.exists()}")

# Check what's in corerag directory
if corerag_path.exists():
    print(f"\nContents of corerag_path:")
    for item in corerag_path.iterdir():
        print(f"  - {item.name}")

# Add to sys.path
sys.path.insert(0, str(corerag_path))
print(f"\nAdded to sys.path: {corerag_path}")

# Show sys.path
print(f"\nsys.path (first 5 entries):")
for i, path in enumerate(sys.path[:5]):
    print(f"  {i}: {path}")

# Try different import approaches
print("\n" + "=" * 60)
print("Testing Import Approaches")
print("=" * 60)

print("\nApproach 1: from config.settings import ONTOLOGY_SETTINGS")
try:
    from config.settings import ONTOLOGY_SETTINGS
    print(f"  ✓ SUCCESS")
    print(f"  ONTOLOGY_SETTINGS type: {type(ONTOLOGY_SETTINGS)}")
except ImportError as e:
    print(f"  ✗ FAILED: {e}")

print("\nApproach 2: from config import settings")
try:
    from config import settings
    print(f"  ✓ SUCCESS")
    print(f"  settings module: {settings}")
    if hasattr(settings, 'ONTOLOGY_SETTINGS'):
        print(f"  ONTOLOGY_SETTINGS found: {type(settings.ONTOLOGY_SETTINGS)}")
except ImportError as e:
    print(f"  ✗ FAILED: {e}")

print("\nApproach 3: import config.settings")
try:
    import config.settings
    print(f"  ✓ SUCCESS")
    print(f"  config.settings module: {config.settings}")
except ImportError as e:
    print(f"  ✗ FAILED: {e}")

# Check if config has __init__.py
config_path = corerag_path / "config"
config_init = config_path / "__init__.py"
print(f"\nconfig directory exists: {config_path.exists()}")
print(f"config/__init__.py exists: {config_init.exists()}")
if config_path.exists():
    print(f"\nContents of config directory:")
    for item in config_path.iterdir():
        print(f"  - {item.name}")
