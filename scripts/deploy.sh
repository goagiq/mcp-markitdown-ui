#!/bin/bash

# MarkItDown Web UI Deployment Script
# This script deploys the MarkItDown Web UI with configurable input/output directories

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
DEFAULT_INPUT_DIR="./input"
DEFAULT_OUTPUT_DIR="./output"
DEFAULT_PORT="8200"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -i, --input-dir DIR     Input directory (default: $DEFAULT_INPUT_DIR)"
    echo "  -o, --output-dir DIR    Output directory (default: $DEFAULT_OUTPUT_DIR)"
    echo "  -p, --port PORT         Port number (default: $DEFAULT_PORT)"
    echo "  -e, --env-file FILE     Environment file (default: .env)"
    echo "  -d, --dev               Development mode"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Use default settings"
    echo "  $0 -i /path/to/docs -o /path/to/output"
    echo "  $0 -i /path/to/images -o /path/to/converted -p 8300"
    echo "  $0 -d                                 # Development mode"
}

# Parse command line arguments
INPUT_DIR="$DEFAULT_INPUT_DIR"
OUTPUT_DIR="$DEFAULT_OUTPUT_DIR"
PORT="$DEFAULT_PORT"
ENV_FILE=".env"
DEV_MODE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--input-dir)
            INPUT_DIR="$2"
            shift 2
            ;;
        -o|--output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -e|--env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        -d|--dev)
            DEV_MODE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate directories
if [[ ! -d "$INPUT_DIR" ]]; then
    print_warning "Input directory '$INPUT_DIR' does not exist. Creating..."
    mkdir -p "$INPUT_DIR"
fi

if [[ ! -d "$OUTPUT_DIR" ]]; then
    print_warning "Output directory '$OUTPUT_DIR' does not exist. Creating..."
    mkdir -p "$OUTPUT_DIR"
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create environment file if it doesn't exist
if [[ ! -f "$ENV_FILE" ]]; then
    print_status "Creating environment file: $ENV_FILE"
    cat > "$ENV_FILE" << EOF
# MarkItDown Web UI Environment Configuration
HOST=0.0.0.0
PORT=$PORT
DEBUG=$DEV_MODE
LOG_LEVEL=INFO

# Input/Output Directory Configuration
INPUT_DIR=$INPUT_DIR
OUTPUT_DIR=$OUTPUT_DIR

# Development settings (handled by separate docker-compose.dev.yml)

# Security Settings
SECRET_KEY=$(openssl rand -hex 32)
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
EOF
    print_success "Environment file created: $ENV_FILE"
fi

# Export environment variables for docker-compose
export INPUT_DIR
export OUTPUT_DIR
export PORT
export DEV_MODE

print_status "Deploying MarkItDown Web UI..."
print_status "Input directory: $INPUT_DIR"
print_status "Output directory: $OUTPUT_DIR"
print_status "Port: $PORT"
print_status "Development mode: $DEV_MODE"

# Build and start the containers
if [[ "$DEV_MODE" == "true" ]]; then
    print_status "Starting in development mode..."
    docker-compose -f docker-compose.dev.yml up --build -d
else
    print_status "Starting in production mode..."
    docker-compose --profile production up --build -d
fi

# Wait for the service to be ready
print_status "Waiting for service to be ready..."
sleep 10

# Check if the service is running
if curl -f http://localhost:$PORT/health &> /dev/null; then
    print_success "MarkItDown Web UI is running successfully!"
    print_success "Access the web UI at: http://localhost:$PORT"
    print_success "API documentation at: http://localhost:$PORT/docs"
    print_success "Health check at: http://localhost:$PORT/health"
    echo ""
    print_status "Configuration:"
    print_status "  Input directory: $INPUT_DIR"
    print_status "  Output directory: $OUTPUT_DIR"
    print_status "  Port: $PORT"
    echo ""
    print_status "To stop the service, run: docker-compose down"
    print_status "To view logs, run: docker-compose logs -f"
else
    print_error "Service failed to start. Check logs with: docker-compose logs"
    exit 1
fi
