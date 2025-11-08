# API Requirements Summary

## TL;DR - What You Need to Run This Project

### Minimum Setup (Cloud Only - Recommended for Start)
1. **Azure OpenAI Account** (for LLM and embeddings)
   - Cost: ~$0.01-0.10 per query (depends on model size)
   - Signup: https://azure.microsoft.com/en-us/products/ai-services/openai-service/

2. **Copy `.env.example` to `.env` and fill in Azure keys**
   ```bash
   cp .env.example .env
   # Edit .env with your Azure OpenAI credentials
   ```

3. **Run setup and start**
   ```bash
   ./setup.sh  # Interactive setup
   python app.py  # Start server
   ```

**Total Setup Time:** ~10 minutes
**Cost:** Free-tier available, then ~$0.01-0.10 per query

---

## Complete API Reference

### ✅ REQUIRED (Choose One)

| Component | Purpose | Cloud Option | Open-Source |
|-----------|---------|---|---|
| **LLM** (Language Model) | Powers all reasoning, routing, response generation | Azure OpenAI (gpt-4o) | Ollama (Mistral 7B) |
| **Embeddings** | Convert text to vectors for RAG retrieval | Azure OpenAI | sentence-transformers (local) |

### ⚠️ OPTIONAL (Can Skip or Use Alternatives)

| Component | Purpose | Cloud Option | Open-Source | Skip? |
|-----------|---------|---|---|---|
| **Vector DB** | Store & retrieve documents | Qdrant Cloud | Qdrant Local ✅ | No - needed for RAG |
| **Web Search** | Research papers & medical news | Tavily API | DuckDuckGo ✅ | Yes - fallback only |
| **Speech TTS** | Text-to-Speech | ElevenLabs | pyttsx3 ✅ | Yes - UI feature only |
| **Speech STT** | Speech-to-Text | ElevenLabs | Whisper ✅ | Yes - UI feature only |

---

## Setup Paths & Costs

### Path 1: Cloud Only (Azure OpenAI) ⭐ RECOMMENDED FOR START
**Cost:** $0 initial + $0.01-0.10 per query
**Setup:** 10 minutes
**Speed:** Fast (cloud inference)

What you need:
```env
deployment_name=gpt-4o-deployment
model_name=gpt-4o
azure_endpoint=https://your-resource.openai.azure.com/
openai_api_key=your-key
openai_api_version=2024-05-01

embedding_deployment_name=text-embedding-3-large-deployment
embedding_model_name=text-embedding-3-large
embedding_azure_endpoint=https://your-resource.openai.azure.com/
embedding_openai_api_key=your-key
embedding_openai_api_version=2024-05-01
```

### Path 2: Open-Source (Ollama + Local) 
**Cost:** $0 (just electricity)
**Setup:** 20 minutes
**Speed:** Slow on CPU, ~1-2s per query on GPU

What you need:
1. Install Ollama: https://ollama.ai
2. Run: `ollama serve`
3. Pull model: `ollama pull mistral`
4. Modify `config.py` (see below)

Modified config.py example:
```python
from langchain_ollama import OllamaLLM, OllamaEmbeddings

class AgentDecisoinConfig:
    def __init__(self):
        self.llm = OllamaLLM(
            model="mistral",
            base_url="http://localhost:11434",
            temperature=0.1
        )
```

### Path 3: Hybrid (Azure LLM + Local Vector DB)
**Cost:** $0.01-0.10 per query (LLM only)
**Setup:** 15 minutes
**Speed:** Very fast

What you need:
- Azure OpenAI credentials (as in Path 1)
- Local Qdrant (automatic, no setup)

---

## Quick Start - Step by Step

### Step 1: Choose Your Path
- **Path 1 (Cloud)** → Get Azure keys → Skip to Step 3
- **Path 2 (Open-Source)** → Install Ollama → Step 2
- **Path 3 (Hybrid)** → Get Azure keys + Install Ollama → Step 2

### Step 2: Clone & Setup (Same for All Paths)
```bash
# Clone repo
git clone https://github.com/souvikmajumder26/Multi-Agent-Medical-Assistant.git
cd Multi-Agent-Medical-Assistant

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
# Copy example file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your editor
```

### Step 4: Start Required Services
**For Cloud (Path 1):** Skip this, Azure is cloud-hosted

**For Open-Source (Path 2 or 3):**
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start the app
source venv/bin/activate
python app.py
```

### Step 5: Test & Use
```bash
# Open browser
http://localhost:8000

