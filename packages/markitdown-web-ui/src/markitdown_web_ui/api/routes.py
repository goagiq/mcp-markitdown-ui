"""API routes for MarkItDown Web UI."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..utils.file_handling import (
    save_upload_file, get_file_info, validate_file_extension, validate_file_size,
    get_output_path, list_input_files, list_output_files, clear_output_directory
)
from ..utils.config import get_settings
from .models import ConversionRequest, ConversionResponse, FormatDetectionResponse, SupportedFormatsResponse

api_router = APIRouter()


class ConversionJob(BaseModel):
    """Conversion job model."""
    job_id: str
    status: str
    file_path: str
    progress: int = 0


# In-memory storage for jobs (replace with database in production)
conversion_jobs: dict[str, ConversionJob] = {}


@api_router.post("/convert", response_model=ConversionResponse)
async def convert_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    output_format: str = "markdown"
) -> ConversionResponse:
    """Convert a single file to Markdown."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not validate_file_extension(file.filename):
            raise HTTPException(status_code=400, detail="File type not supported")
        
        # Save file
        file_path = await save_upload_file(file)
        file_info = get_file_info(file_path)
        
        if not validate_file_size(file_info["size"]):
            raise HTTPException(status_code=400, detail="File too large")
        
        # Create job
        job_id = str(uuid.uuid4())
        job = ConversionJob(
            job_id=job_id,
            status="processing",
            file_path=str(file_path)
        )
        conversion_jobs[job_id] = job
        
        # Start conversion in background
        background_tasks.add_task(process_conversion, job_id, str(file_path), output_format)
        
        return ConversionResponse(
            job_id=job_id,
            status="processing",
            message="Conversion started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/convert/batch")
async def convert_batch_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    output_format: str = "markdown"
) -> JSONResponse:
    """Convert multiple files to Markdown."""
    try:
        job_ids = []
        
        for file in files:
            # Validate file
            if not file.filename:
                continue
            
            if not validate_file_extension(file.filename):
                continue
            
            # Save file
            file_path = await save_upload_file(file)
            file_info = get_file_info(file_path)
            
            if not validate_file_size(file_info["size"]):
                continue
            
            # Create job
            job_id = str(uuid.uuid4())
            job = ConversionJob(
                job_id=job_id,
                status="processing",
                file_path=str(file_path)
            )
            conversion_jobs[job_id] = job
            job_ids.append(job_id)
            
            # Start conversion in background
            background_tasks.add_task(process_conversion, job_id, str(file_path), output_format)
        
        return JSONResponse({
            "job_ids": job_ids,
            "status": "processing",
            "message": f"Started conversion of {len(job_ids)} files"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/detect", response_model=FormatDetectionResponse)
async def detect_format(file: UploadFile = File(...)) -> FormatDetectionResponse:
    """Detect the format of a file."""
    try:
        # Save file temporarily
        file_path = await save_upload_file(file)
        file_info = get_file_info(file_path)
        
        # Get format information
        format_info = {
            "filename": file_info["filename"],
            "mime_type": file_info["mime_type"],
            "extension": file_info["extension"],
            "size": file_info["size"],
            "supported": validate_file_extension(file_info["filename"])
        }
        
        return FormatDetectionResponse(**format_info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/formats", response_model=SupportedFormatsResponse)
async def get_supported_formats() -> SupportedFormatsResponse:
    """Get list of supported file formats."""
    settings = get_settings()
    
    formats = []
    for ext in settings.allowed_extensions:
        formats.append({
            "extension": ext,
            "description": f"Files with {ext} extension",
            "supported": True
        })
    
    return SupportedFormatsResponse(formats=formats, total_formats=len(formats))


@api_router.get("/status/{job_id}")
async def get_conversion_status(job_id: str) -> JSONResponse:
    """Get the status of a conversion job."""
    if job_id not in conversion_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = conversion_jobs[job_id]
    return JSONResponse({
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "file_path": job.file_path
    })


@api_router.get("/download/{job_id}")
async def download_converted_file(job_id: str) -> JSONResponse:
    """Download a converted file."""
    if job_id not in conversion_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = conversion_jobs[job_id]
    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Conversion not completed")
    
    # TODO: Implement file download logic
    return JSONResponse({
        "job_id": job_id,
        "download_url": f"/download/{job_id}",
        "message": "File ready for download"
    })


async def process_conversion(job_id: str, file_path: str, output_format: str) -> None:
    """Process a conversion job in the background."""
    try:
        # Update job status
        if job_id in conversion_jobs:
            conversion_jobs[job_id].status = "processing"
            conversion_jobs[job_id].progress = 10
        
        # Import MarkItDown for actual conversion
        from markitdown import MarkItDown
        from pathlib import Path
        import asyncio
        
        # Update progress
        if job_id in conversion_jobs:
            conversion_jobs[job_id].progress = 30
        
        # Initialize MarkItDown
        md = MarkItDown()
        
        # Update progress
        if job_id in conversion_jobs:
            conversion_jobs[job_id].progress = 50
        
        # Perform the actual conversion
        input_path = Path(file_path)
        output_path = get_output_path(input_path.name, output_format)
        
        # Convert the file using the correct MarkItDown API
        result = md.convert(str(input_path))
        
        # Write the result to the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result.markdown)
        
        # Update progress
        if job_id in conversion_jobs:
            conversion_jobs[job_id].progress = 90
        
        # Update job status to completed
        if job_id in conversion_jobs:
            conversion_jobs[job_id].status = "completed"
            conversion_jobs[job_id].progress = 100
            
    except Exception as e:
        # Update job status on error
        if job_id in conversion_jobs:
            conversion_jobs[job_id].status = "failed"
            conversion_jobs[job_id].progress = 0
            print(f"Conversion error: {str(e)}")


# Directory Management Endpoints

@api_router.get("/directories/input")
async def list_input_directory() -> JSONResponse:
    """List all files in the input directory."""
    try:
        files = list_input_files()
        return JSONResponse({
            "directory": "input",
            "files": files,
            "count": len(files)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/directories/output")
async def list_output_directory() -> JSONResponse:
    """List all files in the output directory."""
    try:
        files = list_output_files()
        return JSONResponse({
            "directory": "output",
            "files": files,
            "count": len(files)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/directories/output/clear")
async def clear_output_directory_endpoint() -> JSONResponse:
    """Clear all files from the output directory."""
    try:
        success = clear_output_directory()
        if success:
            return JSONResponse({
                "message": "Output directory cleared successfully",
                "success": True
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to clear output directory")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/directories/input/upload")
async def upload_to_input_directory(
    file: UploadFile = File(...),
    filename: Optional[str] = None
) -> JSONResponse:
    """Upload a file directly to the input directory."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not validate_file_extension(file.filename):
            raise HTTPException(status_code=400, detail="File type not supported")
        
        # Save file to input directory
        file_path = await save_upload_file(file, filename, use_input_dir=True)
        file_info = get_file_info(file_path)
        
        if not validate_file_size(file_info["size"]):
            raise HTTPException(status_code=400, detail="File too large")
        
        return JSONResponse({
            "message": "File uploaded to input directory successfully",
            "file_info": file_info,
            "success": True
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/directories/config")
async def get_directory_config() -> JSONResponse:
    """Get the current directory configuration."""
    settings = get_settings()
    return JSONResponse({
        "input_dir": str(settings.input_dir),
        "output_dir": str(settings.output_dir),
        "upload_dir": str(settings.upload_dir),
        "configurable": True
    })
