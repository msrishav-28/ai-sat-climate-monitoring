"""
Script to fix import issues in the backend
"""

import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print(f"✅ Added {backend_dir} to Python path")
print(f"✅ Python path: {sys.path[:3]}...")

# Test imports
try:
    from src import gee_utils, inference, config
    print("✅ All local imports working!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("\nCreating __init__.py files...")
    
    # Create __init__.py files
    open(os.path.join(backend_dir, 'src', '__init__.py'), 'a').close()
    print("✅ Created src/__init__.py")

# Test again
try:
    from src import gee_utils, inference, config
    print("✅ Imports fixed!")
except Exception as e:
    print(f"❌ Still having issues: {e}")