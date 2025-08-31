# Package Management and Development Setup

This document describes the package management strategy and development environment setup for the MarkItDown project.

## 📦 Package Structure

The project is organized as a monorepo with multiple packages:

```
markitdown/
├── packages/
│   ├── markitdown/                 # Core MarkItDown library
│   ├── markitdown-mcp-server/      # MCP server for tools
│   ├── markitdown-web-ui/          # FastAPI web interface
│   ├── markitdown-sample-plugin/   # Sample plugin
│   └── markitdown-mcp/             # Legacy MCP package
├── docs/                           # Documentation
├── scripts/                        # Setup and utility scripts
├── pyproject.toml                  # Workspace configuration
├── Makefile                        # Development commands
├── requirements-dev.txt            # Development dependencies
└── .pre-commit-config.yaml         # Pre-commit hooks
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- UV package manager (recommended) or pip
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd markitdown
   ```

2. **Set up development environment:**
   ```bash
   # Using the setup script (recommended)
   ./scripts/setup-dev.sh
   
   # Or using make
   make setup-dev
   
   # Or manually
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   make install-dev
   ```

3. **Start the services:**
   ```bash
   # Start both MCP server and web UI
   make start-all
   
   # Or start individually
   make start-mcp    # MCP server on port 8001
   make start-web    # Web UI on port 8200
   ```

## 📋 Development Commands

### Setup and Installation

| Command | Description |
|---------|-------------|
| `make setup-dev` | Set up complete development environment |
| `make install` | Install all packages |
| `make install-dev` | Install all packages in development mode |

### Development Workflow

| Command | Description |
|---------|-------------|
| `make start-mcp` | Start MCP server |
| `make start-web` | Start web UI |
| `make start-all` | Start both services |
| `make dev` | Run format, lint, type-check, and test |

### Code Quality

| Command | Description |
|---------|-------------|
| `make format` | Format code with black and isort |
| `make lint` | Run linting with ruff |
| `make type-check` | Run type checking with mypy |
| `make test` | Run all tests |
| `make test-cov` | Run tests with coverage |

### Maintenance

| Command | Description |
|---------|-------------|
| `make clean` | Clean build artifacts |
| `make clean-all` | Clean everything including virtual environment |

## 🔧 Package Dependencies

### Core Dependencies

Each package has its own `pyproject.toml` with specific dependencies:

#### markitdown (Core Library)
- Core file conversion capabilities
- Plugin system
- CLI interface

#### markitdown-mcp-server
```toml
dependencies = [
  "mcp>=1.0.0",
  "fastapi-mcp>=0.4.0",
  "markitdown[all]>=0.1.3",
  "pydantic>=2.5.0",
  "fastapi>=0.104.0",
  "uvicorn[standard]>=0.24.0",
  "python-multipart>=0.0.6",
  "websockets>=12.0",
  "requests>=2.25.0",
  "aiofiles>=23.0.0",
  "python-magic>=0.4.27",
]
```

#### markitdown-web-ui
```toml
dependencies = [
  "fastapi>=0.104.0",
  "uvicorn[standard]>=0.24.0",
  "python-multipart>=0.0.6",
  "websockets>=12.0",
  "aiofiles>=23.0.0",
  "jinja2>=3.1.0",
  "python-magic>=0.4.27",
  "pydantic>=2.5.0",
  "pydantic-settings>=2.0.0",
  "markitdown[all]>=0.1.3",
  "markitdown-mcp-server>=0.1.0",
]
```

### Development Dependencies

Shared development dependencies in `requirements-dev.txt`:

```txt
# Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-xdist>=3.0.0

# HTTP testing
httpx>=0.25.0
requests>=2.25.0

# Code formatting and linting
black>=23.0.0
isort>=5.12.0
ruff>=0.1.0
flake8>=6.0.0

# Type checking
mypy>=1.0.0
types-requests>=2.31.0
types-PyYAML>=6.0.0

# Pre-commit hooks
pre-commit>=3.0.0

# Documentation
sphinx>=7.0.0
sphinx-rtd-theme>=1.3.0
myst-parser>=2.0.0

# Development tools
ipython>=8.0.0
jupyter>=1.0.0
notebook>=7.0.0

# Monitoring and debugging
rich>=13.0.0
click>=8.0.0
```

