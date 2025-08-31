"""
Pytest configuration for MarkItDown tests
"""

import os
import sys
import pytest

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'packages', 'markitdown', 'src'))

# Test configuration
pytest_plugins = []

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory"""
    return os.path.join(os.path.dirname(__file__), 'data')

@pytest.fixture(scope="session")
def output_dir():
    """Provide path to test output directory"""
    output_path = os.path.join(project_root, 'output')
    os.makedirs(output_path, exist_ok=True)
    return output_path

@pytest.fixture(scope="session")
def input_dir():
    """Provide path to test input directory"""
    input_path = os.path.join(project_root, 'input')
    os.makedirs(input_path, exist_ok=True)
    return input_path
