#!/usr/bin/env python3
"""
Basic import test to verify the test setup is working correctly.
"""

import sys
import os


def test_basic_imports():
    """Test that basic imports work correctly."""
    # Add the correct path
    project_root = os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    markitdown_path = os.path.join(project_root, 'packages', 'markitdown', 'src')
    sys.path.insert(0, markitdown_path)
    
    # Test basic imports
    from markitdown._markitdown import MarkItDown
    print("✅ MarkItDown imported successfully")
    
    # Test creating instances
    md = MarkItDown()
    print("✅ MarkItDown instance created successfully")
    
    # Assert that imports worked
    assert md is not None
    assert hasattr(md, 'convert')


if __name__ == "__main__":
    success = test_basic_imports()
    sys.exit(0 if success else 1)
