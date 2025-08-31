# MarkItDown Test Suite

This directory contains the test suite for the MarkItDown project.

## Directory Structure

- `unit/` - Unit tests for individual components
- `integration/` - Integration tests for end-to-end functionality
- `performance/` - Performance and stress tests
- `data/` - Test data files (if needed)

## Running Tests

### Run all tests
```bash
pytest test/
```

### Run specific test categories
```bash
# Unit tests only
pytest test/unit/

# Integration tests only
pytest test/integration/

# Performance tests only
pytest test/performance/
```

### Run with coverage
```bash
pytest test/ --cov=packages/markitdown/src/markitdown --cov-report=html
```

## Test Configuration

The test suite uses `conftest.py` for shared fixtures and configuration. Key fixtures include:

- `test_data_dir` - Path to test data directory
- `output_dir` - Path to test output directory
- `input_dir` - Path to test input directory

## Adding New Tests

1. Place unit tests in `unit/`
2. Place integration tests in `integration/`
3. Place performance tests in `performance/`
4. Use descriptive test names starting with `test_`
5. Follow pytest conventions for test functions and classes
