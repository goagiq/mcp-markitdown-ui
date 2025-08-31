"""
FastAPI web application for MarkItDown
Provides a web interface for file conversion to markdown
"""

import os
import sys
import logging
import tempfile
import traceback
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add the packages directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../markitdown/src'))

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

import asyncio
from typing import List, Dict, Any
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

try:
    from markitdown import MarkItDown
    from markitdown._stream_info import StreamInfo
except ImportError:
    # Try alternative import paths
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../markitdown/src'))
    from markitdown._markitdown import MarkItDown
    from markitdown._stream_info import StreamInfo

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MarkItDown
markitdown = MarkItDown(enable_builtins=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf', 'docx', 'doc', 'pptx', 'ppt', 'xlsx', 'xls', 
    'txt', 'md', 'html', 'htm', 'epub', 'csv', 'zip'
}

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class ConversionResult:
    """Represents the result of a file conversion"""
    def __init__(self, filename: str, success: bool, markdown: str = None, error: str = None, processing_time: float = 0):
        self.filename = filename
        self.success = success
        self.markdown = markdown
        self.error = error
        self.processing_time = processing_time

async def convert_file(filepath: str) -> ConversionResult:
    """Convert a single file to markdown"""
    start_time = time.time()
    filename = os.path.basename(filepath)
    
    try:
        logger.info(f"Processing file: {filename}")
        
        # Convert file using MarkItDown
        result = markitdown.convert(filepath)
        
        processing_time = time.time() - start_time
        
        # Save markdown to output directory
        output_filename = f"{Path(filename).stem}.md"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.markdown)
        
        logger.info(f"Successfully converted {filename} in {processing_time:.2f}s")
        
        return ConversionResult(
            filename=filename,
            success=True,
            markdown=result.markdown,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Conversion failed: {str(e)}"
        logger.error(f"Error converting file {filename}: {error_msg}")
        logger.error(f"Traceback: {e}")
        
        return ConversionResult(
            filename=filename,
            success=False,
            error=error_msg,
            processing_time=processing_time
        )

async def process_bulk_conversion(files: List[UploadFile]) -> Dict[str, Any]:
    """Process multiple files with parallel execution and progress tracking"""
    start_time = time.time()
    results = []
    
    # Save uploaded files
    saved_files = []
    for file in files:
        try:
            filepath = os.path.join(INPUT_DIR, file.filename)
            with open(filepath, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            saved_files.append(filepath)
            logger.info(f"Saved uploaded file: {file.filename}")
        except Exception as e:
            logger.error(f"Error saving file {file.filename}: {e}")
            results.append(ConversionResult(
                filename=file.filename,
                success=False,
                error=f"Failed to save file: {str(e)}"
            ))
    
    # Process files in parallel
    if saved_files:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, lambda f=f: asyncio.run(convert_file(f))) for f in saved_files]
        
        # Wait for all conversions to complete
        conversion_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results
        for i, result in enumerate(conversion_results):
            if isinstance(result, Exception):
                filename = os.path.basename(saved_files[i]) if i < len(saved_files) else "unknown"
                results.append(ConversionResult(
                    filename=filename,
                    success=False,
                    error=f"Processing exception: {str(result)}"
                ))
            else:
                results.append(result)
    
    total_time = time.time() - start_time
    
    # Generate summary
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    summary = {
        "total_files": len(files),
        "successful": len(successful),
        "failed": len(failed),
        "total_processing_time": total_time,
        "average_time_per_file": total_time / len(files) if files else 0,
        "results": [
            {
                "filename": r.filename,
                "success": r.success,
                "processing_time": r.processing_time,
                "error": r.error if not r.success else None,
                "markdown_length": len(r.markdown) if r.success else 0
            }
            for r in results
        ]
    }
    
    return summary

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title="MarkItDown Web UI",
        description="Web interface for converting files to markdown",
        version="1.0.0"
    )
    
    # Configure directories
    # Use absolute paths to ensure files are saved in the correct location
    # Get the workspace root directory (3 levels up from the app.py file to reach project root)
    current_file = os.path.abspath(__file__)
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
    INPUT_DIR = os.environ.get('INPUT_DIR', os.path.join(workspace_root, 'uploads'))
    OUTPUT_DIR = os.environ.get('OUTPUT_DIR', os.path.join(workspace_root, 'output'))
    
    # Ensure directories exist
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Set up templates
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
    templates = Jinja2Templates(directory=templates_dir)
    
    # Mount static files
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        """Main page with file upload form"""
        return templates.TemplateResponse("index.html", {"request": request})
    
    @app.get("/health")
    async def health():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "markitdown-web-ui",
            "version": "1.0.0"
        }
    
    @app.post("/convert")
    async def convert_file(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...)
    ):
        """Convert uploaded file to markdown"""
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No file selected")
            
            if not allowed_file(file.filename):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            
            # Save uploaded file
            filename = file.filename
            filepath = os.path.join(INPUT_DIR, filename)
            
            with open(filepath, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            logger.info(f"Processing file: {filename}")
            
            # Convert file using MarkItDown
            result = markitdown.convert(filepath)
            
            # Save result to output folder
            output_filename = f"{Path(filename).stem}.md"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            
            logger.info(f"Saving markdown to: {output_path}")
            logger.info(f"Output directory exists: {os.path.exists(OUTPUT_DIR)}")
            logger.info(f"Output directory: {OUTPUT_DIR}")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.markdown)
            
            logger.info(f"Successfully saved markdown file: {output_path}")
            
            # Return result
            return {
                "success": True,
                "filename": filename,
                "output_filename": output_filename,
                "text_length": len(result.markdown),
                "preview": result.markdown[:500] + '...' if len(result.markdown) > 500 else result.markdown,
                "download_url": f"/download/{output_filename}"
            }
            
        except Exception as e:
            logger.error(f"Error converting file: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

    @app.post("/convert-bulk")
    async def convert_bulk_files(
        background_tasks: BackgroundTasks,
        files: List[UploadFile] = File(...)
    ):
        """Convert multiple uploaded files to markdown"""
        try:
            logger.info(f"Bulk conversion received {len(files)} files")
            for i, file in enumerate(files):
                logger.info(f"File {i}: {file.filename}")
            
            if not files:
                raise HTTPException(status_code=400, detail="No files selected")
            
            results = []
            errors = []
            
            for file in files:
                try:
                    # Validate file
                    if not file.filename:
                        errors.append({"filename": "Unknown", "error": "No filename provided"})
                        continue
                    
                    if not allowed_file(file.filename):
                        errors.append({
                            "filename": file.filename, 
                            "error": f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                        })
                        continue
                    
                    # Save uploaded file
                    filename = file.filename
                    filepath = os.path.join(INPUT_DIR, filename)
                    
                    with open(filepath, "wb") as buffer:
                        content = await file.read()
                        buffer.write(content)
                    
                    logger.info(f"Processing file: {filename}")
                    
                    # Convert file using MarkItDown
                    result = markitdown.convert(filepath)
                    
                    # Save result to output folder
                    output_filename = f"{Path(filename).stem}.md"
                    output_path = os.path.join(OUTPUT_DIR, output_filename)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(result.markdown)
                    
                    results.append({
                        "success": True,
                        "filename": filename,
                        "output_filename": output_filename,
                        "text_length": len(result.markdown),
                        "preview": result.markdown[:200] + '...' if len(result.markdown) > 200 else result.markdown,
                        "download_url": f"/download/{output_filename}"
                    })
                    
                except Exception as e:
                    logger.error(f"Error converting file {file.filename}: {e}")
                    errors.append({
                        "filename": file.filename,
                        "error": str(e)
                    })
            
            response_data = {
                "success": True,
                "total_files": len(files),
                "successful_conversions": len(results),
                "failed_conversions": len(errors),
                "results": results,
                "errors": errors
            }
            logger.info(f"Bulk conversion completed. Returning: {response_data}")
            return response_data
            
        except Exception as e:
            logger.error(f"Error in bulk conversion: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Bulk conversion failed: {str(e)}")
    
    @app.get("/download/{filename}")
    async def download_file(filename: str):
        """Download converted markdown file"""
        try:
            file_path = os.path.join(OUTPUT_DIR, filename)
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            return FileResponse(
                file_path, 
                media_type='text/markdown',
                filename=filename
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
    
    @app.get("/files")
    async def list_files():
        """List available files in input and output folders"""
        try:
            input_files = []
            output_files = []
            
            # List input files
            for file in os.listdir(INPUT_DIR):
                file_path = os.path.join(INPUT_DIR, file)
                if os.path.isfile(file_path):
                    input_files.append({
                        "name": file,
                        "size": os.path.getsize(file_path)
                    })
            
            # List output files
            for file in os.listdir(OUTPUT_DIR):
                file_path = os.path.join(OUTPUT_DIR, file)
                if os.path.isfile(file_path):
                    output_files.append({
                        "name": file,
                        "size": os.path.getsize(file_path),
                        "download_url": f"/download/{file}"
                    })
            
            return {
                "input_files": input_files,
                "output_files": output_files
            }
        
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")
    
    return app

# Create the app instance for uvicorn
app = create_app()

# For direct execution
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8200))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting MarkItDown web server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
