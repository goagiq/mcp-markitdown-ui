"""
Exception classes for MarkItDown.
"""


class FileConversionException(Exception):
    """Base exception for file conversion errors."""
    pass


class UnsupportedFormatException(FileConversionException):
    """Raised when a file format is not supported."""
    pass


class FailedConversionAttempt(FileConversionException):
    """Raised when a conversion attempt fails."""
    
    def __init__(self, converter=None, exc_info=None):
        self.converter = converter
        self.exc_info = exc_info
        super().__init__(f"Conversion failed with converter: {converter}")

