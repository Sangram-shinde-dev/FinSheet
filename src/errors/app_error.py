"""Error handling module."""

from typing import Any


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, status_code: int = 500, details: dict[str, Any] | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class UnauthorizedError(AppError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message, status_code=401)


class ValidationError(AppError):
    """Raised when request validation fails."""

    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class FileTooLargeError(AppError):
    """Raised when uploaded file exceeds size limit."""

    def __init__(self, message: str = "File too large"):
        super().__init__(message, status_code=413)


class UnsupportedFileTypeError(AppError):
    """Raised when file type is not supported."""

    def __init__(self, message: str = "Unsupported file type"):
        super().__init__(message, status_code=400)
