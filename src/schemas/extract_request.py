"""Pydantic models for extraction request validation."""
from typing import Optional
from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    """Request model for extraction endpoint."""
    pass


class ExtractQueryParams(BaseModel):
    """Query parameters for extract endpoint."""
    format: Optional[str] = Field(
        default=None,
        pattern="^(csv|xlsx)$",
        description="Export format: csv or xlsx"
    )
