"""
FastAPI Backend for Multi-Agent Medical Assistant

Main application file with all API endpoints.
"""

import os
import sys
import uuid
import json
import glob
import threading
import time
from typing import Optional, List, Dict, Any

# Add current directory to path to import from backend
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response, Cookie, Request, Query
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from models.schemas import (
    QueryRequest, ChatResponse, UploadResponse,
    ValidationRequest, ValidationResponse,
    SpeechRequest, TranscriptionResponse,
    HealthResponse, ErrorResponse,
    # Database models
    LoginRequest, LoginResponse,
    RegisterRequest, RegisterResponse,
    UserCreate, UserUpdate, UserResponse,
    DoctorCreate, DoctorUpdate, DoctorResponse,
    MeetingCreate, MeetingUpdate, MeetingResponse,
    AppointmentRequestCreate, AppointmentRequestResponse, AppointmentRequestUpdate,
    StatisticsResponse,
    LiveKitVoiceTokenRequest,
    LiveKitVoiceTokenResponse,
    DirectMessageSend,
    DirectMessageItem,
    DirectMessageListResponse,
)
from services.agent_service import AgentService
from services.image_service import ImageService
from services.speech_service import SpeechService
from services.database_service import db_manager
from core.config import Config
from voice_agent.constants import MEDICAL_VOICE_AGENT_NAME

# Load configuration
config = Config()

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Medical Assistant API",
    description="Backend API for Multi-Agent Medical Chatbot with specialized AI agents",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS — localhost + optional extra origins (comma-separated) + ngrok tunnels via regex
_cors_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "https://localhost:3000",
    "https://127.0.0.1:3000",
    "https://unhumidifying-relational-drema.ngrok-free.dev",
]
for _part in (os.getenv("CORS_EXTRA_ORIGINS") or "").split(","):
    _u = _part.strip()
    if _u and _u not in _cors_origins:
        _cors_origins.append(_u)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    # Browser hits ngrok / other tunnels with varying subdomains; OR with allow_origins above
    allow_origin_regex=r"https://([a-z0-9-]+\.)*ngrok-free\.(dev|app)$|https://([a-z0-9-]+\.)*ngrok(\.io|\.app)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- User / doctor direct chat (registered early so it is never shadowed) ---


def _assert_x_user_id_matches(claimed_id: str, request: Request) -> None:
    """If client sends x-user-id, it must match the claimed user/doctor id (light auth hook)."""
    header_uid = (request.headers.get("x-user-id") or "").strip()
    if header_uid and header_uid != (claimed_id or "").strip():
        raise HTTPException(
            status_code=403,
            detail="When x-user-id is sent, it must match sender_id or user_id for this request.",
        )


@app.post("/api/messages", response_model=DirectMessageItem, tags=["Messages"])
async def send_direct_message_early(payload: DirectMessageSend, request: Request):
    """Send a direct message (canonical path: /api/messages)."""
    _assert_x_user_id_matches(payload.sender_id, request)
    try:
        row = await db_manager.send_direct_message(
            payload.sender_id, payload.receiver_id, payload.message
        )
        return DirectMessageItem(**row)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/messages", response_model=DirectMessageListResponse, tags=["Messages"])
async def list_direct_messages_early(
    request: Request,
    user_id: str = Query(..., description="Viewer login id (user_id or doctor_id)"),
    peer_id: str = Query(..., description="Other party login id (user_id or doctor_id)"),
    limit: int = Query(200, ge=1, le=500),
):
    """List thread (canonical path: /api/messages)."""
    _assert_x_user_id_matches(user_id, request)
    try:
        rows = await db_manager.list_direct_messages(user_id, peer_id, limit=limit)
        return DirectMessageListResponse(messages=[DirectMessageItem(**r) for r in rows])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/direct-messages", response_model=DirectMessageItem, tags=["Messages"])
async def send_direct_message_alias(payload: DirectMessageSend, request: Request):
    """Alias of POST /api/messages."""
    _assert_x_user_id_matches(payload.sender_id, request)
    try:
        row = await db_manager.send_direct_message(
            payload.sender_id, payload.receiver_id, payload.message
        )
        return DirectMessageItem(**row)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/direct-messages", response_model=DirectMessageListResponse, tags=["Messages"])
