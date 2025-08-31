# Vision OCR Integration Guide for MarkItDown

## Overview

The Vision OCR integration enhances MarkItDown's capabilities for processing image-based PDFs and complex documents using Ollama vision models. This guide covers installation, configuration, usage, and troubleshooting.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage Examples](#usage-examples)
4. [API Reference](#api-reference)
5. [Advanced Features](#advanced-features)
6. [Troubleshooting](#troubleshooting)
7. [Performance Optimization](#performance-optimization)
8. [Best Practices](#best-practices)

## Installation

### Prerequisites

- **Python**: 3.10 or higher
- **RAM**: Minimum 8GB (16GB recommended)
- **Storage**: 10GB for models and temporary files
- **CPU**: Multi-core processor (4+ cores recommended)
- **Network**: Internet access for model downloads

### Step 1: Install Ollama

#### Linux/macOS
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
Download and install from [https://ollama.ai/download](https://ollama.ai/download)

### Step 2: Pull Vision Models

```bash
# Basic models
ollama pull llava:7b
ollama pull llava:13b

# Advanced models
ollama pull llama3.2-vision:latest
ollama pull minicpm-v:latest
```

### Step 3: Install MarkItDown with Vision OCR

#### Basic Installation
```bash
pip install markitdown[vision-ocr]
```

#### Advanced Features Installation
```bash
pip install markitdown[vision-ocr-advanced]
```

### Step 4: Verify Installation

```python
from markitdown.converter_utils.vision_ocr import OllamaVisionClient

# Test connection
client = OllamaVisionClient("llava:7b")
print("Vision OCR installation successful!")
```

## Configuration

### Environment Variables

Create a `.env` file or set environment variables:

```bash
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
```

### Configuration File

Create a configuration file at `~/.markitdown/config/vision_ocr_advanced.json`:

```json
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
```

## Usage Examples

### Basic Usage

#### Command Line Interface

```bash
# Convert a single file
markitdown convert document.pdf --vision-ocr --model llava:7b

# Convert with specific settings
markitdown convert image.jpg --vision-ocr --model llava:13b --hybrid-ocr --quality-threshold 0.8

# Batch conversion
markitdown convert-batch ./documents/ --vision-ocr --model llava:7b --output ./converted/
```

#### Python API

```python
from markitdown import MarkItDown

# Initialize with Vision OCR
md = MarkItDown(enable_vision_ocr=True)

# Convert a file
result = md.convert_file("document.pdf", model="llava:7b", use_hybrid_ocr=True)
print(result.content)
```

### Advanced Usage

#### Quality Prediction

```python
from markitdown.converter_utils.quality_predictor import QualityAnalyzer

analyzer = QualityAnalyzer()

# Analyze OCR quality
metadata = {
    'file_size': 1024000,
    'image_width': 800,
    'image_height': 600,
    'page_count': 1,
    'analysis': {
        'has_text': True,
        'has_images': False,
        'has_tables': False,
        'has_forms': False
    }
}

processing_info = {
    'compression_ratio': 0.8,
    'processing_time': 15.0,
    'model_used': 'llava:7b',
    'hybrid_ocr_used': True
}

extracted_text = "Sample text content."

metrics = analyzer.analyze_ocr_quality(metadata, processing_info, extracted_text)
print(f"Overall Quality Score: {metrics.overall_score}")
print(f"Confidence Score: {metrics.confidence_score}")
print(f"Recommendations: {metrics.recommendations}")
```

#### Batch Processing

```python
from markitdown.converter_utils.batch_processor import BatchProcessor

processor = BatchProcessor(max_workers=4, max_retries=3)

# Create batch job
files = ["doc1.pdf", "doc2.jpg", "doc3.png"]
settings = {
    "model": "llava:7b",
    "use_hybrid_ocr": True,
    "quality_threshold": 0.8
}

job_id = processor.create_batch_job(files, settings)

# Define processor function
def process_file(file_path, settings):
    md = MarkItDown(enable_vision_ocr=True)
    result = md.convert_file(file_path, **settings)
    return {
        'content': result.content,
        'metadata': result.metadata,
        'quality_metrics': result.quality_metrics
    }

# Start processing
processor.start_batch_processing(job_id, process_file)

# Monitor progress
while True:
    status = processor.get_job_status(job_id)
    print(f"Progress: {status['progress']:.1f}%")
    if status['status'] == 'completed':
        break
    time.sleep(1)

# Get results
results = processor.get_job_results(job_id)
for file_path, result in results['results'].items():
    print(f"{file_path}: {result['success']}")
```

#### Advanced Configuration Management

```python
from markitdown.converter_utils.advanced_config_manager import AdvancedConfigManager

config_manager = AdvancedConfigManager()

# Get optimal settings for a file
settings = config_manager.get_optimal_settings("pdf", 2048000)
print(f"Recommended model: {settings['model']}")
print(f"Strategy: {settings['strategy']}")

# Update performance configuration
config_manager.update_performance_config({
    'max_workers': 8,
    'memory_limit_mb': 16384
})

# Get model recommendations
characteristics = {
    'has_forms': True,
    'has_handwriting': False,
    'has_tables': False,
    'file_size': 2048000,
    'page_count': 5
}

recommendations = config_manager.get_model_recommendations(characteristics)
print(f"Recommended models: {recommendations}")

# Save configuration
config_manager.save_config()
```

### MCP Server Usage

#### Tool Commands

```bash
# Convert file using Vision OCR
mcp call vision_ocr_convert --file_path document.pdf --model llava:7b

# Analyze PDF
mcp call vision_ocr_analyze --file_path document.pdf

# Get configuration
mcp call vision_ocr_config --action get
```

#### Python MCP Client

```python
from mcp import ClientSession

async with ClientSession() as session:
    # Convert file
    result = await session.call_tool("vision_ocr_convert", {
        "file_path": "document.pdf",
        "model": "llava:7b",
        "use_hybrid_ocr": True
    })
    
    # Analyze PDF
    analysis = await session.call_tool("vision_ocr_analyze", {
        "file_path": "document.pdf"
    })
    
    # Get configuration
    config = await session.call_tool("vision_ocr_config", {
        "action": "get"
    })
```

### Web UI Usage

#### REST API Endpoints

```bash
# Convert file
curl -X POST "http://localhost:8100/api/vision-ocr/convert" \
  -F "file=@document.pdf" \
  -F "model=llava:7b" \
  -F "use_hybrid_ocr=true"

# Analyze PDF
curl -X POST "http://localhost:8100/api/vision-ocr/analyze" \
  -F "file=@document.pdf"

# Get job status
curl "http://localhost:8100/api/vision-ocr/status/{job_id}"

# Update configuration
curl -X POST "http://localhost:8100/api/vision-ocr/config" \
  -H "Content-Type: application/json" \
  -d '{"action": "update", "settings": {"preferred_model": "llava:13b"}}'
```

#### JavaScript Client

```javascript
// Convert file
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('model', 'llava:7b');
formData.append('use_hybrid_ocr', 'true');

const response = await fetch('/api/vision-ocr/convert', {
    method: 'POST',
    body: formData
});

const result = await response.json();
console.log('Job ID:', result.job_id);

// Monitor progress
const checkStatus = async (jobId) => {
    const statusResponse = await fetch(`/api/vision-ocr/status/${jobId}`);
    const status = await statusResponse.json();
    
    if (status.status === 'completed') {
        console.log('Conversion completed:', status.result);
    } else if (status.status === 'processing') {
        console.log('Progress:', status.progress);
        setTimeout(() => checkStatus(jobId), 1000);
    }
};

checkStatus(result.job_id);
```

## API Reference

### VisionOcrConverter

Main converter class for Vision OCR processing.

```python
class VisionOcrConverter(DocumentConverter):
    def __init__(self, model="llava:7b", use_hybrid=True, **kwargs):
        """
        Initialize Vision OCR converter.
        
        Args:
            model: Vision model to use
            use_hybrid: Enable hybrid OCR approach
            **kwargs: Additional configuration options
        """
    
    def accepts(self, file_stream, stream_info, **kwargs):
        """Check if converter can handle the file."""
    
    def convert(self, file_stream, stream_info, **kwargs):
        """Convert file using Vision OCR."""
```

### OllamaVisionClient

Client for interacting with Ollama vision models.

```python
class OllamaVisionClient:
    def __init__(self, model_name, host="http://localhost:11434"):
        """
        Initialize Ollama vision client.
        
        Args:
            model_name: Name of the vision model
            host: Ollama server host
        """
    
    def extract_text(self, image_data, prompt=None, **kwargs):
        """
        Extract text from image using vision model.
        
        Args:
            image_data: Image data (bytes or base64)
            prompt: Custom prompt for extraction
            **kwargs: Additional parameters
        
        Returns:
            Extracted text content
        """
    
    def get_model_info(self):
        """Get information about the current model."""
    
    def is_model_available(self):
        """Check if the model is available."""
```

### QualityPredictor

ML-based quality prediction for OCR results.

```python
class QualityPredictor:
    def __init__(self, model_path=None):
        """
        Initialize quality predictor.
        
        Args:
            model_path: Path to pre-trained model
        """
    
    def predict_quality(self, features, extracted_text):
        """
        Predict quality metrics for OCR processing.
        
        Args:
            features: ProcessingFeatures object
            extracted_text: Extracted text content
        
        Returns:
            QualityMetrics object
        """
    
    def extract_features(self, metadata, processing_info):
        """
        Extract features from metadata and processing info.
        
        Args:
            metadata: File metadata
            processing_info: Processing information
        
        Returns:
            ProcessingFeatures object
        """
```

### BatchProcessor

Parallel batch processing for multiple files.

```python
class BatchProcessor:
    def __init__(self, max_workers=4, max_retries=3):
        """
        Initialize batch processor.
        
        Args:
            max_workers: Maximum number of worker threads
            max_retries: Maximum retry attempts
        """
    
    def create_batch_job(self, files, settings):
        """
        Create a new batch processing job.
        
        Args:
            files: List of file paths
            settings: Processing settings
        
        Returns:
            Job ID
        """
    
    def start_batch_processing(self, job_id, processor_function):
        """
        Start batch processing.
        
        Args:
            job_id: Job ID
            processor_function: Function to process each file
        """
    
    def get_job_status(self, job_id):
        """Get job status and progress."""
    
    def get_job_results(self, job_id):
        """Get job results."""
    
    def cancel_job(self, job_id):
        """Cancel a running job."""
```

### AdvancedConfigManager

Advanced configuration management for Vision OCR.

```python
class AdvancedConfigManager:
    def __init__(self, config_path=None):
        """
        Initialize advanced configuration manager.
        
        Args:
            config_path: Path to configuration file
        """
    
    def get_optimal_settings(self, file_type, file_size):
        """
        Get optimal settings for file type and size.
        
        Args:
            file_type: Type of file (pdf, image, etc.)
            file_size: Size of file in bytes
        
        Returns:
            Optimal settings dictionary
        """
    
    def get_model_recommendations(self, file_characteristics):
        """
        Get model recommendations based on file characteristics.
        
        Args:
            file_characteristics: Dictionary of file characteristics
        
        Returns:
            List of recommended model names
        """
    
    def update_performance_config(self, updates):
        """Update performance configuration."""
    
    def update_quality_config(self, updates):
        """Update quality configuration."""
    
    def update_user_preferences(self, updates):
        """Update user preferences."""
    
    def validate_config(self):
        """Validate configuration."""
    
    def save_config(self):
        """Save configuration to file."""
    
    def export_config(self, export_path):
        """Export configuration to file."""
    
    def import_config(self, import_path):
        """Import configuration from file."""
```

## Advanced Features

### Quality Prediction

The quality prediction system provides intelligent assessment of OCR results:

- **ML-based Quality Prediction**: Uses scikit-learn for quality assessment
- **Multi-dimensional Analysis**: Text, image, and processing quality
- **Confidence Scoring**: Quantitative confidence measures
- **Processing Recommendations**: Suggestions for improvement

### Batch Processing

The batch processing system enables scalable document processing:

- **Parallel Processing**: Multi-threaded processing of multiple files
- **Progress Tracking**: Real-time progress monitoring
- **Resource Management**: Memory and CPU monitoring
- **Error Recovery**: Robust error handling and retry mechanisms

### Advanced Configuration

The advanced configuration system provides comprehensive control:

- **Model Intelligence**: Smart model selection based on file characteristics
- **Performance Optimization**: Automatic performance tuning
- **User Customization**: Extensive user preference management
- **Environment Integration**: Seamless environment variable management

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Issues

**Problem**: Cannot connect to Ollama server
```
Error: Connection refused to http://localhost:11434
```

**Solution**:
```bash
# Check if Ollama is running
ollama list

# Start Ollama if not running
ollama serve

# Check Ollama status
curl http://localhost:11434/api/tags
```

#### 2. Model Not Available

**Problem**: Specified model is not available
```
Error: Model 'llava:13b' not found
```

**Solution**:
```bash
# List available models
ollama list

# Pull the required model
ollama pull llava:13b

# Verify model availability
ollama show llava:13b
```

#### 3. Memory Issues

**Problem**: Out of memory during processing
```
Error: CUDA out of memory
```

**Solution**:
```python
# Use smaller model
md = MarkItDown(enable_vision_ocr=True, model="llava:7b")

# Reduce batch size
processor = BatchProcessor(max_workers=2)

# Enable compression
settings = {
    "enable_compression": True,
    "compression_quality": 70
}
```

#### 4. Processing Timeout

**Problem**: Processing takes too long
```
Error: Processing timeout after 300 seconds
```

**Solution**:
```python
# Increase timeout
settings = {
    "timeout": 600,  # 10 minutes
    "timeout_multiplier": 2.0
}

# Use faster model
settings = {
    "model": "minicpm-v:latest"
}
```

#### 5. Quality Issues

**Problem**: Low quality OCR results
```
Quality score: 0.3 (below threshold 0.7)
```

**Solution**:
```python
# Use higher quality model
settings = {
    "model": "llava:13b",
    "use_hybrid_ocr": True
}

# Improve image quality
settings = {
    "max_image_size": 1200,
    "compression_quality": 95
}
```

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or set specific logger
logging.getLogger('markitdown.converter_utils.vision_ocr').setLevel(logging.DEBUG)
```

### Performance Monitoring

Monitor performance metrics:

```python
from markitdown.converter_utils.batch_processor import BatchProcessor

processor = BatchProcessor()

# Get system statistics
stats = processor.get_system_stats()
print(f"Active jobs: {stats['active_jobs']}")
print(f"Completed jobs: {stats['completed_jobs']}")
print(f"Memory usage: {stats.get('memory_usage', 'N/A')}")
```

## Performance Optimization

### Model Selection

Choose the right model for your use case:

| Model | Speed | Accuracy | Memory | Use Case |
|-------|-------|----------|--------|----------|
| minicpm-v:latest | Fast | Good | Low | Simple documents |
| llava:7b | Medium | Very Good | Medium | General purpose |
| llava:13b | Slow | Excellent | High | Complex documents |
| llama3.2-vision:latest | Slow | Excellent | High | Handwriting |

### Image Optimization

Optimize images for better performance:

```python
# Optimal settings for different scenarios
settings = {
    # Text-heavy documents
    "max_image_size": 800,
    "compression_quality": 85,
    "use_grayscale": True,
    
    # Complex layouts
    "max_image_size": 1200,
    "compression_quality": 95,
    "use_grayscale": False,
    
    # Large documents
    "max_image_size": 600,
    "compression_quality": 70,
    "use_grayscale": True
}
```

### Resource Management

Optimize resource usage:

```python
# Memory optimization
settings = {
    "memory_limit_mb": 4096,  # 4GB limit
    "enable_compression": True,
    "cleanup_temp_files": True
}

# CPU optimization
settings = {
    "max_workers": 2,  # Reduce for limited CPU
    "cpu_limit_percent": 50
}
```

### Caching

Enable caching for better performance:

```python
# Enable caching
settings = {
    "enable_caching": True,
    "cache_ttl_hours": 24,
    "cache_dir": "/tmp/markitdown_cache"
}
```

## Best Practices

### 1. Model Selection

- Use `llava:7b` for general purpose processing
- Use `llava:13b` for complex documents with forms or tables
- Use `llama3.2-vision:latest` for handwriting recognition
- Use `minicpm-v:latest` for simple documents or limited resources

### 2. Image Preparation

- Ensure images are at least 300 DPI for good OCR results
- Use grayscale for text-heavy documents
- Maintain aspect ratio when resizing
- Avoid excessive compression

### 3. Batch Processing

- Use appropriate batch sizes based on available memory
- Monitor system resources during processing
- Implement proper error handling and retry logic
- Clean up temporary files regularly

### 4. Configuration Management

- Start with default configurations
- Gradually tune settings based on your use case
- Validate configurations before deployment
- Backup configurations regularly

### 5. Quality Assurance

- Set appropriate quality thresholds
- Use quality prediction for automatic optimization
- Implement manual review for critical documents
- Monitor quality metrics over time

### 6. Error Handling

- Implement graceful fallback to traditional OCR
- Use retry logic for transient failures
- Log errors for debugging and monitoring
- Provide user-friendly error messages

### 7. Performance Monitoring

- Monitor processing times and resource usage
- Track quality metrics and success rates
- Set up alerts for performance degradation
- Regularly review and optimize settings

## Support and Resources

### Documentation

- [MarkItDown Documentation](https://github.com/microsoft/markitdown)
- [Ollama Documentation](https://ollama.ai/docs)
- [Vision OCR API Reference](docs/api-documentation.md)

### Community

- [GitHub Issues](https://github.com/microsoft/markitdown/issues)
- [Discussions](https://github.com/microsoft/markitdown/discussions)
- [Discord Community](https://discord.gg/markitdown)

### Examples

- [Vision OCR Examples](examples/vision-ocr/)
- [Batch Processing Examples](examples/batch-processing/)
- [Configuration Examples](examples/configuration/)

### Troubleshooting

- [Common Issues](troubleshooting/common-issues.md)
- [Performance Tuning](troubleshooting/performance-tuning.md)
- [Error Codes](troubleshooting/error-codes.md)
