@echo off
REM MarkItDown Development Environment Setup Script for Windows
REM This script sets up the development environment for the MarkItDown project

echo 🚀 Setting up MarkItDown Development Environment

REM Check if UV is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo ❌ UV is not installed. Please install UV first:
    echo    curl -LsSf https://astral.sh/uv/install.sh ^| sh
    pause
    exit /b 1
)

echo ✅ UV is installed
uv --version

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    uv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install all packages in development mode
echo 📥 Installing packages in development mode...

REM Install core markitdown package
echo   📦 Installing markitdown...
cd packages\markitdown
uv pip install -e ".[dev]"
cd ..\..

REM Install MCP server package
echo   📦 Installing markitdown-mcp-server...
cd packages\markitdown-mcp-server
uv pip install -e ".[dev]"
cd ..\..

REM Install web UI package
echo   📦 Installing markitdown-web-ui...
cd packages\markitdown-web-ui
uv pip install -e ".[dev]"
cd ..\..

REM Install sample plugin package
echo   📦 Installing markitdown-sample-plugin...
cd packages\markitdown-sample-plugin
uv pip install -e ".[dev]"
cd ..\..

REM Install development dependencies
echo   📦 Installing development dependencies...
uv pip install -r requirements-dev.txt 2>nul || echo   ⚠️  requirements-dev.txt not found, skipping...

REM Run pre-commit setup
echo 🔧 Setting up pre-commit hooks...
pre-commit install 2>nul || echo   ⚠️  pre-commit not available, skipping...

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "packages\markitdown-web-ui\uploads" mkdir packages\markitdown-web-ui\uploads
if not exist "packages\markitdown-web-ui\logs" mkdir packages\markitdown-web-ui\logs
if not exist "packages\markitdown-mcp-server\logs" mkdir packages\markitdown-mcp-server\logs

REM Set up environment variables
echo 🔧 Setting up environment variables...
if not exist ".env" (
    (
        echo # MarkItDown Development Environment Variables
        echo.
        echo # Web UI Settings
        echo WEB_UI_HOST=0.0.0.0
        echo WEB_UI_PORT=8100
        echo WEB_UI_DEBUG=true
        echo.
        echo # MCP Server Settings
        echo MCP_SERVER_HOST=0.0.0.0
        echo MCP_SERVER_PORT=8001
        echo.
        echo # File Upload Settings
        echo MAX_FILE_SIZE=104857600
        echo UPLOAD_DIR=uploads
        echo.
        echo # Security Settings
        echo SECRET_KEY=dev-secret-key-change-in-production
        echo CORS_ORIGINS=*
        echo.
        echo # Logging Settings
        echo LOG_LEVEL=INFO
        echo LOG_FILE=logs/markitdown.log
    ) > .env
    echo   ✅ Created .env file
) else (
    echo   ⚠️  .env file already exists
)

echo.
echo 🎉 Development environment setup complete!
echo.
echo 📋 Next steps:
echo   1. Activate the virtual environment: .venv\Scripts\activate.bat
echo   2. Start the MCP server: cd packages\markitdown-mcp-server ^&^& python -m markitdown_mcp_server
echo   3. Start the web UI: cd packages\markitdown-web-ui ^&^& python -m markitdown_web_ui
echo   4. Access the web UI at: http://localhost:8100
echo   5. Access the API docs at: http://localhost:8100/docs
echo.
echo 🔧 Development commands:
echo   - Run tests: pytest
echo   - Format code: black . ^&^& isort .
echo   - Lint code: ruff check .
echo   - Type check: mypy .
echo.
pause
