# MarkItDown Development Makefile
# Provides common development tasks and commands

.PHONY: help install install-dev test test-cov lint format type-check clean setup-dev start-mcp start-web start-all

# Default target
help:
	@echo "MarkItDown Development Commands"
	@echo "================================"
	@echo ""
	@echo "Setup:"
	@echo "  setup-dev     - Set up development environment"
	@echo "  install       - Install all packages"
	@echo "  install-dev   - Install all packages in development mode"
	@echo ""
	@echo "Development:"
	@echo "  start-mcp     - Start MCP server"
	@echo "  start-web     - Start web UI"
	@echo "  start-all     - Start both MCP server and web UI"
	@echo ""
	@echo "Testing:"
	@echo "  test          - Run all tests"
	@echo "  test-unit     - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-performance - Run performance tests only"
	@echo "  test-cov      - Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint          - Run linting (ruff)"
	@echo "  format        - Format code (black + isort)"
	@echo "  type-check    - Run type checking (mypy)"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean         - Clean build artifacts"
	@echo "  clean-all     - Clean everything including virtual environment"

# Setup development environment
setup-dev:
	@echo "🚀 Setting up development environment..."
	@if [ -f "scripts/setup-dev.sh" ]; then \
		chmod +x scripts/setup-dev.sh && ./scripts/setup-dev.sh; \
	else \
		echo "📦 Creating virtual environment..."; \
		uv venv; \
		echo "📥 Installing packages..."; \
		$(MAKE) install-dev; \
	fi

# Install all packages
install:
	@echo "📦 Installing all packages..."
	@cd packages/markitdown && uv pip install -e .
	@cd packages/markitdown-mcp-server && uv pip install -e .
	@cd packages/markitdown-web-ui && uv pip install -e .
	@cd packages/markitdown-sample-plugin && uv pip install -e .

# Install all packages in development mode
install-dev:
	@echo "📦 Installing all packages in development mode..."
	@cd packages/markitdown && uv pip install -e ".[dev]"
	@cd packages/markitdown-mcp-server && uv pip install -e ".[dev]"
	@cd packages/markitdown-web-ui && uv pip install -e ".[dev]"
	@cd packages/markitdown-sample-plugin && uv pip install -e ".[dev]"

# Start MCP server
start-mcp:
	@echo "🚀 Starting MCP server..."
	@cd packages/markitdown-mcp-server && python -m markitdown_mcp_server

# Start web UI
start-web:
	@echo "🌐 Starting web UI..."
	@cd packages/markitdown-web-ui && python -m markitdown_web_ui

# Start both services
start-all:
	@echo "🚀 Starting all services..."
	@echo "Starting MCP server in background..."
	@cd packages/markitdown-mcp-server && python -m markitdown_mcp_server &
	@echo "Starting web UI..."
	@cd packages/markitdown-web-ui && python -m markitdown_web_ui

# Run tests
test:
	@echo "🧪 Running all tests..."
	@python test/run_tests.py --type all

# Run unit tests
test-unit:
	@echo "🧪 Running unit tests..."
	@python test/run_tests.py --type unit

# Run integration tests
test-integration:
	@echo "🧪 Running integration tests..."
	@python test/run_tests.py --type integration

# Run performance tests
test-performance:
	@echo "🧪 Running performance tests..."
	@python test/run_tests.py --type performance

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	@python test/run_tests.py --type all --coverage

# Run linting
lint:
	@echo "🔍 Running linting..."
	@ruff check .

# Format code
format:
	@echo "🎨 Formatting code..."
	@black .
	@isort .

# Type checking
type-check:
	@echo "🔍 Running type checking..."
	@mypy packages/markitdown/src/markitdown
	@mypy packages/markitdown-mcp-server/src/markitdown_mcp_server
	@mypy packages/markitdown-web-ui/src/markitdown_web_ui

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true

# Clean everything including virtual environment
clean-all: clean
	@echo "🧹 Cleaning virtual environment..."
	@rm -rf .venv 2>/dev/null || true
	@rm -rf packages/*/dist 2>/dev/null || true
	@rm -rf packages/*/build 2>/dev/null || true

# Development workflow
dev: format lint type-check test

# Quick start for development
quick-start: setup-dev start-all
