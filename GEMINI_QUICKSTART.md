# Quick Start Guide - Google Gemini + Open-Source Stack

## ⚡ TL;DR - Get Running in 5 Minutes

### 1. Install Dependencies (2 min)
```bash
cd /home/muthuraja/Project/Multi-Agent-Medical-Assistant
pip install -r requirements.txt
```

### 2. Set Environment Variables (1 min)
```bash
cp .env.gemini .env
# Verify GOOGLE_API_KEY is present in .env
cat .env | grep GOOGLE_API_KEY
```

### 3. Start Qdrant (1 min)
```bash
docker run -d -p 6333:6333 -v $(pwd)/data/qdrant_db:/qdrant/storage qdrant/qdrant:latest
```

### 4. Validate Setup (30 sec)
```bash
python test_gemini_setup.py
```

### 5. Run Application (30 sec)
```bash
python app.py
# Open browser: http://localhost:8000
```

**Total Time**: ~5 minutes ✅

---

## 🔍 What Was Changed?

### Configuration (✅ Done)
- ✅ `config.py` - Azure OpenAI → Google Gemini API
- ✅ `requirements.txt` - Added Gemini, sentence-transformers
- ✅ `.env.gemini` - New Gemini configuration template
- ✅ `agents/rag_agent/embeddings_wrapper.py` - Sentence-Transformers wrapper (NEW)
- ✅ `agents/web_search_processor_agent/opensource_search.py` - DuckDuckGo search (NEW)

### No Changes Needed
- ✅ `app.py` - Works as-is
- ✅ `agents/agent_decision.py` - Works as-is
- ✅ All other agent files - Work as-is

---

## 📊 Stack Comparison

```
BEFORE (Azure)                  AFTER (Gemini + Open-Source)
├── Azure OpenAI (LLM)          ├── Google Gemini API (LLM) ✓
├── Azure OpenAI (Embeddings)   ├── Sentence-Transformers (Embeddings) ✓
├── Qdrant Cloud                ├── Qdrant Local Docker ✓
├── Tavily API (Web Search)     ├── DuckDuckGo (Web Search) ✓
└── PyTorch Vision (Local)      └── PyTorch Vision (Local) ✓

Cost: $74-98/month              Cost: $5-15/month
```

---

## 🧪 Validation Tests

Run comprehensive validation:
```bash
python test_gemini_setup.py
```

Tests:
1. ✅ Gemini API connection
2. ✅ Sentence-Transformers embeddings
3. ✅ Qdrant vector database
4. ✅ DuckDuckGo web search
5. ✅ Configuration module

Expected output: `Overall: 5/5 tests passed`

---

## 📋 Step-by-Step Setup

### Prerequisites
- Python 3.11+
- Docker (for Qdrant)
- 2GB free disk space
- Internet connection

### Step 1: Install Dependencies
```bash
# Navigate to project directory
cd /home/muthuraja/Project/Multi-Agent-Medical-Assistant

# Install all required packages
pip install -r requirements.txt

# This installs:
# - google-generativeai (Gemini API)
# - langchain-google-genai (Gemini integration)
# - sentence-transformers (local embeddings)
# - All other dependencies (FastAPI, LangChain, etc.)
```

**Time**: ~2 minutes
**Disk space**: ~1.5GB

### Step 2: Configure Environment

**Option A: Using provided template**
```bash
cp .env.gemini .env
```

**Option B: Manual setup**
```bash
cat > .env << EOF
# Google Gemini API
GOOGLE_API_KEY=your-gemini-api-key-here

# Qdrant Vector Database (Local)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Other configs (optional)
LOG_LEVEL=INFO
API_PORT=8000
EOF
```

**Verify**:
```bash
cat .env | grep GOOGLE_API_KEY
```

### Step 3: Start Qdrant Vector Database

**Using Docker (Recommended)**:
```bash
# Start Qdrant container
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -v $(pwd)/data/qdrant_db:/qdrant/storage \
  qdrant/qdrant:latest

# Check if running
docker logs qdrant
```

**Verify connection**:
```bash
curl http://localhost:6333/health
# Expected: {"status":"ok"}
```

### Step 4: Validate Configuration

Run the validation test suite:
```bash
python test_gemini_setup.py
```

Expected output:
```
Gemini API....................... ✅ PASSED
Embeddings....................... ✅ PASSED
Qdrant.......................... ✅ PASSED
Web Search...................... ✅ PASSED
Config.......................... ✅ PASSED

Overall: 5/5 tests passed
```

### Step 5: Ingest Medical Documents (Optional)

Prepare documents:
```bash
mkdir -p data/raw
# Copy your PDF files to data/raw/
cp /path/to/your/medical/documents/*.pdf data/raw/
```

