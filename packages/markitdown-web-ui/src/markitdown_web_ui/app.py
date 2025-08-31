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
from typing import List, Optional

# Add the packages directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../markitdown/src'))

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

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
markitdown = MarkItDown()

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'pdf', 'docx', 'doc', 'pptx', 'ppt', 'xlsx', 'xls', 
    'txt', 'md', 'html', 'htm', 'epub', 'csv', 'zip'
}

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title="MarkItDown Web UI",
        description="Web interface for converting files to markdown",
        version="1.0.0"
    )
    
    # Configure directories
    input_dir = os.environ.get('INPUT_DIR', '/app/input')
    output_dir = os.environ.get('OUTPUT_DIR', '/app/output')
    
    # Ensure directories exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up templates
    templates = Jinja2Templates(directory="templates")
    
    # Mount static files
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/", response_class=HTMLResponse)
    async def index(request):
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
            filepath = os.path.join(input_dir, filename)
            
            with open(filepath, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            logger.info(f"Processing file: {filename}")
            
            # Convert file using MarkItDown
            result = markitdown.convert(filepath)
            
            # Save result to output folder
            output_filename = f"{Path(filename).stem}.md"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.markdown)
            
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
    
    @app.get("/download/{filename}")
    async def download_file(filename: str):
        """Download converted markdown file"""
        try:
            file_path = os.path.join(output_dir, filename)
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
            for file in os.listdir(input_dir):
                file_path = os.path.join(input_dir, file)
                if os.path.isfile(file_path):
                    input_files.append({
                        "name": file,
                        "size": os.path.getsize(file_path)
                    })
            
            # List output files
            for file in os.listdir(output_dir):
                file_path = os.path.join(output_dir, file)
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

# For direct execution
if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get('PORT', 8100))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting MarkItDown web server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