async def list_direct_messages_alias(
    request: Request,
    user_id: str = Query(..., description="Viewer login id (user_id or doctor_id)"),
    peer_id: str = Query(..., description="Other party login id (user_id or doctor_id)"),
    limit: int = Query(200, ge=1, le=500),
):
    """Alias of GET /api/messages."""
    _assert_x_user_id_matches(user_id, request)
    try:
        rows = await db_manager.list_direct_messages(user_id, peer_id, limit=limit)
        return DirectMessageListResponse(messages=[DirectMessageItem(**r) for r in rows])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Set up directories (in common folder)
UPLOAD_FOLDER = "../common/uploads/backend"
SKIN_LESION_OUTPUT = "../common/uploads/skin_lesion_output"
SPEECH_DIR = "../common/uploads/speech"

# Create directories if they don't exist
for directory in [UPLOAD_FOLDER, SKIN_LESION_OUTPUT, SPEECH_DIR]:
    os.makedirs(directory, exist_ok=True)

# Mount static files (for serving uploaded images, etc.)
app.mount("/uploads", StaticFiles(directory="../common/uploads"), name="uploads")

# Initialize services
agent_service = AgentService()
image_service = ImageService()
speech_service = SpeechService()


def cleanup_old_audio():
    """Deletes all .mp3 files in the uploads/speech folder every 5 minutes."""
    while True:
        try:
            files = glob.glob(f"{SPEECH_DIR}/*.mp3")
            for file in files:
                os.remove(file)
            print("Cleaned up old speech files.")
        except Exception as e:
            print(f"Error during cleanup: {e}")
        time.sleep(300)  # Runs every 5 minutes


# Start background cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_audio, daemon=True)
cleanup_thread.start()


# ==================== DATABASE STARTUP/SHUTDOWN ====================

@app.on_event("startup")
async def startup_db():
    """Connect to MongoDB on startup"""
    await db_manager.connect_async()
    print("✅ Database connection established")


@app.on_event("shutdown")
async def shutdown_db():
    """Disconnect from MongoDB on shutdown"""
    await db_manager.close_async()
    print("❌ Database connection closed")


# ==================== API ENDPOINTS ====================

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Multi-Agent Medical Assistant API",
        "version": "2.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def health_check():
    """
    Health check endpoint for monitoring and Docker health checks.
    """
    return HealthResponse(status="healthy", version="2.0.0")


