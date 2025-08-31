#!/bin/bash

# MarkItDown Vision OCR Setup Script
# This script automates the installation and configuration of Vision OCR integration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$HOME/.markitdown/config"
LOG_FILE="$PROJECT_ROOT/setup-vision-ocr.log"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_system_requirements() {
    log "Checking system requirements..."
    
    # Check Python version
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        if [[ $(echo "$PYTHON_VERSION >= 3.10" | bc -l) -eq 1 ]]; then
            log "✓ Python $PYTHON_VERSION is compatible"
        else
            error "Python 3.10 or higher is required. Found: $PYTHON_VERSION"
        fi
    else
        error "Python 3 is not installed"
    fi
    
    # Check available memory
    if command_exists free; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
        if [[ $MEMORY_GB -ge 8 ]]; then
            log "✓ Available memory: ${MEMORY_GB}GB (minimum 8GB required)"
        else
            warn "Available memory: ${MEMORY_GB}GB (minimum 8GB recommended)"
        fi
    fi
    
    # Check available disk space
    if command_exists df; then
        DISK_GB=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
        if [[ $DISK_GB -ge 20 ]]; then
            log "✓ Available disk space: ${DISK_GB}GB (minimum 20GB required)"
        else
            warn "Available disk space: ${DISK_GB}GB (minimum 20GB recommended)"
        fi
    fi
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        warn "Running as root. Consider running as a regular user for security."
    fi
}

# Function to install Ollama
install_ollama() {
    log "Installing Ollama..."
    
    if command_exists ollama; then
        log "✓ Ollama is already installed"
        OLLAMA_VERSION=$(ollama --version)
        log "Ollama version: $OLLAMA_VERSION"
        return 0
    fi
    
    # Detect OS and install Ollama
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists curl; then
            log "Installing Ollama on Linux..."
            curl -fsSL https://ollama.ai/install.sh | sh
        else
            error "curl is required to install Ollama"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if command_exists brew; then
            log "Installing Ollama on macOS using Homebrew..."
            brew install ollama
        else
            log "Installing Ollama on macOS..."
            curl -fsSL https://ollama.ai/install.sh | sh
        fi
    else
        error "Unsupported operating system: $OSTYPE"
    fi
    
    # Verify installation
    if command_exists ollama; then
        log "✓ Ollama installed successfully"
        OLLAMA_VERSION=$(ollama --version)
        log "Ollama version: $OLLAMA_VERSION"
    else
        error "Failed to install Ollama"
    fi
}

# Function to start Ollama service
start_ollama() {
    log "Starting Ollama service..."
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        log "✓ Ollama is already running"
        return 0
    fi
    
    # Start Ollama
    if command_exists systemctl; then
        sudo systemctl start ollama
        sudo systemctl enable ollama
    else
        # Start Ollama in background
        nohup ollama serve >/dev/null 2>&1 &
        sleep 5
    fi
    
    # Wait for Ollama to be ready
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            log "✓ Ollama is running"
            return 0
        fi
        log "Waiting for Ollama to start... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    error "Failed to start Ollama service"
}

# Function to pull vision models
pull_vision_models() {
    log "Pulling vision models..."
    
    # List of models to pull
    MODELS=("llava:7b" "llava:13b" "llama3.2-vision:latest" "minicpm-v:latest")
    
    for model in "${MODELS[@]}"; do
        log "Pulling model: $model"
        
        # Check if model already exists
        if ollama list | grep -q "$model"; then
            log "✓ Model $model already exists"
            continue
        fi
        
        # Pull model with progress
        if ollama pull "$model"; then
            log "✓ Successfully pulled $model"
        else
            warn "Failed to pull $model (this is optional)"
        fi
    done
    
    # List available models
    log "Available models:"
    ollama list
}

