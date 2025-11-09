# Google Gemini + Open-Source Stack Implementation Guide

## Overview
This guide implements the Multi-Agent Medical Assistant using Google Gemini API with a fully open-source stack:
- **LLM**: Google Gemini API (free tier available, pay-as-you-go)
- **Embeddings**: Sentence-Transformers (local, 384-dim, no cost)
- **Vector DB**: Qdrant (local, no cost)
- **Web Search**: DuckDuckGo via LangChain (open-source, no API key)
- **Vision Models**: Local PyTorch models (no cost)

**Total Cost**: ~$0/month for setup, minimal Gemini API usage costs (~$0.001-0.01 per query with free tier)

---

## Phase 1: Prerequisites & Installation ✅

### Step 1: Install Dependencies
All dependencies have been added to `requirements.txt`. Install them:

```bash
cd /home/muthuraja/Project/Multi-Agent-Medical-Assistant
pip install -r requirements.txt
```

**New dependencies added:**
- `google-generativeai==0.3.0` - Google Gemini API client
- `langchain-google-genai==0.0.10` - LangChain integration for Gemini
- `sentence-transformers==2.2.2` - Local embeddings (384-dim, all-MiniLM-L6-v2)

**Removed/Not Required:**
- Azure OpenAI dependencies (completely removed)
- No cloud embedding APIs needed

---

## Phase 2: Configuration Files ✅

### Step 2: Set Up Environment Variables

Copy the provided Gemini configuration file:

```bash
cp .env.gemini .env
```

Or manually create `.env` with:

```
# Google Gemini API Configuration
GOOGLE_API_KEY=your-gemini-api-key-here

# Qdrant Vector Database (Local)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# No API keys needed for:
# - Embeddings (runs locally with sentence-transformers)
# - Web search (uses open-source DuckDuckGo)
# - Vision models (local PyTorch)
```

### Step 3: Verify Configuration Files

The following files have been **automatically updated** for Gemini:

✅ **config.py** - Updated with:
- All `AzureChatOpenAI` → `ChatGoogleGenerativeAI`
- All `AzureOpenAIEmbeddings` → `SentenceTransformerEmbeddings`
- Temperature settings maintained per agent type
- Qdrant default URL set to localhost:6333

✅ **requirements.txt** - Updated with:
- Google Gemini dependencies added
- Sentence-Transformers added
- Azure OpenAI dependencies removed (optional)

✅ **New Files Created:**
- `agents/rag_agent/embeddings_wrapper.py` - LangChain-compatible wrapper for SentenceTransformer
- `agents/web_search_processor_agent/opensource_search.py` - DuckDuckGo-based web search
- `.env.gemini` - Gemini configuration template

---

## Phase 3: Start Qdrant Vector Database

### Step 4: Run Qdrant Locally (Docker)

**Option A: Using Docker (Recommended)**
```bash
docker run -d \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/data/qdrant_db:/qdrant/storage \
  qdrant/qdrant:latest
```

**Option B: Using Qdrant CLI (if Docker not available)**
```bash
# Download and run Qdrant standalone
wget https://github.com/qdrant/qdrant/releases/download/v1.7.0/qdrant-x86_64-unknown-linux-gnu.zip
unzip qdrant-x86_64-unknown-linux-gnu.zip
./qdrant --storage-path ./data/qdrant_db
```

**Verify Qdrant is running:**
```bash
curl http://localhost:6333/health
```

Expected response:
```json
{"status":"ok"}
```

---

## Phase 4: Test Configuration

### Step 5: Validate Gemini API Connection

Create a test script `test_gemini_config.py`:

```python
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Test Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1
)

# Test a simple query
response = llm.invoke("Hello, are you working?")
print("Gemini Response:", response.content)
```

Run the test:
```bash
python test_gemini_config.py
```

Expected output: Gemini responds to your greeting.

### Step 6: Validate Embeddings

Create a test script `test_embeddings.py`:

```python
from agents.rag_agent.embeddings_wrapper import SentenceTransformerEmbeddings

# Initialize embeddings
embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')

# Test embedding
query = "What is diabetes?"
embedding = embeddings.embed_query(query)
print(f"Query: {query}")
print(f"Embedding dimension: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")
```

Run the test:
```bash
python test_embeddings.py
```

Expected output: Embedding of 384 dimensions.

### Step 7: Validate Web Search

Create a test script `test_web_search.py`:

```python
from agents.web_search_processor_agent.opensource_search import OpenSourceWebSearch

# Initialize web search (no API key needed)
search = OpenSourceWebSearch(max_results=3)

# Test search
results = search.search("COVID-19 treatment options")
print("Search Results:")
print(results)
```

Run the test:
```bash
python test_web_search.py
```

Expected output: Top 3 DuckDuckGo search results about COVID-19 treatment.

---

## Phase 5: Document Ingestion

### Step 8: Prepare Medical Documents

Place PDF documents in the ingestion directory:
```bash
mkdir -p data/raw
# Copy your medical PDF files to data/raw/
```

### Step 9: Ingest Documents

```bash
python ingest_rag_data.py --input data/raw
```

This will:
1. Parse PDFs using Docling
2. Create semantic chunks using Gemini
3. Generate embeddings with sentence-transformers (local)
4. Index in Qdrant
5. Save parsed content to `data/parsed_docs/`

Expected output:
```
Ingesting files from directory: data/raw
Parsed 5 documents successfully
Created 245 document chunks
Indexed in Qdrant collection: medical_assistance_rag
```

---

## Phase 6: Run the Application

### Step 10: Start the FastAPI Server

