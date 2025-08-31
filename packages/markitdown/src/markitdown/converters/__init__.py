"""
MarkItDown converters package
"""

# Import only the converters that actually exist
from ._advanced_optimized_pdf_ocr_converter import AdvancedOptimizedPdfOcrConverter
from ._vision_ocr_converter import VisionOcrConverter
from ._pdf_converter import PdfConverter

# Create placeholder classes for missing converters
class PlaceholderConverter:
    """Placeholder converter for missing implementations."""
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("This converter is not yet implemented")

# Create placeholder instances
OptimizedPdfOcrConverter = PlaceholderConverter
PlainTextConverter = PlaceholderConverter
HtmlConverter = PlaceholderConverter
RssConverter = PlaceholderConverter
WikipediaConverter = PlaceholderConverter
YouTubeConverter = PlaceholderConverter
IpynbConverter = PlaceholderConverter
BingSerpConverter = PlaceholderConverter
DocxConverter = PlaceholderConverter
XlsxConverter = PlaceholderConverter
PptxConverter = PlaceholderConverter
ImageConverter = PlaceholderConverter
AudioConverter = PlaceholderConverter
OutlookMsgConverter = PlaceholderConverter
ZipConverter = PlaceholderConverter
EpubConverter = PlaceholderConverter
DocumentIntelligenceConverter = PlaceholderConverter
CsvConverter = PlaceholderConverter
EnhancedPdfConverter = PlaceholderConverter

# Alias for XLS files
XlsConverter = XlsxConverter

__all__ = [
    "PdfConverter",
    "VisionOcrConverter",
    "OptimizedPdfOcrConverter",
    "AdvancedOptimizedPdfOcrConverter",
    "PlainTextConverter",
    "HtmlConverter",
    "RssConverter",
    "WikipediaConverter",
    "YouTubeConverter",
    "IpynbConverter",
    "BingSerpConverter",
    "DocxConverter",
    "XlsxConverter",
    "XlsConverter",
    "PptxConverter",
    "ImageConverter",
    "AudioConverter",
    "OutlookMsgConverter",
    "ZipConverter",
    "EpubConverter",
    "DocumentIntelligenceConverter",
    "CsvConverter",
    "EnhancedPdfConverter"
]
