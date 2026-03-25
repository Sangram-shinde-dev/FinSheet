"""Extraction service for LLM-based data extraction."""
import base64
import json
from typing import Any
import pandas as pd
import ollama

from src.errors.app_error import AppError

# Ollama model name
OLLAMA_MODEL = "qwen3.5:397b-cloud"
OLLAMA_HOST = "http://localhost:11434"


class ExtractionService:
    """Service for extracting structured data from text using LLM."""

    def __init__(self):
        """Initialize extraction service."""
        pass

    def _build_prompt(self, text: str) -> str:
        """Build extraction prompt for the LLM."""
        return f"""You are a data extraction specialist. Extract structured tabular data from the following text.
Return ONLY a valid JSON array (list of objects), no markdown, no explanation, no code blocks.

Extract all meaningful data rows. Each object should have consistent keys based on the content.
If no structured data is found, return an empty array [].

Text:
{text}

JSON:"""

    def _build_image_prompt(self) -> str:
        """Build prompt for image-based extraction."""
        return """You are a data extraction specialist. Look at this image and extract all structured data you can see.
Return ONLY a valid JSON array (list of objects), no markdown, no explanation, no code blocks.

Extract all meaningful data rows including but not limited to: tables, receipts, invoices, forms, lists.
Each object should have consistent keys based on the content.
If no structured data is found, return an empty array [].

JSON:"""

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for LLM vision."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _call_llm(self, text: str) -> list[dict[str, Any]]:
        """Call Ollama LLM to extract structured data from text."""
        prompt = self._build_prompt(text)

        try:
            response = ollama.generate(
                model=OLLAMA_MODEL,
                prompt=prompt,
                format="json",
                options={"temperature": 0.1}
            )

            # Parse the response
            raw_response = response.response.strip()

            if not raw_response:
                raise AppError("Model not working: Empty response from model", status_code=503)

            # Handle potential markdown code blocks
            if raw_response.startswith("```"):
                raw_response = raw_response.split("```")[1]
                if raw_response.startswith("json"):
                    raw_response = raw_response[4:]
                raw_response = raw_response.strip()

            if not raw_response:
                raise AppError("Model not working: Empty response after parsing", status_code=503)

            return json.loads(raw_response)

        except Exception as e:
            raise AppError(f"Model not working: {str(e)}", status_code=503)

    def _call_llm_with_image(self, image_path: str) -> list[dict[str, Any]]:
        """Call Ollama LLM to extract structured data directly from image."""
        prompt = self._build_image_prompt()
        image_base64 = self._encode_image(image_path)

        try:
            response = ollama.generate(
                model=OLLAMA_MODEL,
                prompt=prompt,
                images=[image_base64],
                format="json",
                options={"temperature": 0.1}
            )

            # Parse the response
            raw_response = response.response.strip()

            if not raw_response:
                raise AppError("Model not working: Empty response from model", status_code=503)

            # Handle potential markdown code blocks
            if raw_response.startswith("```"):
                raw_response = raw_response.split("```")[1]
                if raw_response.startswith("json"):
                    raw_response = raw_response[4:]
                raw_response = raw_response.strip()

            if not raw_response:
                raise AppError("Model not working: Empty response after parsing", status_code=503)

            return json.loads(raw_response)

        except Exception as e:
            raise AppError(f"Model not working: {str(e)}", status_code=503)

    def extract_to_dataframe(self, text: str, image_path: str = None) -> pd.DataFrame:
        """
        Extract structured data from text using LLM.
        If text is empty and image_path is provided, try LLM vision fallback.

        Args:
            text: Raw text from OCR
            image_path: Optional path to image file for fallback

        Returns:
            DataFrame with extracted data
        """
        # If text is empty and we have an image, try LLM with image
        if (not text or not text.strip()) and image_path:
            try:
                extracted_data = self._call_llm_with_image(image_path)
                if extracted_data:
                    return pd.DataFrame(extracted_data)
            except AppError:
                pass  # Fall through to return empty DataFrame
            return pd.DataFrame()

        if not text or not text.strip():
            return pd.DataFrame()

        # Call LLM to extract data
        extracted_data = self._call_llm(text)

        if not extracted_data:
            return pd.DataFrame()

        # Convert to DataFrame
        return pd.DataFrame(extracted_data)

    def extract_to_json(self, text: str) -> list[dict[str, Any]]:
        """
        Extract structured data from text and return as JSON.

        Args:
            text: Raw text from OCR

        Returns:
            List of dictionaries with extracted data
        """
        df = self.extract_to_dataframe(text)
        return df.to_dict(orient="records")

    def validate_schema(self, data: pd.DataFrame) -> bool:
        """
        Validate extracted data matches expected schema.

        Args:
            data: DataFrame to validate

        Returns:
            True if valid
        """
        required_columns = ["id", "value", "description"]
        return all(col in data.columns for col in required_columns)


# Singleton instance
extraction_service = ExtractionService()
