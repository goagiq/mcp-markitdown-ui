#!/usr/bin/env python3
"""
Optimized PDF OCR Converter with advanced image processing techniques
Based on VisionOCR repository optimization methods
"""

import os
import sys
import logging
import base64
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple
import io

# Image processing imports
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

# Vision OCR imports
from ._vision_ocr_converter import VisionOcrConverter
from ._pdf_converter import PdfConverter
from ..converter_utils.vision_ocr.pdf_processor import PdfProcessor
from .._stream_info import StreamInfo
from .._base_converter import DocumentConverterResult

logger = logging.getLogger(__name__)

class OptimizedPdfOcrConverter:
    """
    Optimized PDF OCR Converter with advanced image processing techniques
    Incorporates methods from VisionOCR repository for better performance
    """
    
    def __init__(
        self,
        vision_model: str = "llama3.2-vision:latest",
        max_image_size: int = 800,
        compression_quality: int = 85,
        use_grayscale: bool = True,
        enable_parallel: bool = True,
        max_workers: int = 4,
        segment_size: int = 800,
        timeout: int = 300,
        fallback_to_tesseract: bool = True
    ):
        """
        Initialize the optimized PDF OCR converter
        
        Args:
            vision_model: Vision model to use for OCR
            max_image_size: Maximum image dimension for processing
            compression_quality: JPEG compression quality (1-100)
            use_grayscale: Convert images to grayscale for text-heavy documents
            enable_parallel: Enable parallel processing of image segments
            max_workers: Maximum number of parallel workers
            segment_size: Size of image segments for processing
            timeout: Processing timeout in seconds
            fallback_to_tesseract: Enable Tesseract fallback
        """
        self.vision_model = vision_model
        self.max_image_size = max_image_size
        self.compression_quality = compression_quality
        self.use_grayscale = use_grayscale
        self.enable_parallel = enable_parallel
        self.max_workers = max_workers
        self.segment_size = segment_size
        self.timeout = timeout
        self.fallback_to_tesseract = fallback_to_tesseract
        
        # Initialize converters
        self.pdf_converter = PdfConverter()
        self.vision_ocr_converter = VisionOcrConverter(vision_model=vision_model, timeout=timeout)
        self.pdf_processor = PdfProcessor()
        
        # Configure Ollama host for Docker
        self.vision_ocr_converter.ollama_client.host = "http://host.docker.internal:11434"
        self.vision_ocr_converter.ollama_client.client.base_url = "http://host.docker.internal:11434"
        
        # Define fallback vision models
        self.fallback_vision_models = [
            "llama3.2-vision:latest",
            "minicpm-v:latest",
            "llava:latest",
            "llava:7b",
            "llava:13b"
        ]
        
        logger.info(f"Initialized Optimized PDF OCR Converter with vision model: {vision_model}")
        logger.info(f"Optimization settings: max_size={max_image_size}, quality={compression_quality}, "
                   f"grayscale={use_grayscale}, parallel={enable_parallel}, workers={max_workers}")

    def convert(self, file_data: bytes, stream_info: StreamInfo) -> DocumentConverterResult:
        """
        Convert PDF using optimized OCR techniques
        """
        try:
            logger.info(f"Starting optimized PDF conversion for {stream_info.filename}")
            
            # Analyze PDF type
            pdf_type = self.pdf_processor.analyze_pdf_type(file_data)
            logger.info(f"PDF type detected: {pdf_type}")
            
            if pdf_type == "text-based":
                logger.info("Processing as text-based PDF")
                return self._process_text_based_pdf(file_data, stream_info)
            else:
                logger.info("Processing as image-based PDF with optimized OCR")
                return self._process_image_based_pdf_optimized(file_data, stream_info)
                
        except Exception as e:
            logger.error(f"Error in optimized PDF conversion: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise

    def _process_text_based_pdf(self, file_data: bytes, stream_info: StreamInfo) -> DocumentConverterResult:
        """Process text-based PDF using traditional methods"""
        return self.pdf_converter.convert(file_data, stream_info)

    def _process_image_based_pdf_optimized(self, file_data: bytes, stream_info: StreamInfo) -> DocumentConverterResult:
        """Process image-based PDF using optimized techniques"""
        try:
            # Convert PDF pages to optimized images
            optimized_images = self._convert_pdf_to_optimized_images(file_data)
            logger.info(f"Converted PDF to {len(optimized_images)} optimized images")
            
            # Process each page with optimized OCR
            all_text = []
            processing_methods = []
            
            for page_num, image_data in enumerate(optimized_images):
                logger.info(f"Processing page {page_num + 1}/{len(optimized_images)}")
                
                # Try traditional OCR first (fast)
                traditional_text = self._extract_text_with_tesseract(image_data)
                
                if traditional_text and len(traditional_text.strip()) > 50:
                    # Traditional OCR found substantial text
                    page_text = traditional_text
                    processing_method = "Traditional OCR (Tesseract)"
                    logger.info(f"Page {page_num + 1}: Used traditional OCR")
                else:
                    # Fall back to optimized vision OCR
                    page_text, method = self._process_image_with_optimized_vision_ocr(image_data, page_num)
                    processing_method = method
                
                all_text.append(page_text)
                processing_methods.append(processing_method)
                
                # Add page separator
                if page_num < len(optimized_images) - 1:
                    all_text.append(f"\n\n--- Page {page_num + 2} ---\n\n")
            
            # Combine all text
            combined_text = "".join(all_text)
            
            # Create metadata
            metadata = {
                "processing_methods": processing_methods,
                "total_pages": len(optimized_images),
                "optimization_settings": {
                    "max_image_size": self.max_image_size,
                    "compression_quality": self.compression_quality,
                    "use_grayscale": self.use_grayscale,
                    "enable_parallel": self.enable_parallel,
                    "segment_size": self.segment_size
                }
            }
            
            return DocumentConverterResult(
                markdown=combined_text,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error in optimized image-based PDF processing: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise

    def _convert_pdf_to_optimized_images(self, file_data: bytes) -> List[bytes]:
        """Convert PDF to optimized images using advanced techniques"""
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=file_data, filetype="pdf")
            optimized_images = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert to image with optimized resolution
                # Use 1.0x resolution instead of 2.0x for better performance
                mat = fitz.Matrix(1.0, 1.0)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image for optimization
                img_data = pix.tobytes("png")
                pil_image = Image.open(io.BytesIO(img_data))
                
                # Apply optimizations
                optimized_image = self._optimize_image(pil_image)
                
                # Convert back to bytes
                img_buffer = io.BytesIO()
                optimized_image.save(img_buffer, format='JPEG', quality=self.compression_quality, optimize=True)
                optimized_images.append(img_buffer.getvalue())
                
                logger.info(f"Optimized page {page_num + 1}: {len(img_data)} -> {len(optimized_images[-1])} bytes")
            
            doc.close()
            return optimized_images
            
        except Exception as e:
            logger.error(f"Error converting PDF to optimized images: {e}")
            raise

    def _optimize_image(self, image: Image.Image) -> Image.Image:
        """Apply image optimizations for better OCR performance"""
        try:
            # Resize if too large
            if max(image.size) > self.max_image_size:
                ratio = self.max_image_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"Resized image to {new_size}")
            
            # Convert to grayscale for text-heavy documents
            if self.use_grayscale:
                image = image.convert('L')
                logger.info("Converted to grayscale")
            
            # Apply image enhancements for better text recognition
            # Increase contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # Apply slight sharpening
            image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            # Remove noise with slight blur
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            return image
            
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return image

    def _process_image_with_optimized_vision_ocr(self, image_data: bytes, page_num: int) -> Tuple[str, str]:
        """Process image with optimized vision OCR including segmentation"""
        try:
            # Convert bytes to PIL Image
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Check if image needs segmentation
            if max(pil_image.size) > self.segment_size:
                logger.info(f"Segmenting large image {pil_image.size} into smaller chunks")
                return self._process_image_with_segmentation(pil_image, page_num)
            else:
                logger.info(f"Processing image directly (size: {pil_image.size})")
                return self._process_single_image(pil_image, page_num)
                
        except Exception as e:
            logger.error(f"Error in optimized vision OCR: {e}")
            return "", "Error"

    def _process_image_with_segmentation(self, image: Image.Image, page_num: int) -> Tuple[str, str]:
        """Process large image by breaking it into segments"""
        try:
            # Create image segments
            segments = self._create_image_segments(image)
            logger.info(f"Created {len(segments)} image segments")
            
            if self.enable_parallel and len(segments) > 1:
                return self._process_segments_parallel(segments, page_num)
            else:
                return self._process_segments_sequential(segments, page_num)
                
        except Exception as e:
            logger.error(f"Error in image segmentation: {e}")
            return "", "Error"

    def _create_image_segments(self, image: Image.Image) -> List[Image.Image]:
        """Create smaller segments from large image"""
        segments = []
        width, height = image.size
        
        # Calculate segment grid
        cols = max(1, width // self.segment_size)
        rows = max(1, height // self.segment_size)
        
        segment_width = width // cols
        segment_height = height // rows
        
        logger.info(f"Creating {cols}x{rows} grid of {segment_width}x{segment_height} segments")
        
        for row in range(rows):
            for col in range(cols):
                left = col * segment_width
                top = row * segment_height
                right = left + segment_width if col < cols - 1 else width
                bottom = top + segment_height if row < rows - 1 else height
                
                segment = image.crop((left, top, right, bottom))
                segments.append(segment)
        
        return segments

    def _process_segments_parallel(self, segments: List[Image.Image], page_num: int) -> Tuple[str, str]:
        """Process image segments in parallel"""
        try:
            all_texts = []
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all segments for processing
                future_to_segment = {
                    executor.submit(self._process_single_segment, segment, i): i 
                    for i, segment in enumerate(segments)
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_segment, timeout=self.timeout):
                    segment_idx = future_to_segment[future]
                    try:
                        segment_text = future.result()
                        all_texts.append((segment_idx, segment_text))
                        logger.info(f"Completed segment {segment_idx + 1}/{len(segments)}")
                    except Exception as e:
                        logger.error(f"Error processing segment {segment_idx}: {e}")
                        all_texts.append((segment_idx, ""))
            
            # Combine results in order
            combined_text = self._combine_segment_texts(all_texts)
            return combined_text, f"Vision OCR (Parallel, {len(segments)} segments)"
            
        except Exception as e:
            logger.error(f"Error in parallel segment processing: {e}")
            return "", "Error"

    def _process_segments_sequential(self, segments: List[Image.Image], page_num: int) -> Tuple[str, str]:
        """Process image segments sequentially"""
        try:
            all_texts = []
            
            for i, segment in enumerate(segments):
                logger.info(f"Processing segment {i + 1}/{len(segments)}")
                segment_text = self._process_single_segment(segment, i)
                all_texts.append((i, segment_text))
            
            # Combine results
            combined_text = self._combine_segment_texts(all_texts)
            return combined_text, f"Vision OCR (Sequential, {len(segments)} segments)"
            
        except Exception as e:
            logger.error(f"Error in sequential segment processing: {e}")
            return "", "Error"

    def _process_single_segment(self, segment: Image.Image, segment_idx: int) -> str:
        """Process a single image segment with vision OCR"""
        try:
            # Convert to base64
            img_buffer = io.BytesIO()
            segment.save(img_buffer, format='JPEG', quality=self.compression_quality, optimize=True)
            img_data = img_buffer.getvalue()
            img_b64 = base64.b64encode(img_data).decode('utf-8')
            
            # Try vision models in order
            for model in self.fallback_vision_models:
                try:
                    logger.info(f"Trying vision model {model} for segment {segment_idx + 1}")
                    
                    # Use direct HTTP call with optimized timeout
                    import requests
                    url = "http://host.docker.internal:11434/api/chat"
                    payload = {
                        "model": model,
                        "messages": [
                            {
                                "role": "user",
                                "content": "Extract all text from this image. Return only the extracted text without any additional formatting or commentary.",
                                "images": [img_b64]
                            }
                        ]
                    }
                    
                    response = requests.post(url, json=payload, timeout=60)  # Shorter timeout for segments
                    
                    if response.status_code == 200:
                        # Parse streaming response
                        content_parts = []
                        for line in response.text.strip().split('\n'):
                            if line.strip():
                                try:
                                    data = json.loads(line)
                                    if 'message' in data and 'content' in data['message']:
                                        content_parts.append(data['message']['content'])
                                except json.JSONDecodeError:
                                    continue
                        
                        if content_parts:
                            text = ''.join(content_parts).strip()
                            if text:
                                logger.info(f"Successfully extracted text from segment {segment_idx + 1} with {model}")
                                return text
                    
                except Exception as e:
                    logger.warning(f"Model {model} failed for segment {segment_idx + 1}: {e}")
                    continue
            
            logger.warning(f"All vision models failed for segment {segment_idx + 1}")
            return ""
            
        except Exception as e:
            logger.error(f"Error processing segment {segment_idx + 1}: {e}")
            return ""

    def _process_single_image(self, image: Image.Image, page_num: int) -> Tuple[str, str]:
        """Process a single image without segmentation"""
        try:
            # Convert to base64
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=self.compression_quality, optimize=True)
            img_data = img_buffer.getvalue()
            img_b64 = base64.b64encode(img_data).decode('utf-8')
            
            # Try vision models in order
            for model in self.fallback_vision_models:
                try:
                    logger.info(f"Trying vision model {model} for page {page_num + 1}")
                    
                    import requests
                    url = "http://host.docker.internal:11434/api/chat"
                    payload = {
                        "model": model,
                        "messages": [
                            {
                                "role": "user",
                                "content": "Extract all text from this image. Return only the extracted text without any additional formatting or commentary.",
                                "images": [img_b64]
                            }
                        ]
                    }
                    
                    response = requests.post(url, json=payload, timeout=120)
                    
                    if response.status_code == 200:
                        # Parse streaming response
                        content_parts = []
                        for line in response.text.strip().split('\n'):
                            if line.strip():
                                try:
                                    data = json.loads(line)
                                    if 'message' in data and 'content' in data['message']:
                                        content_parts.append(data['message']['content'])
                                except json.JSONDecodeError:
                                    continue
                        
                        if content_parts:
                            text = ''.join(content_parts).strip()
                            if text:
                                logger.info(f"Successfully extracted text from page {page_num + 1} with {model}")
                                return text, f"Vision OCR ({model})"
                    
                except Exception as e:
                    logger.warning(f"Model {model} failed for page {page_num + 1}: {e}")
                    continue
            
            logger.warning(f"All vision models failed for page {page_num + 1}")
            return "", "Vision OCR failed"
            
        except Exception as e:
            logger.error(f"Error processing single image for page {page_num + 1}: {e}")
            return "", "Error"

    def _combine_segment_texts(self, segment_texts: List[Tuple[int, str]]) -> str:
        """Combine text from multiple segments in order"""
        try:
            # Sort by segment index
            segment_texts.sort(key=lambda x: x[0])
            
            # Combine texts with separators
            combined = []
            for idx, text in segment_texts:
                if text.strip():
                    combined.append(text.strip())
            
            return "\n\n".join(combined)
            
        except Exception as e:
            logger.error(f"Error combining segment texts: {e}")
            return ""

    def _extract_text_with_tesseract(self, image_data: bytes) -> str:
        """Extract text using Tesseract OCR"""
        try:
            if not self.fallback_to_tesseract:
                return ""
            
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image, config='--psm 6')
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error in Tesseract OCR: {e}")
            return ""
