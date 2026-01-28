"""
Pydantic Models for Request/Response

This module contains all the request and response models for the API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for chat endpoint"""
    query: str = Field(..., description="User query text")
    conversation_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Previous conversation messages"
    )


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    status: str = Field(..., description="Response status")
    response: str = Field(..., description="Agent response text")
    agent: str = Field(..., description="Name of the agent that handled the query")
    result_image: Optional[str] = Field(None, description="Path to result image if any")


class UploadResponse(BaseModel):
    """Response model for image upload endpoint"""
    status: str
    response: str
    agent: str
    result_image: Optional[str] = None


class ValidationRequest(BaseModel):
    """Request model for validation endpoint"""
    validation_result: str = Field(..., description="Yes/No validation result")
    comments: Optional[str] = Field(None, description="Optional validation comments")


class ValidationResponse(BaseModel):
    """Response model for validation endpoint"""
    status: str
    message: str
    response: str
    comments: Optional[str] = None


class SpeechRequest(BaseModel):
    """Request model for text-to-speech"""
    text: str = Field(..., description="Text to convert to speech")
    voice_id: str = Field(
        default="EXAMPLE_VOICE_ID",
        description="ElevenLabs voice ID"
    )


class TranscriptionResponse(BaseModel):
    """Response model for speech-to-text"""
    transcript: str = Field(..., description="Transcribed text")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(default="healthy")
    version: str = Field(default="2.0")


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = Field(default="error")
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Detailed error information")
    agent: str = Field(default="System")
