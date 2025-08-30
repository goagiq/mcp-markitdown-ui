"""Pydantic models for API requests and responses."""

from typing import List, Optional
from pydantic import BaseModel


class ConversionRequest(BaseModel):
    """Request model for file conversion."""
    output_format: str = "markdown"
    use_docintel: bool = False
    use_plugins: bool = False


class ConversionResponse(BaseModel):
    """Response model for file conversion."""
    job_id: str
    status: str
    message: str
    progress: Optional[int] = 0


class FormatDetectionResponse(BaseModel):
    """Response model for format detection."""
    filename: str
    mime_type: str
    extension: str
    size: int
    supported: bool


class SupportedFormat(BaseModel):
    """Model for supported format information."""
    extension: str
    description: str
    supported: bool


class SupportedFormatsResponse(BaseModel):
    """Response model for supported formats."""
    formats: List[SupportedFormat]
    total_formats: int


class BatchConversionRequest(BaseModel):
    """Request model for batch file conversion."""
    output_format: str = "markdown"
    parallel: bool = True
    max_workers: int = 4


class BatchConversionResponse(BaseModel):
    """Response model for batch file conversion."""
    job_ids: List[str]
    status: str
    message: str
    total_files: int


class JobStatusResponse(BaseModel):
    """Response model for job status."""
    job_id: str
    status: str
    progress: int
    file_path: str
    error: Optional[str] = None


class DownloadResponse(BaseModel):
    """Response model for file download."""
    job_id: str
    download_url: str
    message: str
    filename: Optional[str] = None
