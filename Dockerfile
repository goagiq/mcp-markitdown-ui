# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmagic1 \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Copy workspace configuration
COPY pyproject.toml ./
COPY README.md ./

# Create virtual environment and install dependencies using UV
RUN uv venv

# Create configurable directories
RUN mkdir -p /app/input /app/output

# Install markitdown with Vision OCR dependencies
RUN pip install -e ".[vision-ocr]"

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port 8100
EXPOSE 8100

# Set environment variables
ENV PYTHONPATH=/app/packages/markitdown-web-ui/src:/app/packages/markitdown-mcp-server/src
ENV INPUT_DIR=/app/input
ENV OUTPUT_DIR=/app/output
ENV HOST=0.0.0.0
ENV PORT=8100

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8100/health || exit 1

# Start the application
CMD ["python", "-m", "uvicorn", "markitdown_web_ui.app:create_app", "--host", "0.0.0.0", "--port", "8100"]
