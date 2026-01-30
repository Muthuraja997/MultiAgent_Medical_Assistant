"""
Pydantic Models for Request/Response

This module contains all the request and response models for the API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


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


# ==================== DATABASE MODELS ====================

class UserType(str, Enum):
    """User type enum"""
    USER = "USER"
    DOCTOR = "DOCTOR"


class AppointmentStatus(str, Enum):
    """Appointment status enum"""
    SCHEDULED = "SCHEDULED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# ==================== AUTHENTICATION MODELS ====================

class LoginRequest(BaseModel):
    """Model for login request"""
    user_id: str = Field(..., description="User ID or Doctor ID for login")
    password: str = Field(..., description="User password")
    user_type: UserType = Field(..., description="Login as USER or DOCTOR")


class LoginResponse(BaseModel):
    """Model for login response"""
    success: bool
    message: str
    user_id: str
    user_name: str
    user_type: UserType
    token: Optional[str] = None


class RegisterRequest(BaseModel):
    """Model for registration request"""
    user_id: str = Field(..., description="Unique user/doctor ID (e.g., user_001, doc_001)")
    name: str = Field(..., description="Full name")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")
    user_type: UserType = Field(..., description="Register as USER or DOCTOR")
    email: Optional[str] = Field(None, description="Email address (optional)")
    phone: Optional[str] = Field(None, description="Phone number (optional)")


class RegisterResponse(BaseModel):
    """Model for registration response"""
    success: bool
    message: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    user_type: Optional[UserType] = None


# ==================== USER MODELS ====================

class UserCreate(BaseModel):
    """Model for creating a new user"""
    user_id: str = Field(..., description="Unique user identifier")
    user_name: str = Field(..., description="User's full name")
    user_type: UserType = Field(..., description="Type of user (USER or DOCTOR)")
    appointment_status: AppointmentStatus = Field(AppointmentStatus.SCHEDULED, description="Current appointment status")
    doctor_id: Optional[str] = Field(None, description="Assigned doctor ID")
    password: str = Field(..., description="User password for login")


class UserUpdate(BaseModel):
    """Model for updating user information"""
    user_name: Optional[str] = None
    user_type: Optional[UserType] = None
    appointment_status: Optional[AppointmentStatus] = None
    doctor_id: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    """Model for user response"""
    user_id: str
    user_name: str
    user_type: str
    appointment_status: str
    doctor_id: Optional[str] = None
    created_at: Optional[datetime] = None


# ==================== DOCTOR MODELS ====================

class DoctorCreate(BaseModel):
    """Model for creating a new doctor"""
    doctor_id: str = Field(..., description="Unique doctor identifier")
    doc_name: str = Field(..., description="Doctor's full name")
    available_status: bool = Field(default=True, description="Doctor availability")
    password: str = Field(..., description="Doctor password for login")


class DoctorUpdate(BaseModel):
    """Model for updating doctor information"""
    doc_name: Optional[str] = None
    available_status: Optional[bool] = None
    password: Optional[str] = None


class DoctorResponse(BaseModel):
    """Model for doctor response"""
    doctor_id: str
    doc_name: str
    available_status: bool
    created_at: Optional[datetime] = None


# ==================== MEETING MODELS ====================

class MeetingCreate(BaseModel):
    """Model for creating a meeting"""
    doctor_id: str = Field(..., description="Doctor ID")
    meet_link: str = Field(..., description="Video meeting link")
    start_meet_time: str = Field(..., description="Meeting start time (HH:MM)")
    end_meet_time: str = Field(..., description="Meeting end time (HH:MM)")


class MeetingUpdate(BaseModel):
    """Model for updating meeting"""
    meet_link: Optional[str] = None
    start_meet_time: Optional[str] = None
    end_meet_time: Optional[str] = None


class MeetingResponse(BaseModel):
    """Model for meeting response"""
    meeting_id: str
    doctor_id: str
    meet_link: str
    start_meet_time: str
    end_meet_time: str
    created_at: Optional[datetime] = None


# ==================== APPOINTMENT REQUEST MODELS ====================

class AppointmentRequestStatus(str, Enum):
    """Appointment request status"""
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class AppointmentRequestCreate(BaseModel):
    """Model for creating appointment request"""
    doctor_id: str = Field(..., description="Doctor ID to request appointment with")
    reason: Optional[str] = Field(None, description="Reason for appointment")
    preferred_date: Optional[str] = Field(None, description="Preferred date (YYYY-MM-DD)")
    preferred_time: Optional[str] = Field(None, description="Preferred time (HH:MM)")


class AppointmentRequestResponse(BaseModel):
    """Model for appointment request response"""
    request_id: str
    user_id: str
    user_name: str
    doctor_id: str
    doctor_name: Optional[str] = None
    reason: Optional[str] = None
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    status: str
    meet_link: Optional[str] = None
    meeting_id: Optional[str] = None
    created_at: Optional[datetime] = None


class AppointmentRequestUpdate(BaseModel):
    """Model for updating appointment request"""
    status: AppointmentRequestStatus = Field(..., description="New status (ACCEPTED/REJECTED)")
    meet_link: Optional[str] = Field(None, description="Video meeting link if accepted")


# ==================== STATISTICS MODELS ====================

class StatisticsResponse(BaseModel):
    """Model for admin statistics"""
    total_users: int
    total_doctors: int
    available_doctors: int
    total_meetings: int
    total_appointment_requests: int

