# Backend - Multi-Agent Medical Assistant API

FastAPI-based backend for the Multi-Agent Medical Assistant system.

## 🏗️ Structure

```
backend/
├── main.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── start.sh               # Quick start script
│
├── api/                   # API route handlers (future expansion)
├── services/              # Business logic layer
│   ├── agent_service.py   # Agent orchestration
│   ├── image_service.py   # Image processing
│   └── speech_service.py  # Speech/TTS services
│
├── models/                # Pydantic models
│   └── schemas.py         # Request/Response models
│
├── core/                  # Core utilities
│   └── config.py          # Configuration
│
└── utils/                 # Utility functions
```

## 🚀 Quick Start

### Option 1: Using start script (Recommended)
```bash
# From project root
./backend/start.sh
```

### Option 2: Manual start
```bash
cd backend
source ../venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt
python main.py
```

## 📡 API Endpoints

### Health & Info
- `GET /` - API information
- `GET /api/health` - Health check

### Chat
- `POST /api/chat` - Process text query

### Image Analysis
- `POST /api/upload` - Upload and analyze medical image

### Validation
- `POST /api/validate` - Human validation for AI outputs

### Speech
- `POST /api/transcribe` - Speech-to-text
- `POST /api/generate-speech` - Text-to-speech

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🔧 Configuration

Configuration is loaded from `backend/core/config.py` which reads from the root `.env` file.

Required environment variables:
```env
GOOGLE_API_KEY=your_gemini_api_key
ELEVEN_LABS_API_KEY=your_elevenlabs_key
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

## 🧪 Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is diabetes?"}'
```

## 🛠️ Development

### Adding New Endpoints

1. Create route handler in `main.py` or create new file in `api/`
2. Define Pydantic models in `models/schemas.py`
3. Implement business logic in appropriate service class
4. Update API documentation

### Service Layer

The backend follows a service-oriented architecture:
- **Routes** (`main.py`): Handle HTTP requests/responses
- **Services** (`services/`): Business logic and agent coordination
- **Models** (`models/`): Data validation and serialization

## 📊 Response Format

All endpoints return JSON responses:

**Success Response:**
```json
{
  "status": "success",
  "response": "Agent response text",
  "agent": "AGENT_NAME",
  "result_image": "/path/to/image.png"  // optional
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": "Error message",
  "details": "Detailed error information",  // optional
  "agent": "System"
}
```

## 🔐 Security

- File upload size limits enforced
- Secure filename handling
- CORS configured for development
- Session cookie support

## 📝 Notes

- Backend runs on port 8000 by default
- Static files (uploads) are served from `/uploads` route
- Old speech files are cleaned up every 5 minutes
- All routes are prefixed with `/api` except root

## 🐛 Troubleshooting

### Port already in use
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Import errors
```bash
# Ensure you're in the correct directory and venv is activated
cd backend
source ../venv/bin/activate
pip install -r requirements.txt
```

### Agent errors
Check that:
1. Root `.env` file exists with API keys
2. Qdrant is running (for RAG agent)
3. Models are downloaded (for CV agents)

## 🔗 Related

- Frontend: `../frontend/README.md`
- Agent Documentation: `../agents/README.md`
- Main README: `../README.md`
