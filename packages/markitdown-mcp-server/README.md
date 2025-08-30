# MarkItDown MCP Server

A Model Context Protocol (MCP) server for MarkItDown file conversion tools.

## Overview

This package provides MCP tools for converting various file formats to Markdown using the MarkItDown engine. It includes tools for single file conversion, batch processing, format detection, and information retrieval.

## Features

- **Single File Conversion**: Convert individual files to Markdown
- **Batch Processing**: Convert multiple files simultaneously with parallel processing
- **Format Detection**: Automatically detect file formats and MIME types
- **Supported Formats Listing**: Get information about all supported file formats
- **Plugin Management**: List and manage available plugins

## Installation

```bash
# Install the package
uv pip install markitdown-mcp-server

# Or install in development mode
uv pip install -e .
```

## Usage

### Running the MCP Server

```bash
# Run the server directly
python -m markitdown_mcp_server

# Or use the CLI entry point
markitdown-mcp
```

### Available Tools

#### 1. convert_file
Convert a single file to Markdown format.

**Input Schema:**
```json
{
  "file_path": "path/to/file.docx",
  "file_url": "https://example.com/file.docx",
  "output_format": "markdown",
  "options": {
    "use_docintel": false,
    "use_plugins": false
  }
}
```

#### 2. convert_batch
Convert multiple files to Markdown format.

**Input Schema:**
```json
{
  "files": [
    {"file_path": "file1.docx"},
    {"file_path": "file2.pdf"}
  ],
  "batch_options": {
    "parallel": true,
    "max_workers": 4
  }
}
```

#### 3. detect_format
Detect the format of a file.

**Input Schema:**
```json
{
  "file_path": "path/to/file.docx"
}
```

#### 4. list_supported_formats
List all supported file formats.

**Input Schema:**
```json
{}
```

#### 5. list_plugins
List all available plugins.

**Input Schema:**
```json
{}
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd packages/markitdown-mcp-server

# Create virtual environment
uv venv

# Install dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=markitdown_mcp_server

# Run specific test file
pytest tests/test_convert.py
```

### Code Quality

```bash
# Format code
black src/
isort src/

# Type checking
mypy src/

# Linting
ruff check src/
```

## Architecture

The MCP server is built with the following components:

- **Server**: Main MCP server implementation
- **Tools**: Individual tool implementations
- **Utils**: Utility functions for validation and formatting
- **Base**: Abstract base classes for tools

## Dependencies

- `mcp>=1.0.0`: MCP server framework
- `markitdown[all]>=1.0.0`: Core MarkItDown engine
- `pydantic>=2.5.0`: Data validation
- `aiofiles>=23.0.0`: Async file operations

## License

MIT License - see LICENSE file for details.
