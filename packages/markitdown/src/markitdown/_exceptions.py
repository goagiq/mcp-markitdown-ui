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
    pass