@app.post(
    "/api/voice/livekit-token",
    response_model=LiveKitVoiceTokenResponse,
    tags=["Voice"],
)
def create_livekit_voice_token(
    body: LiveKitVoiceTokenRequest,
    request: Request,
):
    """
    Mint a LiveKit participant JWT that dispatches the medical voice agent to the room.
    Requires LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET. Run the voice worker separately.
    """
    try:
        from livekit import api as livekit_api
    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail="livekit-api is not installed. Install backend requirements including livekit packages.",
        ) from e

    lk_url = os.getenv("LIVEKIT_URL")
    if not lk_url:
        raise HTTPException(
            status_code=503,
            detail="LIVEKIT_URL is not configured.",
        )

    room_name = (body.room_name or "").strip() or f"voice-medical-{uuid.uuid4().hex[:16]}"
    user_id = request.headers.get("x-user-id") or ""
    identity = f"user-{user_id}" if user_id else f"user-{uuid.uuid4().hex[:12]}"
    display = "Medical app user"

    metadata = json.dumps({"source": "multi_agent_medical_assistant"})
    room_config = livekit_api.RoomConfiguration(
        agents=[
            livekit_api.RoomAgentDispatch(
                agent_name=MEDICAL_VOICE_AGENT_NAME,
                metadata=metadata,
            )
        ],
    )

    token = (
        livekit_api.AccessToken()
        .with_identity(identity)
        .with_name(display)
        .with_grants(
            livekit_api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )
        )
        .with_room_config(room_config)
        .to_jwt()
    )

    return LiveKitVoiceTokenResponse(
        url=lk_url,
        token=token,
        room_name=room_name,
        agent_name=MEDICAL_VOICE_AGENT_NAME,
    )


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
def chat(
    request: QueryRequest,
    response: Response,
    session_id: Optional[str] = Cookie(None)
):
    """
    Process user text query through the multi-agent system.
    
    - **query**: User's text input
    - **conversation_history**: Optional list of previous messages
    
    Returns the agent's response with metadata.
    """
    # Generate session ID for cookie if it doesn't exist
    if not session_id:
        session_id = str(uuid.uuid4())
    
    try:
        print(f"[DEBUG] Chat request received: {request.query}")
        
        # Process query through agent service
        result = agent_service.process_text_query(
            query=request.query,
            conversation_history=request.conversation_history
        )
        
        # Set session cookie
        response.set_cookie(key="session_id", value=session_id)
        
        print(f"[DEBUG] Query processed successfully")
        
        return ChatResponse(
            status=result["status"],
            response=result["response"],
            agent=result["agent"],
            result_image=result.get("result_image")
        )
        
    except Exception as e:
        import traceback
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"[ERROR] Chat endpoint error: {error_msg}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/api/upload", response_model=UploadResponse, tags=["Image"])
async def upload_image(
    response: Response,
    image: UploadFile = File(...),
    text: str = Form(""),
    session_id: Optional[str] = Cookie(None)
):
    """
    Process medical image uploads with optional text input.
    
    - **image**: Image file (PNG, JPG, JPEG)
    - **text**: Optional text description/query
    
    Returns analysis results from the appropriate medical imaging agent.
    """
    # Validate file type
    if not image_service.allowed_file(image.filename):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed formats: PNG, JPG, JPEG"
        )
    
    # Check file size before saving
    file_content = await image.read()
    is_valid, error_message = image_service.validate_file_size(
        file_content,
        config.api.max_image_upload_size
    )
    
    if not is_valid:
        raise HTTPException(status_code=413, detail=error_message)
    
    # Generate session ID for cookie if it doesn't exist
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Save file securely
    file_path = image_service.save_uploaded_image(file_content, image.filename)
    
    try:
        # Process image through agent service
        result = agent_service.process_image_query(
            image_path=file_path,
            text=text
        )
        
        # Set session cookie
        response.set_cookie(key="session_id", value=session_id)
        
        # Remove temporary file after processing
        image_service.delete_file(file_path)
        
        return UploadResponse(
            status=result["status"],
            response=result["response"],
            agent=result["agent"],
            result_image=result.get("result_image")
        )
        
    except Exception as e:
        import traceback

        image_service.delete_file(file_path)
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"[ERROR] Upload / image processing: {error_msg}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/api/validate", response_model=ValidationResponse, tags=["Validation"])
def validate_medical_output(
    request: ValidationRequest,
    response: Response,
    session_id: Optional[str] = Cookie(None)
):
    """
    Handle human validation for medical AI outputs.
    
    - **validation_result**: Yes/No validation
    - **comments**: Optional validation comments
    
    Returns validation confirmation or re-routing for review.
    """
    # Generate session ID for cookie if it doesn't exist
    if not session_id:
        session_id = str(uuid.uuid4())

    try:
        # Set session cookie
        response.set_cookie(key="session_id", value=session_id)
        
        # Process validation through agent service
        result = agent_service.process_validation(
            validation_result=request.validation_result,
            comments=request.comments
        )
        
        return ValidationResponse(
            status=result["status"],
            message=result["message"],
            response=result["response"],
            comments=result.get("comments")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/transcribe", response_model=TranscriptionResponse, tags=["Speech"])
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe speech to text using ElevenLabs API.
    
    - **audio**: Audio file (WebM, MP3, WAV)
    
    Returns transcribed text.
    """
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No audio file selected")
    
    try:
        # Read audio content
        audio_content = await audio.read()
        
        # Transcribe using speech service
        transcript = await speech_service.transcribe_audio(
            audio_content=audio_content,
            filename=audio.filename
        )
        
        return TranscriptionResponse(transcript=transcript)
        
    except Exception as e:
        print(f"Transcription error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-speech", tags=["Speech"])
async def generate_speech(request: SpeechRequest):
    """
    Generate speech from text using ElevenLabs API.
    
    - **text**: Text to convert to speech
    - **voice_id**: ElevenLabs voice ID
    
    Returns audio file (MP3).
    """
    try:
        # Generate speech using speech service
        audio_path = speech_service.generate_speech(
            text=request.text,
            voice_id=request.voice_id
        )
        
        # Return the generated audio file
        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename="generated_speech.mp3"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/hospitals/nearby", tags=["Hospitals"])
async def find_nearby_hospitals(
    lat: float,
    lon: float,
    radius: int = 5000
):
    """
    Find nearby hospitals using OpenStreetMap Overpass API.
    
    - **lat**: Latitude of user location
    - **lon**: Longitude of user location
    - **radius**: Search radius in meters (default: 5000m = 5km)
    
    Returns list of nearby hospitals with their details.
    """
    try:
        import requests
        from math import radians, sin, cos, sqrt, atan2
        
        print(f"[HOSPITAL LOCATOR] Searching for hospitals near ({lat}, {lon}) within {radius}m")
        
        # Query Overpass API for hospitals - using simpler query
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Simpler query that's more reliable
        overpass_query = f"""[out:json][timeout:15];
(
  node["amenity"="hospital"](around:{radius},{lat},{lon});
  way["amenity"="hospital"](around:{radius},{lat},{lon});
  relation["amenity"="hospital"](around:{radius},{lat},{lon});
  node["amenity"="clinic"](around:{radius},{lat},{lon});
  node["healthcare"="hospital"](around:{radius},{lat},{lon});
);
out center tags;"""
        
        print(f"[HOSPITAL LOCATOR] Sending request to Overpass API...")
        
        response = requests.post(
            overpass_url,
            data={"data": overpass_query},
            timeout=15,
            headers={'User-Agent': 'MedicalAssistant/1.0'}
        )
        
        print(f"[HOSPITAL LOCATOR] Response status: {response.status_code}")
        
        response.raise_for_status()
        data = response.json()
        
        print(f"[HOSPITAL LOCATOR] Found {len(data.get('elements', []))} elements")
        
        # Calculate distance between two coordinates
        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 6371000  # Earth's radius in meters
            phi1 = radians(lat1)
            phi2 = radians(lat2)
            delta_phi = radians(lat2 - lat1)
            delta_lambda = radians(lon2 - lon1)
            
            a = sin(delta_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            
            return R * c
        
        # Process hospitals
        hospitals = []
        for element in data.get('elements', []):
            # Get coordinates
            hospital_lat = element.get('lat')
            hospital_lon = element.get('lon')
            
            # For ways and relations, use center coordinates
            if not hospital_lat and 'center' in element:
                hospital_lat = element['center'].get('lat')
                hospital_lon = element['center'].get('lon')
            
            if not hospital_lat or not hospital_lon:
                continue
            
            tags = element.get('tags', {})
            
            # Calculate distance
            distance = calculate_distance(lat, lon, hospital_lat, hospital_lon)
            
            # Get hospital name
            name = tags.get('name') or tags.get('alt_name') or tags.get('official_name')
            if not name:
                name = f"{tags.get('amenity', 'Medical Facility').title()}"
            
            hospital = {
                'id': element.get('id'),
                'name': name,
                'lat': hospital_lat,
                'lon': hospital_lon,
                'distance': round(distance, 2),
                'address': tags.get('addr:full') or tags.get('addr:street', ''),
                'phone': tags.get('phone') or tags.get('contact:phone', ''),
                'emergency': tags.get('emergency') == 'yes' or tags.get('healthcare') == 'hospital',
                'opening_hours': tags.get('opening_hours', ''),
            }
            
            hospitals.append(hospital)
        
        # Sort by distance
        hospitals.sort(key=lambda x: x['distance'])
        
        print(f"[HOSPITAL LOCATOR] Returning {len(hospitals)} hospitals")
        
        return {
            'success': True,
            'count': len(hospitals),
            'hospitals': hospitals,
            'user_location': {'lat': lat, 'lon': lon},
            'search_radius': radius
        }
        
    except requests.exceptions.Timeout:
        print(f"[HOSPITAL LOCATOR ERROR] Request timed out")
        raise HTTPException(
            status_code=504,
            detail="Request to OpenStreetMap timed out. Please try again."
        )
    except requests.exceptions.RequestException as e:
        print(f"[HOSPITAL LOCATOR ERROR] Request failed: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch hospital data: {str(e)}"
        )
    except Exception as e:
        print(f"[HOSPITAL LOCATOR ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# ==================== AUTHENTICATION ENDPOINT ====================

@app.post("/api/login", response_model=LoginResponse, tags=["Authentication"])
async def login(login_request: LoginRequest):
    """User/Doctor login endpoint"""
    try:
        # Authenticate user
        user_data = await db_manager.login_user(
            login_request.user_id,
            login_request.password,
            login_request.user_type.value
        )
        
        if not user_data:
            return LoginResponse(
                success=False,
                message="Invalid credentials",
                user_id="",
                user_name="",
                user_type=login_request.user_type
            )
        
        # Generate token
        from services.auth_service import auth_service
        token = auth_service.generate_token(
            login_request.user_id,
            login_request.user_type.value
        )
        
        # Get name based on user type
        if login_request.user_type.value == "USER":
            user_name = user_data.get("user_name", "")
        else:  # DOCTOR
            user_name = user_data.get("doc_name", "")
        
        return LoginResponse(
            success=True,
            message="Login successful",
            user_id=login_request.user_id,
            user_name=user_name,
            user_type=login_request.user_type,
            token=token
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/register", response_model=RegisterResponse, tags=["Authentication"])
async def register(register_request: RegisterRequest):
    """User/Doctor registration endpoint"""
    try:
        user_type = register_request.user_type.value
        user_id = (register_request.user_id or "").strip()
        name = (register_request.name or "").strip()

        if not user_id:
            return RegisterResponse(success=False, message="Username cannot be empty.")
        if len(user_id) > 128:
            return RegisterResponse(success=False, message="Username must be at most 128 characters.")
        if not name:
            return RegisterResponse(success=False, message="Name cannot be empty.")

        # Register user/doctor (doctors get available_status=True in database_service)
        result = await db_manager.register_user({
            "user_id": user_id,
            "name": name,
            "password": register_request.password,
            "user_type": user_type,
            "email": register_request.email,
            "phone": register_request.phone
        })
        
        if not result:
            return RegisterResponse(
                success=False,
                message=f"This username is already taken. Please choose another."
            )
        
        return RegisterResponse(
            success=True,
            message="Registration successful! You can now login.",
            user_id=user_id,
            user_name=name,
            user_type=register_request.user_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== USER MANAGEMENT ENDPOINTS ====================

@app.post("/api/users", response_model=dict, tags=["Users"])
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = await db_manager.get_user(user.user_id)
        if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")
        
        user_data = user.dict()
        result_id = await db_manager.create_user(user_data)
        return {"status": "success", "message": "User created", "id": result_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users", response_model=List[dict], tags=["Users"])
async def get_all_users(user_type: Optional[str] = None):
    """Get all users, optionally filtered by type"""
    try:
        users = await db_manager.get_all_users(user_type)
        # Convert ObjectId to string for JSON serialization
        for user in users:
            user["_id"] = str(user["_id"])
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}", response_model=dict, tags=["Users"])
async def get_user(user_id: str):
    """Get user by ID"""
    try:
        user = await db_manager.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user["_id"] = str(user["_id"])
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/users/{user_id}", response_model=dict, tags=["Users"])
async def update_user(user_id: str, user_update: UserUpdate):
    """Update user information"""
    try:
        update_data = {k: v for k, v in user_update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        success = await db_manager.update_user(user_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"status": "success", "message": "User updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/users/{user_id}", response_model=dict, tags=["Users"])
async def delete_user(user_id: str):
    """Delete a user"""
    try:
        success = await db_manager.delete_user(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "success", "message": "User deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DOCTOR MANAGEMENT ENDPOINTS ====================

@app.post("/api/doctors", response_model=dict, tags=["Doctors"])
async def create_doctor(doctor: DoctorCreate):
    """Create a new doctor"""
    try:
        existing_doctor = await db_manager.get_doctor(doctor.doctor_id)
        if existing_doctor:
            raise HTTPException(status_code=400, detail="Doctor already exists")
        
        doctor_data = doctor.dict()
        result_id = await db_manager.create_doctor(doctor_data)
        return {"status": "success", "message": "Doctor created", "id": result_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/doctors", response_model=List[dict], tags=["Doctors"])
async def get_all_doctors(available_only: bool = False):
    """Get all doctors"""
    try:
        doctors = await db_manager.get_all_doctors(available_only)
        for doctor in doctors:
            doctor["_id"] = str(doctor["_id"])
        return doctors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/doctors/{doctor_id}", response_model=dict, tags=["Doctors"])
async def get_doctor(doctor_id: str):
    """Get doctor by ID"""
    try:
        doctor = await db_manager.get_doctor(doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        doctor["_id"] = str(doctor["_id"])
        return doctor
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/doctors/{doctor_id}", response_model=dict, tags=["Doctors"])
async def update_doctor(doctor_id: str, doctor_update: DoctorUpdate):
    """Update doctor information"""
    try:
        update_data = {k: v for k, v in doctor_update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        success = await db_manager.update_doctor(doctor_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        return {"status": "success", "message": "Doctor updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/doctors/{doctor_id}", response_model=dict, tags=["Doctors"])
async def delete_doctor(doctor_id: str):
    """Delete a doctor"""
    try:
        success = await db_manager.delete_doctor(doctor_id)
        if not success:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return {"status": "success", "message": "Doctor deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/doctors/{doctor_id}/availability", response_model=dict, tags=["Doctors"])
async def update_doctor_availability(
    doctor_id: str,
    available: bool = Query(..., description="true = accepting patients, false = unavailable"),
):
    """Update doctor availability status"""
    try:
        success = await db_manager.update_doctor_availability(doctor_id, available)
        if not success:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return {"status": "success", "message": "Availability updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MEETING MANAGEMENT ENDPOINTS ====================

@app.post("/api/meetings", response_model=dict, tags=["Meetings"])
async def create_meeting(meeting: MeetingCreate):
    """Create a new meeting"""
    try:
        # Verify doctor exists
        doctor = await db_manager.get_doctor(meeting.doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        meeting_data = meeting.dict()
        result_id = await db_manager.create_meeting(meeting_data)
        return {"status": "success", "message": "Meeting created", "id": result_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/meetings", response_model=List[dict], tags=["Meetings"])
async def get_all_meetings():
    """Get all meetings"""
    try:
        meetings = await db_manager.get_all_meetings()
        for meeting in meetings:
            meeting["_id"] = str(meeting["_id"])
        return meetings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/meetings/user/{user_id}", response_model=List[dict], tags=["Meetings"])
async def get_user_meetings(user_id: str):
    """Get all meetings for a user"""
    try:
        meetings = await db_manager.get_user_meetings(user_id)
        for meeting in meetings:
            meeting["_id"] = str(meeting["_id"])
        return meetings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/meetings/doctor/{doctor_id}", response_model=List[dict], tags=["Meetings"])
async def get_doctor_meetings(doctor_id: str):
    """Get all meetings for a doctor"""
    try:
        meetings = await db_manager.get_doctor_meetings(doctor_id)
        for meeting in meetings:
            meeting["_id"] = str(meeting["_id"])
        return meetings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/meetings/{meeting_id}", response_model=dict, tags=["Meetings"])
async def get_meeting(meeting_id: str):
    """Get meeting by ID"""
    try:
        meeting = await db_manager.get_meeting(meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        meeting["_id"] = str(meeting["_id"])
        return meeting
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/meetings/{meeting_id}", response_model=dict, tags=["Meetings"])
async def update_meeting(meeting_id: str, meeting_update: MeetingUpdate):
    """Update meeting information"""
    try:
        update_data = {k: v for k, v in meeting_update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        success = await db_manager.update_meeting(meeting_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        return {"status": "success", "message": "Meeting updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/meetings/{meeting_id}", response_model=dict, tags=["Meetings"])
async def delete_meeting(meeting_id: str):
    """Delete a meeting"""
    try:
        success = await db_manager.delete_meeting(meeting_id)
        if not success:
            raise HTTPException(status_code=404, detail="Meeting not found")
        return {"status": "success", "message": "Meeting deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== APPOINTMENT REQUEST ENDPOINTS ====================

@app.post("/api/appointment-requests", response_model=dict, tags=["Appointment Requests"])
async def create_appointment_request(request: Dict[str, Any]):
    """Create a new appointment request (User only)"""
    try:
        # Get user_id from request body
        user_id = request.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID is required")
        
        # Get user details
        user = await db_manager.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get doctor_id from request
        doctor_id = request.get("doctor_id")
        if not doctor_id:
            raise HTTPException(status_code=400, detail="Doctor ID is required")
        
        # Check if doctor exists and is available
        doctor = await db_manager.get_doctor(doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        # Create appointment request
        request_id = await db_manager.create_appointment_request(
            user_id=user_id,
            user_name=user.get("user_name", ""),
            request_data=request
        )
        
        return {
            "status": "success",
            "message": "Appointment request sent successfully",
            "request_id": request_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/appointment-requests/doctor/{doctor_id}", response_model=List[AppointmentRequestResponse], tags=["Appointment Requests"])
async def get_doctor_appointment_requests(doctor_id: str, status: Optional[str] = None):
    """Get all appointment requests for a doctor"""
    try:
        requests = await db_manager.get_doctor_appointment_requests(doctor_id, status)
        
        # Convert ObjectId to string
        for req in requests:
            req["request_id"] = str(req.pop("_id"))
            
            # Get doctor name
            doctor = await db_manager.get_doctor(req["doctor_id"])
            req["doctor_name"] = doctor.get("doc_name") if doctor else None
        
        return requests
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/appointment-requests/user/{user_id}", response_model=List[AppointmentRequestResponse], tags=["Appointment Requests"])
async def get_user_appointment_requests(user_id: str):
    """Get all appointment requests for a user"""
    try:
        requests = await db_manager.get_user_appointment_requests(user_id)
        
        # Convert ObjectId to string
        for req in requests:
            req["request_id"] = str(req.pop("_id"))
            
            # Get doctor name
            doctor = await db_manager.get_doctor(req["doctor_id"])
            req["doctor_name"] = doctor.get("doc_name") if doctor else None
        
        return requests
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/appointment-requests/{request_id}", response_model=dict, tags=["Appointment Requests"])
async def update_appointment_request(request_id: str, update: AppointmentRequestUpdate):
    """Update appointment request status (Doctor only)"""
    try:
        result = await db_manager.update_appointment_request(
            request_id=request_id,
            status=update.status.value,
            meet_link=update.meet_link
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("message", "Appointment request not found"))
        
        response = {
            "status": "success",
            "message": result.get("message", f"Appointment request {update.status.value.lower()}")
        }
        
        # Include meeting details if accepted
        if result.get("meet_link"):
            response["meet_link"] = result["meet_link"]
        if result.get("meeting_id"):
            response["meeting_id"] = result["meeting_id"]
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/appointment-requests/{request_id}", response_model=dict, tags=["Appointment Requests"])
async def remove_completed_appointment(
    request_id: str,
    actor_id: str = Query(..., description="user_id of the logged-in user or doctor ending the consultation"),
):
    """Remove an ACCEPTED appointment and its meeting after the consultation is finished (user or doctor)."""
    try:
        result = await db_manager.remove_completed_consultation(request_id, actor_id)
        if not result.get("success"):
            msg = result.get("message", "Cannot remove appointment")
            if "not found" in msg.lower():
                status = 404
            elif "Only the patient" in msg or "doctor can end" in msg:
                status = 403
            elif "Invalid appointment" in msg:
                status = 400
            else:
                status = 400
            raise HTTPException(status_code=status, detail=msg)
        return {"status": "success", "message": result.get("message", "Removed")}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ADMIN DASHBOARD ENDPOINTS ====================

@app.get("/api/admin/statistics", response_model=StatisticsResponse, tags=["Admin"])
async def get_statistics():
    """Get platform statistics for admin dashboard"""
    try:
        stats = await db_manager.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Exception handler for request entity too large
@app.exception_handler(413)
async def request_entity_too_large(request: Request, exc: Exception):
    """Handle file size limit exceeded errors"""
    return JSONResponse(
        status_code=413,
        content=ErrorResponse(
            status="error",
            error=f"File too large. Maximum size allowed: {config.api.max_image_upload_size}MB",
            agent="System"
        ).dict()
    )


# Global exception handler (do not swallow HTTPException / validation errors)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions; delegate HTTPException to FastAPI defaults."""
    if isinstance(exc, HTTPException):
        return await http_exception_handler(request, exc)
    print(f"[ERROR] Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status="error",
            error="Internal server error",
            details=str(exc),
            agent="System"
        ).dict()
    )


# ==================== SERVER STARTUP ====================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Multi-Agent Medical Assistant Backend")
    print("=" * 60)
    print(f"📡 Server: http://{config.api.host}:{config.api.port}")
    print(f"📚 API Docs: http://{config.api.host}:{config.api.port}/api/docs")
    print(f"🔍 Health Check: http://{config.api.host}:{config.api.port}/api/health")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host=config.api.host,
        port=config.api.port,
        log_level="info"
    )