# Function to install Python dependencies
install_python_dependencies() {
    log "Installing Python dependencies..."
    
    # Check if pip is available
    if ! command_exists pip3; then
        error "pip3 is not available"
    fi
    
    # Upgrade pip
    log "Upgrading pip..."
    python3 -m pip install --upgrade pip
    
    # Install basic Vision OCR dependencies
    log "Installing Vision OCR dependencies..."
    pip3 install markitdown[vision-ocr]
    
    # Install advanced features if requested
    if [[ "$1" == "--advanced" ]]; then
        log "Installing advanced Vision OCR features..."
        pip3 install markitdown[vision-ocr-advanced]
    fi
    
    log "✓ Python dependencies installed successfully"
}

# Function to create configuration directory
create_config_directory() {
    log "Creating configuration directory..."
    
    mkdir -p "$CONFIG_DIR"
    log "✓ Configuration directory created: $CONFIG_DIR"
}

# Function to create default configuration
create_default_config() {
    log "Creating default configuration..."
    
    local config_file="$CONFIG_DIR/vision_ocr_advanced.json"
    
    cat > "$config_file" << 'EOF'
{
  "models": {
    "llava:7b": {
      "name": "llava:7b",
      "max_tokens": 2048,
      "temperature": 0.1,
      "prompt_template": "Extract all text from this image accurately:",
      "timeout": 300,
      "memory_usage": "medium",
      "accuracy_level": "balanced",
      "recommended_for": ["general", "documents", "images"]
    },
    "llava:13b": {
      "name": "llava:13b",
      "max_tokens": 4096,
      "temperature": 0.05,
      "prompt_template": "Please extract and transcribe all visible text from this document:",
      "timeout": 600,
      "memory_usage": "high",
      "accuracy_level": "high",
      "recommended_for": ["complex", "forms", "tables", "handwriting"]
    },
    "llama3.2-vision:latest": {
      "name": "llama3.2-vision:latest",
      "max_tokens": 4096,
      "temperature": 0.05,
      "prompt_template": "Please extract and transcribe all visible text from this document:",
      "timeout": 450,
      "memory_usage": "high",
      "accuracy_level": "high",
      "recommended_for": ["handwriting", "complex", "multilingual"]
    },
    "minicpm-v:latest": {
      "name": "minicpm-v:latest",
      "max_tokens": 1024,
      "temperature": 0.2,
      "prompt_template": "Extract text from this image:",
      "timeout": 180,
      "memory_usage": "low",
      "accuracy_level": "fast",
      "recommended_for": ["simple", "quick", "low_memory"]
    }
  },
  "performance": {
    "max_workers": 4,
    "max_concurrent_tasks": 4,
    "max_retries": 3,
    "timeout_multiplier": 1.0,
    "memory_limit_mb": 8192,
    "cpu_limit_percent": 80,
    "enable_caching": true,
    "cache_ttl_hours": 24,
    "enable_compression": true,
    "compression_quality": 85
  },
  "quality": {
    "min_confidence_threshold": 0.7,
    "enable_quality_prediction": true,
    "enable_auto_retry": true,
    "max_retry_attempts": 2,
    "quality_improvement_threshold": 0.1,
    "enable_fallback_strategies": true,
    "enable_hybrid_ocr": true
  },
  "user_preferences": {
    "preferred_model": "llava:7b",
    "preferred_strategy": "balanced",
    "auto_optimize_settings": true,
    "enable_notifications": true,
    "save_processing_history": true,
    "max_history_items": 100,
    "language_preference": "en",
    "output_format": "markdown"
  }
}
EOF
    
    log "✓ Default configuration created: $config_file"
}

