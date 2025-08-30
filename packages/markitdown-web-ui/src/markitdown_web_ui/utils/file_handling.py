"""File handling utilities for MarkItDown Web UI."""

import aiofiles
import magic
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

from .config import get_settings


async def save_upload_file(
    upload_file: UploadFile, 
    filename: Optional[str] = None, 
    use_input_dir: bool = False
) -> Path:
    """Save an uploaded file to the upload directory or input directory."""
    settings = get_settings()
    
    # Choose directory based on parameter
    if use_input_dir:
        target_dir = settings.input_dir
    else:
        target_dir = settings.upload_dir
    
    # Create target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename if not provided
    if filename is None:
        filename = upload_file.filename
    
    file_path = target_dir / filename
    
    # Save the file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await upload_file.read()
        await f.write(content)
    
    return file_path


def get_file_info(file_path: Path) -> dict:
    """Get information about a file."""
    try:
        # Get file size
        file_size = file_path.stat().st_size
        
        # Get MIME type
        mime_type = magic.from_file(str(file_path), mime=True)
        
        # Get file extension
        extension = file_path.suffix.lower()
        
        return {
            "filename": file_path.name,
            "size": file_size,
            "mime_type": mime_type,
            "extension": extension,
            "path": str(file_path)
        }
    except Exception as e:
        return {
            "filename": file_path.name,
            "error": str(e)
        }


def validate_file_extension(filename: str) -> bool:
    """Validate if the file extension is allowed."""
    settings = get_settings()
    extension = Path(filename).suffix.lower()
    return extension in settings.allowed_extensions


def validate_file_size(file_size: int) -> bool:
    """Validate if the file size is within limits."""
    settings = get_settings()
    return file_size <= settings.max_file_size


def get_output_path(filename: str, output_format: str = "markdown") -> Path:
    """Get the output path for a converted file."""
    settings = get_settings()
    
    # Create output directory if it doesn't exist
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename
    stem = Path(filename).stem
    output_filename = f"{stem}.{output_format}"
    
    return settings.output_dir / output_filename


def list_input_files() -> list[dict]:
    """List all files in the input directory."""
    settings = get_settings()
    
    if not settings.input_dir.exists():
        return []
    
    files = []
    for file_path in settings.input_dir.iterdir():
        if file_path.is_file():
            files.append(get_file_info(file_path))
    
    return files


def list_output_files() -> list[dict]:
    """List all files in the output directory."""
    settings = get_settings()
    
    if not settings.output_dir.exists():
        return []
    
    files = []
    for file_path in settings.output_dir.iterdir():
        if file_path.is_file():
            files.append(get_file_info(file_path))
    
    return files


def clear_output_directory() -> bool:
    """Clear all files from the output directory."""
    settings = get_settings()
    
    if not settings.output_dir.exists():
        return True
    
    try:
        for file_path in settings.output_dir.iterdir():
            if file_path.is_file():
                file_path.unlink()
        return True
    except Exception:
        return False
