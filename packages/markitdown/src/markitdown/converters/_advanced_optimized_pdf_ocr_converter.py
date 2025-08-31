import traceback
#!/usr/bin/env python3
"""
Advanced Optimized PDF OCR Converter with enhanced performance features
Based on VisionOCR repository optimization methods with additional improvements
"""

import os
import sys
import logging
import base64
import json
import time
import threading
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple, Any, BinaryIO
import io
from collections import defaultdict
import pickle

# Image processing imports
import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract

# Vision OCR imports
from ._vision_ocr_converter import VisionOcrConverter
from ._pdf_converter import PdfConverter
from ..converter_utils.vision_ocr.pdf_processor import PdfProcessor
from .._stream_info import StreamInfo
from .._base_converter import DocumentConverterResult

logger = logging.getLogger(__name__)

class ModelPerformanceTracker:
    """Track model performance for smart model selection"""
    
    def __init__(self, cache_file: str = "model_performance_cache.pkl"):
        self.cache_file = cache_file
        self.performance_data = defaultdict(lambda: {
            'success_count': 0,
            'failure_count': 0,
            'avg_response_time': 0.0,
            'last_used': 0.0
        })
        self.load_performance_data()
    
    def load_performance_data(self):
        """Load performance data from cache"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    self.performance_data = pickle.load(f)
                logger.info(f"Loaded performance data for {len(self.performance_data)} models")
        except Exception as e:
            logger.warning(f"Could not load performance data: {e}")
    
    def save_performance_data(self):
        """Save performance data to cache"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.performance_data, f)
        except Exception as e:
            logger.warning(f"Could not save performance data: {e}")
    
    def record_success(self, model: str, response_time: float):
        """Record successful model usage"""
        data = self.performance_data[model]
        data['success_count'] += 1
        data['last_used'] = time.time()
        
        # Update average response time
        total_attempts = data['success_count'] + data['failure_count']
        data['avg_response_time'] = (
            (data['avg_response_time'] * (total_attempts - 1) + response_time) / total_attempts
        )
    
    def record_failure(self, model: str):
        """Record failed model usage"""
        data = self.performance_data[model]
        data['failure_count'] += 1
        data['last_used'] = time.time()
    
    def get_model_rankings(self, models: List[str]) -> List[str]:
        """Get models ranked by performance"""
        def score_model(model):
            if model not in self.performance_data:
                return 0.0
            
            data = self.performance_data[model]
            total_attempts = data['success_count'] + data['failure_count']
            
            if total_attempts == 0:
                return 0.0
            
            success_rate = data['success_count'] / total_attempts
            avg_time = data['avg_response_time'] if data['avg_response_time'] > 0 else 60.0
            
            # Score based on success rate and speed (higher is better)
            return success_rate * (60.0 / max(avg_time, 1.0))
        
        return sorted(models, key=score_model, reverse=True)

class ImageQualityAssessor:
    """Assess image quality and determine optimal processing strategy"""
    
    @staticmethod
    def assess_image_quality(image: Image.Image) -> Dict[str, Any]:
        """Assess image quality and return metrics"""
        try:
            # Convert to numpy array for analysis
            img_array = np.array(image.convert('L'))
            
            # Calculate quality metrics
            metrics = {
                'resolution': image.size[0] * image.size[1],
                'contrast': np.std(img_array),
                'brightness': np.mean(img_array),
                'sharpness': ImageQualityAssessor._calculate_sharpness(img_array),
                'text_density': ImageQualityAssessor._estimate_text_density(img_array),
                'noise_level': ImageQualityAssessor._estimate_noise_level(img_array)
            }
            
            # Calculate overall quality score (0-100)
            quality_score = (
                min(metrics['resolution'] / 1000000, 30) +  # Resolution contribution
                min(metrics['contrast'] / 50, 20) +         # Contrast contribution
                min(metrics['sharpness'] / 100, 25) +       # Sharpness contribution
                min(metrics['text_density'] * 100, 15) +    # Text density contribution
                max(0, 10 - metrics['noise_level'] / 10)    # Noise penalty
            )
            
            metrics['quality_score'] = min(100, max(0, quality_score))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error assessing image quality: {e}")
            return {'quality_score': 50}  # Default medium quality
    
    @staticmethod
    def _calculate_sharpness(img_array: np.ndarray) -> float:
        """Calculate image sharpness using Laplacian variance"""
        try:
            laplacian = cv2.Laplacian(img_array, cv2.CV_64F)
            return laplacian.var()
        except:
            return 0.0
    
    @staticmethod
    def _estimate_text_density(img_array: np.ndarray) -> float:
        """Estimate text density using edge detection"""
        try:
            edges = cv2.Canny(img_array, 50, 150)
            return np.sum(edges > 0) / edges.size
        except:
            return 0.0
    
    @staticmethod
    def _estimate_noise_level(img_array: np.ndarray) -> float:
        """Estimate noise level using high-frequency components"""
        try:
            # Apply high-pass filter
            kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            filtered = cv2.filter2D(img_array, -1, kernel)
            return np.std(filtered)
        except:
            return 0.0