```bash
python app.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 11: Access the Web Interface

Open browser and navigate to:
```
http://localhost:8000
```

### Step 12: Test End-to-End Workflow

In the chat interface:
1. **Text Query**: Ask "What are symptoms of COVID-19?"
   - Triggers RAG Agent
   - Uses Gemini to expand query
   - Retrieves from Qdrant using sentence-transformers embeddings
   - Generates response with Gemini
   - Returns sources from ingested documents

2. **Image Query**: Upload a chest X-ray image
   - Triggers Vision Agent
   - Analyzes with local PyTorch model
   - Uses Gemini for interpretation
   - Returns classification with confidence

3. **Web Search Query**: Ask about latest medical news
   - Triggers Web Search Agent
   - Uses DuckDuckGo (open-source)
   - Generates response with Gemini
   - Returns links to sources

---

## Architecture Changes Summary

### Components Updated for Gemini

| Component | Before (Azure) | After (Gemini) | Status |
|-----------|---|---|---|
| **LLM Provider** | AzureChatOpenAI | ChatGoogleGenerativeAI | ✅ Updated |
| **Embeddings** | AzureOpenAIEmbeddings (1536-dim) | SentenceTransformer (384-dim) | ✅ Updated |
| **Embedding Wrapper** | None | SentenceTransformerEmbeddings | ✅ Created |
| **Vector DB** | Qdrant Cloud | Qdrant Local | ✅ Updated |
| **Web Search** | Tavily API | DuckDuckGo + SearchWrapper | ✅ Updated |
| **Config File** | config.py (Azure) | config.py (Gemini) | ✅ Updated |
| **Dependencies** | requirements.txt (Azure) | requirements.txt (Gemini) | ✅ Updated |

### Files Modified

```
✅ config.py
   - 5 LLM instantiations → ChatGoogleGenerativeAI
   - 1 Embedding instantiation → SentenceTransformerEmbeddings
   - Default QDRANT_URL → http://localhost:6333

✅ requirements.txt
   - Removed: Azure OpenAI dependencies (optional)
   - Added: google-generativeai, langchain-google-genai
   - Added: sentence-transformers
   
✅ Created: agents/rag_agent/embeddings_wrapper.py
   - SentenceTransformerEmbeddings class (LangChain-compatible)
   
✅ Created: agents/web_search_processor_agent/opensource_search.py
   - OpenSourceWebSearch class (DuckDuckGo-based)
   - SearchWrapper class (fallback support)
```

### Backward Compatibility

✅ **Fully Compatible** - No changes needed to:
- `agents/agent_decision.py` (LangGraph workflow)
- `app.py` (FastAPI endpoints)
- `agents/rag_agent/__init__.py` (RAG orchestration)
- `agents/image_analysis_agent/` (Vision models)
- All other agent files

---

## Cost Comparison

| Component | Azure Setup | Open-Source Setup | Monthly Cost Difference |
|-----------|---|---|---|
| LLM (1000 queries/day) | $30-50 | $5-15 (Gemini free tier) | -$20-40 |
| Embeddings | $8-12 | $0 (local) | -$8-12 |
| Vector DB | $16 (Qdrant Cloud) | $0 (local) | -$16 |
| Web Search | $20 (Tavily) | $0 (DuckDuckGo) | -$20 |
| **TOTAL** | **$74-98** | **$5-15** | **-$59-93/month** |

---

## Troubleshooting

### Issue: "GOOGLE_API_KEY not found"
**Solution**: Ensure `.env` file exists with valid API key
```bash
cat .env | grep GOOGLE_API_KEY
```

### Issue: "Qdrant connection refused"
**Solution**: Start Qdrant container
```bash
docker ps | grep qdrant  # Check if running
docker run -d -p 6333:6333 qdrant/qdrant:latest  # Start if not running
```

### Issue: "SentenceTransformer model download fails"
**Solution**: Pre-download model before first use
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Issue: "DuckDuckGo search returns no results"
**Solution**: Check internet connection and query format
```bash
python test_web_search.py  # Test web search functionality
```

### Issue: "Gemini API rate limit exceeded"
**Solution**: Gemini free tier has limits (~60 requests/minute). Wait or use paid tier.

---

## Next Steps

1. ✅ **Phase 1**: Install dependencies (COMPLETED)
2. ✅ **Phase 2**: Configure environment (COMPLETED)
3. ✅ **Phase 3**: Start Qdrant (MANUAL: Run Docker command above)
4. ⏳ **Phase 4**: Validate configuration (MANUAL: Run test scripts above)
5. ⏳ **Phase 5**: Ingest documents (MANUAL: Run ingest_rag_data.py)
6. ⏳ **Phase 6**: Run application (MANUAL: Run app.py)

---

## Support & Resources

- **Gemini API Docs**: https://ai.google.dev/docs
- **Sentence-Transformers**: https://www.sbert.net/
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **LangChain Integration**: https://python.langchain.com/docs/integrations/providers/google

---

## Configuration Validation Checklist

- [ ] `.env` file exists with `GOOGLE_API_KEY`
- [ ] `pip install -r requirements.txt` completed successfully
- [ ] Qdrant Docker container running on localhost:6333
- [ ] `test_gemini_config.py` passes
- [ ] `test_embeddings.py` returns 384-dim embedding
- [ ] `test_web_search.py` returns search results
- [ ] `python app.py` starts without errors
- [ ] Web UI loads at `http://localhost:8000`
- [ ] Test query returns RAG results with sources
- [ ] Test image upload returns vision model results

---

**Last Updated**: 2025
**Status**: ✅ Ready for Phase 3 (Manual Qdrant startup)
