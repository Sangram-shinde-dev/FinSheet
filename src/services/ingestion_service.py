"""Ingestion service for handling file uploads."""
import os
import tempfile
from typing import Optional
from fastapi import UploadFile

from src.config.settings import settings
from src.errors.app_error import UnsupportedFileTypeError, FileTooLargeError


ALLOWED_EXTENSIONS = {".pdf", ".jpeg", ".jpg", ".png"}


def validate_file_type(filename: str) -> str:
    """Validate file extension and return normalized extension."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsupportedFileTypeError()
    return ext


async def handle_upload(file: UploadFile) -> tuple[str, str]:
    """
    Handle file upload: validate and save to temp location.

    Returns:
        tuple: (temp_file_path, file_extension)
    """
    # Validate file type
    ext = validate_file_type(file.filename)

    # Read and validate size
    content = await file.read()
    if len(content) > settings.max_file_size_mb * 1024 * 1024:
        raise FileTooLargeError()

    # Save to temp file
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"extraction_{os.urandom(8).hex()}{ext}")

    with open(temp_path, "wb") as f:
        f.write(content)

    return temp_path, ext


def cleanup_temp_file(file_path: str) -> None:
    """Remove temporary file after processing."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except OSError:
        pass  # Best effort cleanup