# Or test API
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is diabetes?"}'
```

---

## API Keys Explained

### Azure OpenAI Keys
Where to find them:
1. Go to https://portal.azure.com/
2. Create "OpenAI" resource
3. Go to "Keys and Endpoint"
4. Copy `Key 1`, `Endpoint`, `Deployment Name`

Example values:
```
deployment_name: gpt-4o-deployment
model_name: gpt-4o
azure_endpoint: https://my-resource.openai.azure.com/
openai_api_key: 1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
openai_api_version: 2024-05-01
```

### Tavily API Key
- Go to https://tavily.com/
- Sign up (free tier: 50 searches/month)
- Copy API key
- For local alternative: Use DuckDuckGo (no key needed)

### ElevenLabs API Key
- Go to https://elevenlabs.io/
- Sign up (free tier: 10,000 characters/month)
- Go to Account → API Key
- For local alternative: Use pyttsx3 (no key needed)

### Qdrant
- **Cloud:** https://cloud.qdrant.io/ (optional)
- **Local:** Automatic in `./data/qdrant_db/` (recommended)

---

## Minimal .env Examples

### Minimal Cloud Setup
```env
deployment_name=gpt-4o-deployment
model_name=gpt-4o
azure_endpoint=https://my-resource.openai.azure.com/
openai_api_key=YOUR-KEY-HERE
openai_api_version=2024-05-01
embedding_deployment_name=text-embedding-3-large-deployment
embedding_model_name=text-embedding-3-large
embedding_azure_endpoint=https://my-resource.openai.azure.com/
embedding_openai_api_key=YOUR-KEY-HERE
embedding_openai_api_version=2024-05-01
```

### Minimal Open-Source Setup
```env
# Leave empty or comment out - nothing needed!
# Make sure Ollama is running on localhost:11434
```

---

## Cost Comparison

### Monthly Usage Estimate (1000 queries)

| Setup | LLM Cost | Embeddings | Vector DB | Storage | Total |
|-------|----------|-----------|-----------|---------|-------|
| **Cloud** | $10 | $5 | $0 (local) | $0 | **$15/mo** |
| **Open-Source** | $0 | $0 | $0 | $0 | **$0** |
| **Hybrid** | $10 | $5 | $0 | $0 | **$15/mo** |

Note: Cloud costs vary based on model size and query complexity

---

## Troubleshooting

### "API Key Invalid"
```
❌ Check 1: Copy the key again from Azure Portal
❌ Check 2: Ensure no extra spaces in .env
❌ Check 3: Try a fresh API key from Azure
```

### "Ollama connection refused"
```
❌ Check: Run `ollama serve` in another terminal
❌ Check: Verify ollama is on localhost:11434
❌ Check: Run `curl http://localhost:11434`
```

### "Out of memory (CUDA)"
```
❌ Solution 1: Use smaller model (neural-chat vs llama2)
❌ Solution 2: Use Cloud (Azure OpenAI)
❌ Solution 3: Increase GPU memory
```

### "Very slow responses (30+ seconds)"
```
⚠️  Normal for CPU inference, expected on first request
✅ Solution 1: Use GPU (NVIDIA/AMD)
✅ Solution 2: Use Cloud (Azure OpenAI) for instant responses
✅ Solution 3: Upgrade CPU
```

---

## File Reference

| File | Purpose | Cloud? | Open-Source? |
|------|---------|--------|---|
| `config.py` | LLM/API config | Uses Azure | Modify to use Ollama |
| `.env` | API keys | ✅ | Leave empty |
| `.env.example` | Template | ✅ | Use as-is |
| `SETUP_GUIDE.md` | Full docs | ✅ | ✅ |
| `setup.sh` | Auto setup | ✅ | ✅ |
| `requirements.txt` | Deps | ✅ | ✅ |
| `requirements-alternatives.txt` | Alt deps | N/A | Optional |

---

## Next Steps

1. **Choose your path** (Cloud/Open-Source/Hybrid)
2. **Run setup.sh** (automatic configuration)
3. **Test LLM connection** (verify API keys work)
4. **Ingest documents** (prepare RAG data)
5. **Start server** (python app.py)
6. **Test in browser** (http://localhost:8000)

---

## Support

- **Setup issues?** → Read SETUP_GUIDE.md
- **API issues?** → Check your .env file
- **Performance issues?** → See Troubleshooting section
- **Code issues?** → See .github/copilot-instructions.md

**Ready to start?** → Run `./setup.sh`
