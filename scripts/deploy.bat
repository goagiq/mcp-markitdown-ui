@echo off
setlocal enabledelayedexpansion

REM MarkItDown Web UI Deployment Script for Windows
REM This script deploys the MarkItDown Web UI with configurable input/output directories

REM Default configuration
set DEFAULT_INPUT_DIR=.\input
set DEFAULT_OUTPUT_DIR=.\output
set DEFAULT_PORT=8100

REM Parse command line arguments
set INPUT_DIR=%DEFAULT_INPUT_DIR%
set OUTPUT_DIR=%DEFAULT_OUTPUT_DIR%
set PORT=%DEFAULT_PORT%
set ENV_FILE=.env
set DEV_MODE=false

:parse_args
if "%~1"=="" goto :end_parse
if "%~1"=="-i" (
    set INPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--input-dir" (
    set INPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-o" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--output-dir" (
    set OUTPUT_DIR=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-p" (
    set PORT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--port" (
    set PORT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-e" (
    set ENV_FILE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--env-file" (
    set ENV_FILE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-d" (
    set DEV_MODE=true
    shift
    goto :parse_args
)
if "%~1"=="--dev" (
    set DEV_MODE=true
    shift
    goto :parse_args
)
if "%~1"=="-h" (
    goto :show_usage
)
if "%~1"=="--help" (
    goto :show_usage
)
echo [ERROR] Unknown option: %~1
goto :show_usage

:show_usage
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   -i, --input-dir DIR     Input directory ^(default: %DEFAULT_INPUT_DIR%^)
echo   -o, --output-dir DIR    Output directory ^(default: %DEFAULT_OUTPUT_DIR%^)
echo   -p, --port PORT         Port number ^(default: %DEFAULT_PORT%^)
echo   -e, --env-file FILE     Environment file ^(default: .env^)
echo   -d, --dev               Development mode
echo   -h, --help              Show this help message
echo.
echo Examples:
echo   %0                                    # Use default settings
echo   %0 -i C:\path\to\docs -o C:\path\to\output
echo   %0 -i C:\path\to\images -o C:\path\to\converted -p 8200
echo   %0 -d                                 # Development mode
exit /b 1

:end_parse

REM Validate directories
if not exist "%INPUT_DIR%" (
    echo [WARNING] Input directory '%INPUT_DIR%' does not exist. Creating...
    mkdir "%INPUT_DIR%"
)

if not exist "%OUTPUT_DIR%" (
    echo [WARNING] Output directory '%OUTPUT_DIR%' does not exist. Creating...
    mkdir "%OUTPUT_DIR%"
)

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Create environment file if it doesn't exist
if not exist "%ENV_FILE%" (
    echo [INFO] Creating environment file: %ENV_FILE%
    
    REM Generate a random secret key (simple implementation)
    set SECRET_KEY=
    for /L %%i in (1,1,32) do (
        set /a rand=!random! %% 16
        if !rand! lss 10 (
            set SECRET_KEY=!SECRET_KEY!!rand!
        ) else (
            set /a char=!rand! + 87
            for %%j in (!char!) do set SECRET_KEY=!SECRET_KEY!%%j
        )
    )
    
    (
        echo # MarkItDown Web UI Environment Configuration
        echo HOST=0.0.0.0
        echo PORT=%PORT%
        echo DEBUG=%DEV_MODE%
        echo LOG_LEVEL=INFO
        echo.
        echo # Input/Output Directory Configuration
        echo INPUT_DIR=%INPUT_DIR%
        echo OUTPUT_DIR=%OUTPUT_DIR%
        echo.
        echo # Development settings (handled by separate docker-compose.dev.yml)
        echo.
        echo # Security Settings
        echo SECRET_KEY=%SECRET_KEY%
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo.
        echo # Monitoring and Logging
        echo ENABLE_METRICS=true
        echo LOG_FILE=/app/logs/markitdown.log
        echo.
        echo # Rate Limiting
        echo RATE_LIMIT_REQUESTS=100
        echo RATE_LIMIT_WINDOW=60
        echo.
        echo # File Upload Settings
        echo MAX_FILE_SIZE=100MB
        echo ALLOWED_FILE_TYPES=pdf,docx,txt,jpg,png,html
        echo.
        echo # MCP Server Settings
        echo MCP_SERVER_HOST=localhost
        echo MCP_SERVER_PORT=8001
        echo MCP_SERVER_TIMEOUT=30
    ) > "%ENV_FILE%"
    
    echo [SUCCESS] Environment file created: %ENV_FILE%
)

REM Set environment variables for docker-compose
set INPUT_DIR=%INPUT_DIR%
set OUTPUT_DIR=%OUTPUT_DIR%
set PORT=%PORT%
set DEV_MODE=%DEV_MODE%

echo [INFO] Deploying MarkItDown Web UI...
echo [INFO] Input directory: %INPUT_DIR%
echo [INFO] Output directory: %OUTPUT_DIR%
echo [INFO] Port: %PORT%
echo [INFO] Development mode: %DEV_MODE%

REM Build and start the containers
if "%DEV_MODE%"=="true" (
    echo [INFO] Starting in development mode...
    docker-compose -f docker-compose.dev.yml up --build -d
) else (
    echo [INFO] Starting in production mode...
    docker-compose --profile production up --build -d
)

REM Wait for the service to be ready
echo [INFO] Waiting for service to be ready...
timeout /t 10 /nobreak >nul

REM Check if the service is running
curl -f http://localhost:%PORT%/health >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Service failed to start. Check logs with: docker-compose logs
    exit /b 1
) else (
    echo [SUCCESS] MarkItDown Web UI is running successfully!
    echo [SUCCESS] Access the web UI at: http://localhost:%PORT%
    echo [SUCCESS] API documentation at: http://localhost:%PORT%/docs
    echo [SUCCESS] Health check at: http://localhost:%PORT%/health
    echo.
    echo [INFO] Configuration:
    echo [INFO]   Input directory: %INPUT_DIR%
    echo [INFO]   Output directory: %OUTPUT_DIR%
    echo [INFO]   Port: %PORT%
    echo.
    echo [INFO] To stop the service, run: docker-compose down
    echo [INFO] To view logs, run: docker-compose logs -f
)