Ingest:
```bash
python ingest_rag_data.py --input data/raw
```

This will:
- Parse PDFs with Docling
- Create semantic chunks
- Generate embeddings (locally with sentence-transformers)
- Index in Qdrant
- Save parsed content

### Step 6: Run the Application

**Start FastAPI server**:
```bash
python app.py
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Access web interface**:
- Open browser: `http://localhost:8000`
- You should see the chat interface

### Step 7: Test the System

In the web interface, try:

1. **Text Query**: "What are symptoms of COVID-19?"
   - Should retrieve medical documents from RAG
   - Generate response using Gemini
   - Show source documents

2. **Web Search**: "Latest COVID-19 treatment research"
   - Should search DuckDuckGo
   - Generate response using Gemini
   - Show source links

3. **Image Upload** (if documents ingested):
   - Upload a chest X-ray image
   - Should analyze with vision model
   - Generate interpretation using Gemini

---

## 🛠 Troubleshooting

### Issue: `GOOGLE_API_KEY not found`
**Solution**:
```bash
# Check if .env exists
ls -la .env

# Verify API key is present
grep GOOGLE_API_KEY .env

# If missing, copy template again
cp .env.gemini .env
```

### Issue: `ModuleNotFoundError: No module named 'google'`
**Solution**:
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify installation
python -c "import google; print(google.__version__)"
```

### Issue: `Connection refused` on Qdrant
**Solution**:
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Start if not running
docker run -d -p 6333:6333 -v $(pwd)/data/qdrant_db:/qdrant/storage qdrant/qdrant:latest

# Test connection
curl http://localhost:6333/health
```

### Issue: Web search returns no results
**Solution**:
- Check internet connection
- Try different search query
- This is normal - DuckDuckGo free API can be rate-limited

### Issue: Gemini returns rate limit error
**Solution**:
- Free tier has ~60 requests/minute limit
- Wait a moment and retry
- Consider using paid tier for production

### Issue: Low embedding quality
**Solution**:
- all-MiniLM-L6-v2 is fast (384-dim)
- For better quality, use: `all-mpnet-base-v2` (768-dim)
- Update in `config.py` RAGConfig

---

## 📚 API Reference

### Gemini API
- **Model**: `gemini-pro`
- **Free tier**: Yes (~$0 for low usage)
- **Rate limit**: 60 requests/minute free tier
- **Docs**: https://ai.google.dev/docs

### Sentence-Transformers
- **Model**: `all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Speed**: Very fast (local, CPU-friendly)
- **Cost**: Free (local, no API calls)

### Qdrant
- **Mode**: Local Docker
- **Port**: 6333
- **Storage**: `./data/qdrant_db`
- **Cost**: Free (local)

### DuckDuckGo
- **API**: Free, no authentication
- **Limits**: Reasonable rate limits
- **Cost**: Free

---

## ✅ Verification Checklist

Before running production:
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created with valid GOOGLE_API_KEY
- [ ] Qdrant running: `docker ps | grep qdrant`
- [ ] Test suite passing: `python test_gemini_setup.py`
- [ ] App starts without errors: `python app.py`
- [ ] Web UI loads: `http://localhost:8000`
- [ ] First query works and returns response
- [ ] Chat history persists across messages

---

## 🔄 Reverting to Previous Setup

To go back to Azure configuration:
```bash
git checkout config.py requirements.txt
```

To keep both configurations:
```bash
# Current (Gemini) remains in config.py
# Create backup with Azure config
git show HEAD:config.py > config_azure.py
```

---

## 📞 Support

### Files Modified
- `config.py` - LLM/Embedding configuration
- `requirements.txt` - Dependencies
- `.env.gemini` - Environment template

### Files Created
- `test_gemini_setup.py` - Validation tests
- `agents/rag_agent/embeddings_wrapper.py` - Embeddings wrapper
- `agents/web_search_processor_agent/opensource_search.py` - Web search
- `GEMINI_SETUP_IMPLEMENTATION.md` - Detailed guide

### Documentation
- Read: `GEMINI_SETUP_IMPLEMENTATION.md` for detailed setup
- Read: `API_REQUIREMENTS.md` for all dependencies
- Read: `.github/copilot-instructions.md` for architecture

---

## 🎯 What's Next?

1. ✅ **Phase 1-4**: System setup (THIS GUIDE)
2. ⏳ **Phase 5**: Ingest documents (`python ingest_rag_data.py`)
3. ⏳ **Phase 6**: Deploy application (production)
4. ⏳ **Phase 7**: Monitor and optimize

---

**Status**: Ready for immediate use ✅
**Last Updated**: 2025
**Version**: Gemini 1.0