class AdvancedOptimizedPdfOcrConverter:
    """
    Advanced Optimized PDF OCR Converter with enhanced performance features
    Incorporates methods from VisionOCR repository plus additional optimizations
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
        fallback_to_tesseract: bool = True,
        enable_caching: bool = True,
        enable_smart_model_selection: bool = True,
        enable_quality_assessment: bool = True,
        cache_dir: str = "ocr_cache"
    ):
        """
        Initialize the advanced optimized PDF OCR converter
        
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
            enable_caching: Enable result caching
            enable_smart_model_selection: Enable smart model selection
            enable_quality_assessment: Enable image quality assessment
            cache_dir: Directory for caching results
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
        self.enable_caching = enable_caching
        self.enable_smart_model_selection = enable_smart_model_selection
        self.enable_quality_assessment = enable_quality_assessment
        self.cache_dir = cache_dir
        
        # Initialize converters
        self.pdf_converter = PdfConverter()
        self.vision_ocr_converter = VisionOcrConverter(model=vision_model, timeout=timeout)
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
        
        # Initialize performance tracking and caching
        if self.enable_smart_model_selection:
            self.model_tracker = ModelPerformanceTracker()
        
        if self.enable_caching:
            self._setup_cache()
        
        if self.enable_quality_assessment:
            self.quality_assessor = ImageQualityAssessor()
        
        logger.info(f"Initialized Advanced Optimized PDF OCR Converter with vision model: {vision_model}")
        logger.info(f"Advanced features: caching={enable_caching}, smart_selection={enable_smart_model_selection}, "
                   f"quality_assessment={enable_quality_assessment}")

    def accepts(
        self,
        file_stream: BinaryIO,
        stream_info: StreamInfo,
        **kwargs: Any,
    ) -> bool:
        """
        Check if this converter can handle the given file.
        
        Args:
            file_stream: File stream to check
            stream_info: Stream information
            **kwargs: Additional arguments
            
        Returns:
            True if converter can handle the file, False otherwise
        """
        mimetype = (stream_info.mimetype or "").lower()
        extension = (stream_info.extension or "").lower()
        
        # Check file extension
        if extension in ['.pdf']:
            return True
        
        # Check MIME type
        if mimetype.startswith('application/pdf'):
            return True
        
        return False

    def _setup_cache(self):
        """Setup caching directory"""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Cache directory setup: {self.cache_dir}")
        except Exception as e:
            logger.warning(f"Could not setup cache directory: {e}")
            self.enable_caching = False

    def _get_cache_key(self, image_data: bytes) -> str:
        """Generate cache key for image data"""
        return hashlib.md5(image_data).hexdigest()

    def _get_cached_result(self, cache_key: str) -> Optional[str]:
        """Get cached result if available"""
        if not self.enable_caching:
            return None
        
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.txt")
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
        
        return None

    def _save_cached_result(self, cache_key: str, result: str):
        """Save result to cache"""
        if not self.enable_caching:
            return
        
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.txt")
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(result)
        except Exception as e:
            logger.warning(f"Error saving cache: {e}")

    def convert(self, file_path_or_stream, stream_info: Optional[StreamInfo] = None, **kwargs) -> DocumentConverterResult:
        """
        Convert PDF using advanced optimized OCR techniques
        """
        try:
            # Handle both file path (string) and file stream (BinaryIO)
            if isinstance(file_path_or_stream, str):
                # File path provided
                with open(file_path_or_stream, 'rb') as f:
                    file_data = f.read()
                filename = stream_info.filename if stream_info and stream_info.filename else os.path.basename(file_path_or_stream)
            else:
                # File stream provided
                file_data = file_path_or_stream.read()
                filename = stream_info.filename if stream_info and stream_info.filename else "unknown"
                # Reset stream position
                file_path_or_stream.seek(0)
            
            logger.info(f"Starting advanced optimized PDF conversion for {filename}")
            
            # Analyze PDF type
            pdf_type = self.pdf_processor.analyze_pdf_type(file_data)
            logger.info(f"PDF type detected: {pdf_type}")
            
            if pdf_type == "text-based":
                logger.info("Processing as text-based PDF")
                return self._process_text_based_pdf(file_data, stream_info)
            else:
                logger.info("Processing as image-based PDF with advanced optimized OCR")
                return self._process_image_based_pdf_advanced(file_data, stream_info)
                
        except Exception as e:
            logger.error(f"Error in advanced optimized PDF conversion: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise

    def convert_stream(self, stream: BinaryIO, stream_info: Optional[StreamInfo] = None, **kwargs) -> DocumentConverterResult:
        """Convert stream to markdown"""
        try:
            # Read stream data
            file_data = stream.read()
            
            # Create a temporary file to process
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(file_data)
                temp_path = temp_file.name
            
            try:
                return self.convert(temp_path, stream_info)
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error in stream conversion: {e}")
            raise

    def _process_text_based_pdf(self, file_data: bytes, stream_info: StreamInfo) -> DocumentConverterResult:
        """Process text-based PDF using traditional methods"""
        return self.pdf_converter.convert(file_data, stream_info)

    def _process_image_based_pdf_advanced(self, file_data: bytes, stream_info: StreamInfo) -> DocumentConverterResult:
        """Process image-based PDF using advanced optimized techniques"""
        try:
            # Convert PDF pages to optimized images
            optimized_images = self._convert_pdf_to_optimized_images_advanced(file_data)
            logger.info(f"Converted PDF to {len(optimized_images)} optimized images")
            
            # Process each page with advanced optimized OCR
            all_text = []
            processing_methods = []
            quality_metrics = []
            
            for page_num, (image_data, quality_data) in enumerate(optimized_images):
                logger.info(f"Processing page {page_num + 1}/{len(optimized_images)}")
                
                # Check cache first
                cache_key = self._get_cache_key(image_data)
                cached_result = self._get_cached_result(cache_key)
                
                if cached_result:
                    page_text = cached_result
                    processing_method = "Cached Result"
                    logger.info(f"Page {page_num + 1}: Used cached result")
                else:
                    # Try traditional OCR first (fast)
                    traditional_text = self._extract_text_with_tesseract(image_data)
                    
                    if traditional_text and len(traditional_text.strip()) > 50:
                        # Traditional OCR found substantial text
                        page_text = traditional_text
                        processing_method = "Traditional OCR (Tesseract)"
                        logger.info(f"Page {page_num + 1}: Used traditional OCR")
                    else:
                        # Fall back to advanced vision OCR
                        page_text, method = self._process_image_with_advanced_vision_ocr(
                            image_data, page_num, quality_data
                        )
                        processing_method = method
                    
                    # Cache the result
                    if page_text:
                        self._save_cached_result(cache_key, page_text)
                
                all_text.append(page_text)
                processing_methods.append(processing_method)
                quality_metrics.append(quality_data)
                
                # Add page separator
                if page_num < len(optimized_images) - 1:
                    all_text.append(f"\n\n--- Page {page_num + 2} ---\n\n")
            
            # Combine all text
            combined_text = "".join(all_text)
            
            # Create metadata
            metadata = {
                "processing_methods": processing_methods,
                "total_pages": len(optimized_images),
                "quality_metrics": quality_metrics,
                "optimization_settings": {
                    "max_image_size": self.max_image_size,
                    "compression_quality": self.compression_quality,
                    "use_grayscale": self.use_grayscale,
                    "enable_parallel": self.enable_parallel,
                    "segment_size": self.segment_size,
                    "enable_caching": self.enable_caching,
                    "enable_smart_model_selection": self.enable_smart_model_selection,
                    "enable_quality_assessment": self.enable_quality_assessment
                }
            }
            
            return DocumentConverterResult(
                markdown=combined_text,

            )
            
        except Exception as e:
            logger.error(f"Error in advanced image-based PDF processing: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise

    def _convert_pdf_to_optimized_images_advanced(self, file_data: bytes) -> List[Tuple[bytes, Dict[str, Any]]]:
        """Convert PDF to optimized images using advanced techniques"""
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=file_data, filetype="pdf")
            optimized_images = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Convert to image with optimized resolution
                mat = fitz.Matrix(1.0, 1.0)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert to PIL Image for optimization
                img_data = pix.tobytes("png")
                pil_image = Image.open(io.BytesIO(img_data))
                
                # Assess image quality
                quality_data = {}
                if self.enable_quality_assessment:
                    quality_data = self.quality_assessor.assess_image_quality(pil_image)
                    logger.info(f"Page {page_num + 1} quality score: {quality_data.get('quality_score', 0):.1f}")
                
                # Apply advanced optimizations
                optimized_image = self._optimize_image_advanced(pil_image, quality_data)
                
                # Convert back to bytes
                img_buffer = io.BytesIO()
                optimized_image.save(img_buffer, format='JPEG', quality=self.compression_quality, optimize=True)
                optimized_images.append((img_buffer.getvalue(), quality_data))
                
                logger.info(f"Advanced optimized page {page_num + 1}: {len(img_data)} -> {len(optimized_images[-1][0])} bytes")
            
            doc.close()
            return optimized_images
            
        except Exception as e:
            logger.error(f"Error converting PDF to advanced optimized images: {e}")
            raise

    def _optimize_image_advanced(self, image: Image.Image, quality_data: Dict[str, Any]) -> Image.Image:
        """Apply advanced image optimizations for better OCR performance"""
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
            
            # Apply advanced image enhancements based on quality assessment
            if self.enable_quality_assessment:
                quality_score = quality_data.get('quality_score', 50)
                
                # Adjust enhancement based on quality
                if quality_score < 30:
                    # Low quality image - apply aggressive enhancement
                    image = self._apply_aggressive_enhancement(image)
                elif quality_score < 70:
                    # Medium quality image - apply moderate enhancement
                    image = self._apply_moderate_enhancement(image)
                else:
                    # High quality image - apply minimal enhancement
                    image = self._apply_minimal_enhancement(image)
            else:
                # Default enhancement
                image = self._apply_moderate_enhancement(image)
            
            return image
            
        except Exception as e:
            logger.error(f"Error in advanced image optimization: {e}")
            return image

    def _apply_aggressive_enhancement(self, image: Image.Image) -> Image.Image:
        """Apply aggressive image enhancement for low quality images"""
        try:
            # Increase contrast significantly
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            # Increase brightness
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.2)
            
            # Apply strong sharpening
            image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=200, threshold=2))
            
            # Apply noise reduction
            image = image.filter(ImageFilter.GaussianBlur(radius=0.3))
            
            logger.info("Applied aggressive image enhancement")
            return image
        except Exception as e:
            logger.error(f"Error in aggressive enhancement: {e}")
            return image

    def _apply_moderate_enhancement(self, image: Image.Image) -> Image.Image:
        """Apply moderate image enhancement for medium quality images"""
        try:
            # Increase contrast moderately
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # Apply moderate sharpening
            image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
            
            # Remove noise with slight blur
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            logger.info("Applied moderate image enhancement")
            return image
        except Exception as e:
            logger.error(f"Error in moderate enhancement: {e}")
            return image

    def _apply_minimal_enhancement(self, image: Image.Image) -> Image.Image:
        """Apply minimal image enhancement for high quality images"""
        try:
            # Slight contrast enhancement
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            # Very light sharpening
            image = image.filter(ImageFilter.UnsharpMask(radius=0.5, percent=120, threshold=5))
            
            logger.info("Applied minimal image enhancement")
            return image
        except Exception as e:
            logger.error(f"Error in minimal enhancement: {e}")
            return image

    def _process_image_with_advanced_vision_ocr(self, image_data: bytes, page_num: int, quality_data: Dict[str, Any]) -> Tuple[str, str]:
        """Process image with advanced vision OCR including smart model selection"""
        try:
            # Convert bytes to PIL Image
            pil_image = Image.open(io.BytesIO(image_data))
            
            # Check if image needs segmentation
            if max(pil_image.size) > self.segment_size:
                logger.info(f"Segmenting large image {pil_image.size} into smaller chunks")
                return self._process_image_with_segmentation_advanced(pil_image, page_num, quality_data)
            else:
                logger.info(f"Processing image directly (size: {pil_image.size})")
                return self._process_single_image_advanced(pil_image, page_num, quality_data)
                
        except Exception as e:
            logger.error(f"Error in advanced vision OCR: {e}")
            return "", "Error"

    def _process_image_with_segmentation_advanced(self, image: Image.Image, page_num: int, quality_data: Dict[str, Any]) -> Tuple[str, str]:
        """Process large image by breaking it into segments with advanced features"""
        try:
            # Create image segments
            segments = self._create_image_segments(image)
            logger.info(f"Created {len(segments)} image segments")
            
            if self.enable_parallel and len(segments) > 1:
                return self._process_segments_parallel_advanced(segments, page_num, quality_data)
            else:
                return self._process_segments_sequential_advanced(segments, page_num, quality_data)
                
        except Exception as e:
            logger.error(f"Error in advanced image segmentation: {e}")
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

    def _process_segments_parallel_advanced(self, segments: List[Image.Image], page_num: int, quality_data: Dict[str, Any]) -> Tuple[str, str]:
        """Process image segments in parallel with advanced features"""
        try:
            all_texts = []
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all segments for processing
                future_to_segment = {
                    executor.submit(self._process_single_segment_advanced, segment, i, quality_data): i 
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
            return combined_text, f"Advanced Vision OCR (Parallel, {len(segments)} segments)"
            
        except Exception as e:
            logger.error(f"Error in advanced parallel segment processing: {e}")
            return "", "Error"

    def _process_segments_sequential_advanced(self, segments: List[Image.Image], page_num: int, quality_data: Dict[str, Any]) -> Tuple[str, str]:
        """Process image segments sequentially with advanced features"""
        try:
            all_texts = []
            
            for i, segment in enumerate(segments):
                logger.info(f"Processing segment {i + 1}/{len(segments)}")
                segment_text = self._process_single_segment_advanced(segment, i, quality_data)
                all_texts.append((i, segment_text))
            
            # Combine results
            combined_text = self._combine_segment_texts(all_texts)
            return combined_text, f"Advanced Vision OCR (Sequential, {len(segments)} segments)"
            
        except Exception as e:
            logger.error(f"Error in advanced sequential segment processing: {e}")
            return "", "Error"

    def _process_single_segment_advanced(self, segment: Image.Image, segment_idx: int, quality_data: Dict[str, Any]) -> str:
        """Process a single image segment with advanced vision OCR"""
        try:
            # Convert to base64
            img_buffer = io.BytesIO()
            segment.save(img_buffer, format='JPEG', quality=self.compression_quality, optimize=True)
            img_data = img_buffer.getvalue()
            img_b64 = base64.b64encode(img_data).decode('utf-8')
            
            # Get smart model selection
            models_to_try = self._get_smart_model_selection()
            
            # Try vision models in order
            for model in models_to_try:
                try:
                    logger.info(f"Trying vision model {model} for segment {segment_idx + 1}")
                    
                    start_time = time.time()
                    
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
                    
                    # Adjust timeout based on image quality
                    timeout = self._get_adaptive_timeout(quality_data)
                    response = requests.post(url, json=payload, timeout=timeout)
                    
                    response_time = time.time() - start_time
                    
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
                                # Record success
                                if self.enable_smart_model_selection:
                                    self.model_tracker.record_success(model, response_time)
                                
                                logger.info(f"Successfully extracted text from segment {segment_idx + 1} with {model}")
                                return text
                    else:
                        # Record failure
                        if self.enable_smart_model_selection:
                            self.model_tracker.record_failure(model)
                    
                except Exception as e:
                    # Record failure
                    if self.enable_smart_model_selection:
                        self.model_tracker.record_failure(model)
                    
                    logger.warning(f"Model {model} failed for segment {segment_idx + 1}: {e}")
                    continue
            
            logger.warning(f"All vision models failed for segment {segment_idx + 1}")
            return ""
            
        except Exception as e:
            logger.error(f"Error processing segment {segment_idx + 1}: {e}")
            return ""

    def _process_single_image_advanced(self, image: Image.Image, page_num: int, quality_data: Dict[str, Any]) -> Tuple[str, str]:
        """Process a single image without segmentation with advanced features"""
        try:
            # Convert to base64
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='JPEG', quality=self.compression_quality, optimize=True)
            img_data = img_buffer.getvalue()
            img_b64 = base64.b64encode(img_data).decode('utf-8')
            
            # Get smart model selection
            models_to_try = self._get_smart_model_selection()
            
            # Try vision models in order
            for model in models_to_try:
                try:
                    logger.info(f"Trying vision model {model} for page {page_num + 1}")
                    
                    start_time = time.time()
                    
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
                    
                    # Adjust timeout based on image quality
                    timeout = self._get_adaptive_timeout(quality_data)
                    response = requests.post(url, json=payload, timeout=timeout)
                    
                    response_time = time.time() - start_time
                    
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
                                # Record success
                                if self.enable_smart_model_selection:
                                    self.model_tracker.record_success(model, response_time)
                                
                                logger.info(f"Successfully extracted text from page {page_num + 1} with {model}")
                                return text, f"Advanced Vision OCR ({model})"
                    else:
                        # Record failure
                        if self.enable_smart_model_selection:
                            self.model_tracker.record_failure(model)
                    
                except Exception as e:
                    # Record failure
                    if self.enable_smart_model_selection:
                        self.model_tracker.record_failure(model)
                    
                    logger.warning(f"Model {model} failed for page {page_num + 1}: {e}")
                    continue
            
            logger.warning(f"All vision models failed for page {page_num + 1}")
            return "", "Advanced Vision OCR failed"
            
        except Exception as e:
            logger.error(f"Error processing single image for page {page_num + 1}: {e}")
            return "", "Error"

    def _get_smart_model_selection(self) -> List[str]:
        """Get smart model selection based on performance history"""
        if self.enable_smart_model_selection and hasattr(self, 'model_tracker'):
            return self.model_tracker.get_model_rankings(self.fallback_vision_models)
        else:
            return self.fallback_vision_models

    def _get_adaptive_timeout(self, quality_data: Dict[str, Any]) -> int:
        """Get adaptive timeout based on image quality"""
        if not self.enable_quality_assessment:
            return 120
        
        quality_score = quality_data.get('quality_score', 50)
        
        # Adjust timeout based on quality score
        if quality_score < 30:
            return 180  # Low quality - longer timeout
        elif quality_score < 70:
            return 120  # Medium quality - standard timeout
        else:
            return 90   # High quality - shorter timeout

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

    def __del__(self):
        """Cleanup when object is destroyed"""
        try:
            if hasattr(self, 'model_tracker'):
                self.model_tracker.save_performance_data()
        except Exception as e:
            logger.warning(f"Error saving performance data: {e}")