# Function to create environment file
create_environment_file() {
    log "Creating environment configuration..."
    
    local env_file="$PROJECT_ROOT/.env"
    
    cat > "$env_file" << 'EOF'
# MarkItDown Web UI Environment Configuration

# Application Settings
HOST=0.0.0.0
PORT=8200
DEBUG=false
LOG_LEVEL=INFO

# Input/Output Directory Configuration
INPUT_DIR=./input
OUTPUT_DIR=./output

# Security Settings
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Monitoring and Logging
ENABLE_METRICS=true
LOG_FILE=/app/logs/markitdown.log

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# File Upload Settings
MAX_FILE_SIZE=100MB
ALLOWED_FILE_TYPES=pdf,docx,txt,jpg,png,html

# MCP Server Settings
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8001
MCP_SERVER_TIMEOUT=30

# =============================================================================
# VISION OCR CONFIGURATION
# =============================================================================

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_TIMEOUT=300
OLLAMA_RETRY_ATTEMPTS=3

# Vision OCR Model Settings
VISION_OCR_MODEL=llava:7b
VISION_OCR_STRATEGY=balanced
VISION_OCR_ENABLE_HYBRID=true
VISION_OCR_MAX_WORKERS=4
VISION_OCR_TIMEOUT=300
VISION_OCR_MEMORY_LIMIT=8192
VISION_OCR_ENABLE_CACHING=true
VISION_OCR_QUALITY_THRESHOLD=0.7

# Performance Tuning
VISION_OCR_MAX_CONCURRENT_TASKS=4
VISION_OCR_MAX_RETRIES=3
VISION_OCR_TIMEOUT_MULTIPLIER=1.0
VISION_OCR_CPU_LIMIT_PERCENT=80
VISION_OCR_CACHE_TTL_HOURS=24
VISION_OCR_ENABLE_COMPRESSION=true
VISION_OCR_COMPRESSION_QUALITY=85

# Quality Control
VISION_OCR_ENABLE_QUALITY_PREDICTION=true
VISION_OCR_ENABLE_AUTO_RETRY=true
VISION_OCR_MAX_RETRY_ATTEMPTS=2
VISION_OCR_QUALITY_IMPROVEMENT_THRESHOLD=0.1
VISION_OCR_ENABLE_FALLBACK_STRATEGIES=true

# User Preferences
VISION_OCR_AUTO_OPTIMIZE_SETTINGS=true
VISION_OCR_ENABLE_NOTIFICATIONS=true
VISION_OCR_SAVE_PROCESSING_HISTORY=true
VISION_OCR_MAX_HISTORY_ITEMS=100
VISION_OCR_LANGUAGE_PREFERENCE=en
VISION_OCR_OUTPUT_FORMAT=markdown

# Batch Processing
VISION_OCR_BATCH_MAX_WORKERS=4
VISION_OCR_BATCH_MAX_CONCURRENT=4
VISION_OCR_BATCH_MAX_RETRIES=3
VISION_OCR_BATCH_CLEANUP_HOURS=24

# Advanced Features
VISION_OCR_ENABLE_ML_QUALITY_PREDICTION=true
VISION_OCR_ENABLE_BATCH_PROCESSING=true
VISION_OCR_ENABLE_ADVANCED_CONFIG=true
VISION_OCR_ENABLE_MULTI_PAGE_PROCESSING=true
VISION_OCR_ENABLE_PERFORMANCE_OPTIMIZATION=true

# Error Handling and Recovery
VISION_OCR_ENABLE_ERROR_RECOVERY=true
VISION_OCR_FALLBACK_TO_TRADITIONAL_OCR=true
VISION_OCR_ENABLE_PROGRESS_TRACKING=true
VISION_OCR_ENABLE_DETAILED_LOGGING=true

# Resource Management
VISION_OCR_ENABLE_MEMORY_MONITORING=true
VISION_OCR_ENABLE_CPU_MONITORING=true
VISION_OCR_ENABLE_DISK_MONITORING=true
VISION_OCR_AUTO_CLEANUP_TEMP_FILES=true

# Integration Settings
VISION_OCR_ENABLE_MCP_INTEGRATION=true
VISION_OCR_ENABLE_WEB_UI_INTEGRATION=true
VISION_OCR_ENABLE_API_INTEGRATION=true
VISION_OCR_ENABLE_BACKGROUND_PROCESSING=true

# Development and Testing
VISION_OCR_ENABLE_DEBUG_MODE=false
VISION_OCR_ENABLE_TEST_MODE=false
VISION_OCR_ENABLE_MOCK_PROCESSING=false
VISION_OCR_ENABLE_PERFORMANCE_PROFILING=false
EOF
    
    log "✓ Environment configuration created: $env_file"
}