## 🛠️ Development Tools

### UV Package Manager

The project uses UV for fast dependency resolution and installation:

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Install dependencies
uv pip install -e ".[dev]"
```

### Pre-commit Hooks

Automated code quality checks run on every commit:

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Hooks include:
- Code formatting (black, isort)
- Linting (ruff)
- Type checking (mypy)
- Security checks (bandit)
- Dependency analysis (vulture)

### Testing

Comprehensive testing setup with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=markitdown --cov=markitdown_mcp_server --cov=markitdown_web_ui

# Run specific package tests
pytest packages/markitdown-web-ui/tests/
```

## 🔄 Dependency Management

### Adding New Dependencies

1. **Runtime dependencies:** Add to the specific package's `pyproject.toml`
2. **Development dependencies:** Add to `requirements-dev.txt`
3. **Workspace dependencies:** Add to root `pyproject.toml`

### Updating Dependencies

```bash
# Update all dependencies
uv pip install --upgrade -r requirements-dev.txt

# Update specific package
cd packages/markitdown-web-ui
uv pip install --upgrade fastapi
```

### Dependency Conflicts

If you encounter dependency conflicts:

1. Check version constraints in `pyproject.toml` files
2. Use `uv pip list` to see installed versions
3. Use `uv pip show <package>` to see dependency tree
4. Resolve conflicts by updating version constraints

## 🌍 Environment Configuration

### Environment Variables

Create a `.env` file for local development:

```bash
# Web UI Settings
WEB_UI_HOST=0.0.0.0
WEB_UI_PORT=8200
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
```

### Port Configuration

- **Web UI:** Port 8200 (configurable via `WEB_UI_PORT`)
- **MCP Server:** Port 8001 (configurable via `MCP_SERVER_PORT`)
- **API Documentation:** http://localhost:8200/docs

## 📁 Directory Structure

```
markitdown/
├── .venv/                          # Virtual environment
├── packages/                       # All packages
│   ├── markitdown/
│   │   ├── src/markitdown/        # Source code
│   │   ├── tests/                 # Tests
│   │   └── pyproject.toml         # Package config
│   ├── markitdown-mcp-server/
│   │   ├── src/markitdown_mcp_server/
│   │   ├── tests/
│   │   └── pyproject.toml
│   ├── markitdown-web-ui/
│   │   ├── src/markitdown_web_ui/
│   │   ├── tests/
│   │   ├── uploads/               # File uploads
│   │   ├── logs/                  # Application logs
│   │   └── pyproject.toml
│   └── markitdown-sample-plugin/
│       ├── src/markitdown_sample_plugin/
│       ├── tests/
│       └── pyproject.toml
├── docs/                          # Documentation
├── scripts/                       # Setup scripts
├── logs/                          # Global logs
└── uploads/                       # Global uploads
```

## 🚨 Troubleshooting

### Common Issues

1. **Module not found errors:**
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate
   
   # Reinstall packages
   make install-dev
   ```

2. **Port conflicts:**
   ```bash
   # Check what's using the port
   netstat -ano | findstr :8200
   
   # Kill the process or change port in .env
   ```

3. **Dependency conflicts:**
   ```bash
   # Clean and reinstall
   make clean-all
   make setup-dev
   ```

4. **Pre-commit hooks failing:**
   ```bash
   # Run manually to see errors
   pre-commit run --all-files
   
   # Skip hooks for this commit
   git commit --no-verify
   ```

### Getting Help

1. Check the logs in `packages/markitdown-web-ui/logs/`
2. Run with debug mode: `WEB_UI_DEBUG=true make start-web`
3. Check the API documentation: http://localhost:8200/docs
4. Review the test suite for usage examples

## 📚 Additional Resources

- [UV Documentation](https://docs.astral.sh/uv/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pre-commit Documentation](https://pre-commit.com/)
