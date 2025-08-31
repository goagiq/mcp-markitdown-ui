#!/usr/bin/env python3
"""
FastAPI deployment for MarkItDown MCP Server
Provides REST API access to MCP tools
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

# Add the packages directory to the path
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 
                                'packages/markitdown/src'))

from markitdown import MarkItDown

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MarkItDown MCP Server",
    description="Model Context Protocol Server for document conversion",
    version="1.0.0"
)

# Initialize MarkItDown
markitdown = MarkItDown()

# Pydantic models for request/response
class ConvertRequest(BaseModel):
    file_path: Optional[str] = None
    file_content: Optional[str] = None
    file_name: Optional[str] = None

class ConvertResponse(BaseModel):
    success: bool
    markdown: str
    text_length: int
    error: Optional[str] = None

class FormatDetectionRequest(BaseModel):
    file_path: Optional[str] = None
    file_content: Optional[str] = None

class FormatDetectionResponse(BaseModel):
    format: str
    error: Optional[str] = None

class SupportedFormatsResponse(BaseModel):
    formats: list[str]

# FastAPI endpoints for REST API access
@app.get("/", operation_id="get_root")
async def root():
    """Root endpoint"""
    return {
        "service": "MarkItDown MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "convert": "/convert",
            "detect_format": "/detect_format",
            "supported_formats": "/supported_formats",
            "health": "/health"
        }
    }

@app.get("/health", operation_id="get_health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "markitdown-mcp",
        "version": "1.0.0"
    }

@app.post("/convert", operation_id="convert_document")
async def convert_document(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    file_content: Optional[str] = Form(None),
    file_name: Optional[str] = Form(None)
):
    """Convert a document to markdown format"""
    try:
        if file:
            # Handle uploaded file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_path = temp_file.name
            
            try:
                result = markitdown.convert(temp_path)
                return ConvertResponse(
                    success=True,
                    markdown=result.markdown,
                    text_length=len(result.markdown)
                )
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
        
        elif file_path:
            # Handle file path
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
            
            result = markitdown.convert(file_path)
            return ConvertResponse(
                success=True,
                markdown=result.markdown,
                text_length=len(result.markdown)
            )
        
        elif file_content and file_name:
            # Handle base64 content
            import base64
            
            try:
                file_data = base64.b64decode(file_content)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid base64 content: {e}")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix) as temp_file:
                temp_file.write(file_data)
                temp_path = temp_file.name
            
            try:
                result = markitdown.convert(temp_path)
                return ConvertResponse(
                    success=True,
                    markdown=result.markdown,
                    text_length=len(result.markdown)
                )
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
        
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either file upload, file_path, or both file_content and file_name must be provided"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting document: {e}")
        return ConvertResponse(
            success=False,
            markdown="",
            text_length=0,
            error=str(e)
        )

@app.post("/detect_format", operation_id="detect_format")
async def detect_format(
    file: Optional[UploadFile] = File(None),
    file_path: Optional[str] = Form(None),
    file_content: Optional[str] = Form(None)
):
    """Detect the format of a document"""
    try:
        extension = None
        
        if file:
            # Handle uploaded file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No filename provided")
            extension = Path(file.filename).suffix.lower()
        
        elif file_path:
            # Handle file path
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
            extension = Path(file_path).suffix.lower()
        
        elif file_content:
            # For base64 content, we'd need the filename to detect format
            raise HTTPException(
                status_code=400, 
                detail="Format detection requires file upload or file_path"
            )
        
        else:
            raise HTTPException(
                status_code=400, 
                detail="Either file upload or file_path must be provided"
            )
        
        # Map extensions to format names
        format_map = {
            ".pdf": "PDF",
            ".docx": "DOCX", 
            ".doc": "DOC",
            ".pptx": "PPTX",
            ".ppt": "PPT",
            ".xlsx": "XLSX",
            ".xls": "XLS",
            ".txt": "TXT",
            ".md": "Markdown",
            ".html": "HTML",
            ".htm": "HTML",
            ".epub": "EPUB",
            ".csv": "CSV",
            ".zip": "ZIP"
        }
        
        detected_format = format_map.get(extension, f"Unknown ({extension})")
        
        return FormatDetectionResponse(format=detected_format)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting format: {e}")
        return FormatDetectionResponse(
            format="Unknown",
            error=str(e)
        )

@app.get("/supported_formats", operation_id="list_supported_formats")
async def list_supported_formats():
    """List all supported document formats"""
    try:
        supported_formats = [
            "PDF", "DOCX", "DOC", "PPTX", "PPT", "XLSX", "XLS",
            "TXT", "MD", "HTML", "HTM", "EPUB", "CSV", "ZIP"
        ]
        
        return SupportedFormatsResponse(formats=supported_formats)
    
    except Exception as e:
        logger.error(f"Error listing formats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
