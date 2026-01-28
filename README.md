# Multi-Agent Medical Assistant

> AI-powered medical assistant with 7 specialized agents for comprehensive healthcare support

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](common/LICENSE)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+ (for frontend)
- Virtual environment activated

### Start Backend
```bash
cd backend
./start.sh
```

**Backend runs on:**
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs

### Create Frontend (Coming Soon)
```bash
cd frontend
npx create-react-app .
npm install axios react-markdown
npm start
```

---

## 📁 Project Structure

```
.
├── backend/              # FastAPI backend with 7 AI agents
├── frontend/             # React frontend (ready to create)
├── common/               # Shared resources
│   ├── assets/          # Images, videos, logos
│   ├── data/            # Data files & databases
│   ├── docs/            # Documentation
│   ├── scripts/         # Utility scripts
│   ├── sample_images/   # Test images
│   └── uploads/         # User uploads
├── .env                  # Environment variables (create from common/.env.example)
├── requirements.txt      # Python dependencies
└── venv/                 # Virtual environment
```

---

## 🤖 AI Agents

1. **Psychology Agent** - Mental health support
2. **RAG Agent** - Medical knowledge retrieval
3. **Web Search Agent** - Real-time medical research
4. **Brain Tumor Agent** - MRI analysis
5. **Chest X-ray Agent** - Lung disease detection
6. **Skin Lesion Agent** - Dermatology analysis
7. **Conversation Agent** - Natural dialogue

---

## 📚 Documentation

All documentation is in `common/`:

- **Setup**: `common/GETTING_STARTED.md`
- **Structure**: `common/FINAL_STRUCTURE.md`
- **API Docs**: `common/docs/api/`
- **Agents**: `common/docs/agents/`

---

## 🛠️ Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
python common/scripts/tests/test_psychology_agent.py
```

### Load Data
```bash
python common/scripts/data_ingestion/ingest_rag_data.py
```

---

## 🔑 Environment Setup

1. Copy example environment file:
   ```bash
   cp common/.env.example .env
   ```

2. Add your API keys:
   ```
   GOOGLE_API_KEY=your_gemini_key
   ELEVENLABS_API_KEY=your_elevenlabs_key
   SERPER_API_KEY=your_serper_key
   ```

---

## 📖 API Documentation

Once backend is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

---

## 🎯 Features

- ✅ Multi-agent medical AI system
- ✅ Image analysis (MRI, X-ray, skin lesions)
- ✅ Medical document RAG
- ✅ Real-time web search
- ✅ Voice input/output
- ✅ Natural conversation
- ✅ Guardrails for safety

---

## 📝 License

MIT License - See `common/LICENSE`

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## 📞 Support

For issues, questions, or contributions:
- Check `common/docs/` for guides
- Review `common/GETTING_STARTED.md`
- See API docs at `/api/docs`

---

## 🏗️ Architecture

```
┌─────────────┐
│   Frontend  │ (React)
└──────┬──────┘
       │ HTTP/REST
       │
┌──────▼──────┐
│   Backend   │ (FastAPI)
├─────────────┤
│  7 Agents   │
│  Services   │
│  RAG/Vector │
└─────────────┘
```

---

**Status**: ✅ Production Ready  
**Version**: 2.0  
**Last Updated**: January 27, 2026
