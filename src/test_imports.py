import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def test_imports():
    try:
        from src.AxisRAG import AxisRAG
        from src.cli import cli
        print("✓ Imports successful")
    except Exception as e:
        print(f"✗ Import error: {str(e)}")

if __name__ == '__main__':
    test_imports() 