# Function to test installation
test_installation() {
    log "Testing Vision OCR installation..."
    
    # Test Python import
    if python3 -c "from markitdown.converter_utils.vision_ocr import OllamaVisionClient; print('✓ Vision OCR import successful')" 2>/dev/null; then
        log "✓ Python imports working correctly"
    else
        error "Failed to import Vision OCR modules"
    fi
    
    # Test Ollama connection
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        log "✓ Ollama connection successful"
    else
        error "Failed to connect to Ollama"
    fi
    
    # Test model availability
    if ollama list | grep -q "llava:7b"; then
        log "✓ At least one vision model is available"
    else
        warn "No vision models found. You may need to pull models manually."
    fi
    
    log "✓ Installation test completed successfully"
}

# Function to create directories
create_directories() {
    log "Creating necessary directories..."
    
    local dirs=(
        "$PROJECT_ROOT/input"
        "$PROJECT_ROOT/output"
        "$PROJECT_ROOT/logs"
        "$PROJECT_ROOT/cache"
        "$PROJECT_ROOT/temp"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        log "✓ Created directory: $dir"
    done
}

# Function to set permissions
set_permissions() {
    log "Setting file permissions..."
    
    # Make script executable
    chmod +x "$SCRIPT_DIR/setup-vision-ocr.sh"
    
    # Set directory permissions
    chmod 755 "$PROJECT_ROOT/input"
    chmod 755 "$PROJECT_ROOT/output"
    chmod 755 "$PROJECT_ROOT/logs"
    chmod 755 "$PROJECT_ROOT/cache"
    chmod 755 "$PROJECT_ROOT/temp"
    
    log "✓ Permissions set successfully"
}

# Function to display usage information
show_usage() {
    log "Vision OCR setup completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Start the MarkItDown Web UI:"
    echo "   cd $PROJECT_ROOT"
    echo "   python3 -m markitdown_web_ui"
    echo
    echo "2. Or use Docker:"
    echo "   docker-compose up -d"
    echo
    echo "3. Test the installation:"
    echo "   python3 -c \"from markitdown import MarkItDown; md = MarkItDown(enable_vision_ocr=True); print('Setup successful!')\""
    echo
    echo "4. View documentation:"
    echo "   open docs/vision-ocr-guide.md"
    echo
    echo "Configuration files:"
    echo "- Environment: $PROJECT_ROOT/.env"
    echo "- Advanced config: $CONFIG_DIR/vision_ocr_advanced.json"
    echo "- Logs: $LOG_FILE"
    echo
    echo "For more information, see: docs/vision-ocr-guide.md"
}

# Function to cleanup on error
cleanup() {
    error "Setup failed. Check the log file: $LOG_FILE"
}

# Main function
main() {
    # Set up error handling
    trap cleanup ERR
    
    # Parse command line arguments
    INSTALL_ADVANCED=false
    while [[ $# -gt 0 ]]; do
        case $1 in
            --advanced)
                INSTALL_ADVANCED=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [--advanced]"
                echo "  --advanced  Install advanced features (ML, batch processing, etc.)"
                echo "  --help      Show this help message"
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
    
    # Start setup
    log "Starting MarkItDown Vision OCR setup..."
    log "Project root: $PROJECT_ROOT"
    log "Log file: $LOG_FILE"
    
    # Check system requirements
    check_system_requirements
    
    # Install Ollama
    install_ollama
    
    # Start Ollama service
    start_ollama
    
    # Pull vision models
    pull_vision_models
    
    # Install Python dependencies
    if [[ "$INSTALL_ADVANCED" == true ]]; then
        install_python_dependencies --advanced
    else
        install_python_dependencies
    fi
    
    # Create directories and configuration
    create_directories
    create_config_directory
    create_default_config
    create_environment_file
    set_permissions
    
    # Test installation
    test_installation
    
    # Show usage information
    show_usage
    
    log "Vision OCR setup completed successfully!"
}

# Run main function with all arguments
main "$@"
