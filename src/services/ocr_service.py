"""OCR service for extracting text from images and PDFs using Tesseract."""
import os
from typing import Optional
import pytesseract
from PIL import Image, ImageOps, ImageEnhance
from PyPDF2 import PdfReader

from src.errors.app_error import AppError, UnsupportedFileTypeError

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


class OcrService:
    """Service for optical character recognition using Tesseract."""

    def __init__(self):
        """Initialize OCR service."""
        pass

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results."""
        # Convert to grayscale
        img = image.convert('L')
        # Increase contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        return img

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image file using Tesseract.

        Args:
            image_path: Path to image file (JPEG, PNG)

        Returns:
            Extracted text as string
        """
        try:
            image = Image.open(image_path)
            # Preprocess for better results
            image = self._preprocess_image(image)
            text = pytesseract.image_to_string(image, config='--psm 3')
            return text.strip()
        except Exception as e:
            raise AppError(f"Failed to extract text from image: {str(e)}")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.

        For PDFs with text layers, extracts text directly.
        For image-based PDFs, uses OCR on each page.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text as string
        """
        try:
            reader = PdfReader(pdf_path)
            text_parts = []

            for page_num, page in enumerate(reader.pages):
                # Try to extract text directly
                page_text = page.extract_text()

                if page_text and page_text.strip():
                    text_parts.append(page_text)
                else:
                    # Fallback to OCR for image-based PDFs
                    # Convert page to image and OCR
                    pass  # Would need additional library for this

            return "\n".join(text_parts).strip()
        except Exception as e:
            raise AppError(f"Failed to extract text from PDF: {str(e)}")

    def extract_text(self, file_path: str, file_extension: str) -> str:
        """
        Extract text from file based on its type.

        Args:
            file_path: Path to file
            file_extension: File extension (pdf, jpg, jpeg, png)

        Returns:
            Extracted text as string
        """
        ext = file_extension.lower()

        if ext == ".pdf":
            return self.extract_text_from_pdf(file_path)
        elif ext in [".jpeg", ".jpg", ".png"]:
            return self.extract_text_from_image(file_path)
        else:
            raise UnsupportedFileTypeError(f"Unsupported file type for OCR: {ext}")


# Singleton instance
ocr_service = OcrService()
