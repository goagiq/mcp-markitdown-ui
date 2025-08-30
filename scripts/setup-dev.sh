#!/bin/bash

# MarkItDown Development Environment Setup Script
# This script sets up the development environment for the MarkItDown project

set -e

echo "🚀 Setting up MarkItDown Development Environment"

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install UV first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ UV is installed: $(uv --version)"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install all packages in development mode
echo "📥 Installing packages in development mode..."

# Install core markitdown package
echo "  📦 Installing markitdown..."
cd packages/markitdown
uv pip install -e ".[dev]"
cd ../..

# Install MCP server package
echo "  📦 Installing markitdown-mcp-server..."
cd packages/markitdown-mcp-server
uv pip install -e ".[dev]"
cd ../..

# Install web UI package
echo "  📦 Installing markitdown-web-ui..."
cd packages/markitdown-web-ui
uv pip install -e ".[dev]"
cd ../..

# Install sample plugin package
echo "  📦 Installing markitdown-sample-plugin..."
cd packages/markitdown-sample-plugin
uv pip install -e ".[dev]"
cd ../..

# Install development dependencies
echo "  📦 Installing development dependencies..."
uv pip install -r requirements-dev.txt 2>/dev/null || echo "  ⚠️  requirements-dev.txt not found, skipping..."

# Run pre-commit setup
echo "🔧 Setting up pre-commit hooks..."
pre-commit install || echo "  ⚠️  pre-commit not available, skipping..."

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p packages/markitdown-web-ui/uploads
mkdir -p packages/markitdown-web-ui/logs
mkdir -p packages/markitdown-mcp-server/logs

# Set up environment variables
echo "🔧 Setting up environment variables..."
if [ ! -f ".env" ]; then
    cat > .env << EOF
# MarkItDown Development Environment Variables

# Web UI Settings
WEB_UI_HOST=0.0.0.0
WEB_UI_PORT=8100
WEB_UI_DEBUG=true

# MCP Server Settings
MCP_SERVER_HOST=0.0.0.0
MCP_SERVER_PORT=8001

# File Upload Settings
MAX_FILE_SIZE=104857600
UPLOAD_DIR=uploads

# Security Settings
SECRET_KEY=dev-secret-key-change-in-production
CORS_ORIGINS=*

# Logging Settings
LOG_LEVEL=INFO
LOG_FILE=logs/markitdown.log
EOF
    echo "  ✅ Created .env file"
else
    echo "  ⚠️  .env file already exists"
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Start the MCP server: cd packages/markitdown-mcp-server && python -m markitdown_mcp_server"
echo "  3. Start the web UI: cd packages/markitdown-web-ui && python -m markitdown_web_ui"
echo "  4. Access the web UI at: http://localhost:8100"
echo "  5. Access the API docs at: http://localhost:8100/docs"
echo ""
echo "🔧 Development commands:"
echo "  - Run tests: pytest"
echo "  - Format code: black . && isort ."
echo "  - Lint code: ruff check ."
echo "  - Type check: mypy ."
echo ""
