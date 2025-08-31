#!/usr/bin/env python3
"""
Simple test to verify the test infrastructure is working.
"""

import os
import sys


def test_project_structure():
    """Test that the project structure is correct."""
    # Check that we're in the right directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))))
    
    # Check that key directories exist
    assert os.path.exists(os.path.join(project_root, 'packages'))
    assert os.path.exists(os.path.join(project_root, 'test'))
    assert os.path.exists(os.path.join(project_root, 'input'))
    assert os.path.exists(os.path.join(project_root, 'output'))
    
    print("✅ Project structure is correct")


def test_python_path():
    """Test that Python path manipulation works."""
    # Test basic path operations
    current_dir = os.path.dirname(os.path.abspath(__file__))
    assert os.path.exists(current_dir)
    
    # Test that we can add paths
    original_path = sys.path.copy()
    sys.path.insert(0, current_dir)
    assert current_dir in sys.path
    
    # Restore original path
    sys.path = original_path
    
    print("✅ Python path manipulation works")


def test_basic_imports():
    """Test that basic Python imports work."""
    import json
    import os
    import sys
    
    # Test that we can import standard library modules
    assert json is not None
    assert os is not None
    assert sys is not None
    
    print("✅ Basic imports work")
