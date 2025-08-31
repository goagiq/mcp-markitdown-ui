# MarkItDown Web UI

A web interface for the MarkItDown file conversion tool.

## Features

- Upload and convert various file formats to Markdown
- Modern, responsive web interface
- Drag and drop file upload
- Real-time conversion status
- Download converted files

## Supported Formats

- PDF
- DOCX, DOC
- PPTX, PPT
- XLSX, XLS
- TXT, MD
- HTML, HTM
- EPUB
- CSV
- ZIP

## Installation

```bash
pip install -e .
```

## Usage

Start the web server:

```bash
python -m uvicorn markitdown_web_ui.app:create_app --host 0.0.0.0 --port 8100
```

Or use the command line:

```bash
markitdown-web
```

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

## License

MIT License

