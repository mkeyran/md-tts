"""
Pydantic models for request/response schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ConvertRequest(BaseModel):
    """Request model for TTS conversion."""

    markdown_text: str = Field(
        ..., min_length=1, description="Markdown text to convert"
    )
    title: str | None = Field(None, description="Optional title for the conversion")
    voice_id: str | None = Field(None, description="Voice model ID to use for conversion")


class ConvertResponse(BaseModel):
    """Response model for TTS conversion."""

    conversion_id: str = Field(..., description="Unique ID for this conversion")
    status: str = Field(..., description="Conversion status")
    message: str = Field(..., description="Status message")
    download_url: str | None = Field(None, description="URL to download MP3 file")


class HistoryItem(BaseModel):
    """Model for conversion history item."""

    id: str = Field(..., description="Conversion ID")
    title: str | None = Field(None, description="Conversion title")
    text_preview: str = Field(..., description="Preview of converted text")
    created_at: datetime = Field(..., description="Creation timestamp")
    status: str = Field(..., description="Conversion status")
    file_size: int | None = Field(None, description="MP3 file size in bytes")
    download_url: str | None = Field(None, description="Download URL if available")


class HistoryResponse(BaseModel):
    """Response model for conversion history."""

    items: list[HistoryItem] = Field(
        ..., description="List of conversion history items"
    )


class VoiceModelInfo(BaseModel):
    """Voice model information."""
    
    id: str = Field(..., description="Voice model ID")
    language: str = Field(..., description="Language name")
    language_code: str = Field(..., description="Language code")
    language_name: str = Field(..., description="Native language name")
    speaker: str = Field(..., description="Speaker name")
    quality: str = Field(..., description="Model quality (low, medium, high)")
    gender: Optional[str] = Field(None, description="Voice gender")
    description: Optional[str] = Field(None, description="Voice description")


class VoicesResponse(BaseModel):
    """Response model for available voices."""
    
    voices: list[VoiceModelInfo] = Field(..., description="List of available voice models")
    default_voice: str = Field(..., description="Default voice model ID")
