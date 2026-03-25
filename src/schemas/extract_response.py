"""Pydantic models for extraction response."""
from typing import List, Any, Optional
from pydantic import BaseModel, Field


class ExtractionRow(BaseModel):
    """Single row from extraction."""
    pass


class ExtractResponse(BaseModel):
    """Response model for successful extraction."""
    data: List[Any] = Field(
        description="Extracted data as list of rows"
    )
    row_count: int = Field(
        description="Number of extracted rows"
    )
    format: Optional[str] = Field(
        default=None,
        description="Export format if applicable"
    )


class ExtractError(BaseModel):
    """Error response model."""
    error: str = Field(description="Error message")
