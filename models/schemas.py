"""
Pydantic models for request/response schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ConvertRequest(BaseModel):
    """Request model for TTS conversion."""
    markdown_text: str = Field(..., min_length=1, description="Markdown text to convert")
    title: Optional[str] = Field(None, description="Optional title for the conversion")


class ConvertResponse(BaseModel):
    """Response model for TTS conversion."""
    conversion_id: str = Field(..., description="Unique ID for this conversion")
    status: str = Field(..., description="Conversion status")
    message: str = Field(..., description="Status message")
    download_url: Optional[str] = Field(None, description="URL to download MP3 file")


class HistoryItem(BaseModel):
    """Model for conversion history item."""
    id: str = Field(..., description="Conversion ID")
    title: Optional[str] = Field(None, description="Conversion title")
    text_preview: str = Field(..., description="Preview of converted text")
    created_at: datetime = Field(..., description="Creation timestamp")
    status: str = Field(..., description="Conversion status")
    file_size: Optional[int] = Field(None, description="MP3 file size in bytes")
    download_url: Optional[str] = Field(None, description="Download URL if available")


class HistoryResponse(BaseModel):
    """Response model for conversion history."""
    items: list[HistoryItem] = Field(..., description="List of conversion history items")