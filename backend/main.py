"""
FastAPI Backend for Multi-Agent Medical Assistant

Main application file with all API endpoints.
"""

import os
import sys
import uuid
import glob
import threading
import time
from typing import Optional

# Add current directory to path to import from backend
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response, Cookie, Request
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from models.schemas import (
    QueryRequest, ChatResponse, UploadResponse,
    ValidationRequest, ValidationResponse,
    SpeechRequest, TranscriptionResponse,
    HealthResponse, ErrorResponse
)
from services.agent_service import AgentService
from services.image_service import ImageService
from services.speech_service import SpeechService
from core.config import Config

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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8000",  # Backend server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        # Clean up file on error
        image_service.delete_file(file_path)
        raise HTTPException(status_code=500, detail=str(e))


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


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
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
