# 📋 Project Setup & API Requirements - Complete Summary

## What You'll Find in This Project

This is a **FastAPI-based multi-agent medical chatbot** that uses:
- **LLMs** (Azure OpenAI or Ollama) for reasoning and responses
- **Vector embeddings** for document retrieval (RAG)
- **Computer vision models** for medical image analysis
- **Web search** for latest medical research
- **Voice interfaces** for accessibility

---

## 🎯 Quick Start (Choose One Path)

### Path 1: Cloud Setup (Recommended for Production)
**Time:** 10 minutes | **Cost:** $0.01-0.10/query | **Speed:** Fast ⚡

```bash
# 1. Get Azure OpenAI keys from https://portal.azure.com/
# 2. Run setup script
./setup.sh
# Select option: 1 (Cloud Setup)
# 3. Start server
python app.py
# 4. Open http://localhost:8000
```

### Path 2: Open-Source (Recommended for Local Dev)
**Time:** 20 minutes | **Cost:** Free | **Speed:** Slow on CPU

```bash
# 1. Install Ollama from https://ollama.ai
# 2. Run setup script
./setup.sh
# Select option: 2 (Open-Source Setup)
# 3. In Terminal 2, start Ollama
ollama serve
# 4. In Terminal 1, start server (after setup.sh modifies config.py)
python app.py
# 5. Open http://localhost:8000
```

### Path 3: Hybrid (Azure LLM + Local Vector DB)
**Time:** 15 minutes | **Cost:** $0.01-0.10/query | **Speed:** Very Fast ⚡⚡

```bash
# 1. Get Azure OpenAI keys
# 2. Run setup script
./setup.sh
# Select option: 3 (Hybrid Setup)
# 3. Start server
python app.py
# 4. Open http://localhost:8000
```

---

## 📦 What Gets Created for You

### New Documentation Files
| File | Purpose | Size |
|------|---------|------|
| **SETUP_GUIDE.md** | 🔧 Detailed setup with 4 options (Cloud/Open-Source/Hybrid/Docker) | 14 KB |
| **API_REQUIREMENTS.md** | 📋 API costs, requirements, comparisons, troubleshooting | 8 KB |
| **.env.example** | 🔑 Template for all environment variables | 7 KB |
| **setup.sh** | 🚀 Interactive setup script (automated) | 13 KB |
| **requirements-alternatives.txt** | 📚 Alt dependencies (Ollama, pyttsx3, etc) | 4 KB |
| **.github/copilot-instructions.md** | 🤖 AI agent guide to codebase | 6.5 KB |

### Use These Files In This Order:
1. **START HERE:** `API_REQUIREMENTS.md` - Understand what's needed
2. **THEN:** Run `./setup.sh` - Automated setup
3. **REFERENCE:** `SETUP_GUIDE.md` - Deep dive into each option
4. **IF ISSUES:** `API_REQUIREMENTS.md` troubleshooting section

---

## 🔐 All API Keys Explained

### ✅ YOU MUST CHOOSE ONE:

**Option A: Cloud LLM (Azure OpenAI)**
```
What: Provides GPT-4o model for text generation
Cost: ~$0.01-0.10 per query (pay as you go)
Where: https://portal.azure.com/
What you get from Azure:
  - deployment_name (e.g., "gpt-4o-deployment")
  - model_name (e.g., "gpt-4o")
  - azure_endpoint (e.g., "https://my-resource.openai.azure.com/")
  - openai_api_key (copy from Keys and Endpoint)
  - openai_api_version (e.g., "2024-05-01")
```

**Option B: Open-Source LLM (Ollama)**
```
What: Runs Mistral 7B locally on your computer
Cost: FREE (just uses your electricity)
Where: https://ollama.ai
What you do:
  1. Download and install Ollama
  2. Run: ollama serve (in terminal)
  3. Run: ollama pull mistral (download model)
  4. Edit config.py to use OllamaLLM instead of AzureChatOpenAI
```

### 🔵 ALSO NEEDED FOR LLM:

**Embeddings Model (same provider as LLM)**
```
Cloud: Use Azure's text-embedding-3-large
  - embedding_deployment_name
  - embedding_model_name
  - embedding_azure_endpoint
  - embedding_openai_api_key
  - embedding_openai_api_version

Open-Source: Uses sentence-transformers (local, no keys)
```

### ⚪ OPTIONAL (Can Skip):

**Web Search (pick one)**
```
Option 1: Tavily API (requires API key)
  - Where: https://tavily.com/
  - Cost: Free tier (50/month), then $0.05 per 1000
  - Key: TAVILY_API_KEY

Option 2: DuckDuckGo (no key needed)
  - Free, no signup needed
  - Modify: agents/web_search_processor_agent/tavily_search.py
  - No action needed in .env
```

**Speech (pick one or skip)**
```
Option 1: ElevenLabs (requires API key)
  - Where: https://elevenlabs.io/
  - Cost: Free tier (10,000 chars/month)
  - Key: ELEVEN_LABS_API_KEY

Option 2: pyttsx3 (no key needed)
  - Local text-to-speech
  - No signup needed
  - Already in requirements.txt
```

**Vector Database**
```
Option 1: Local Qdrant (default, no keys)
  - Stores vectors locally in ./data/qdrant_db/
  - Completely free
  - No configuration needed ✅

Option 2: Qdrant Cloud (optional, remote)
  - Where: https://cloud.qdrant.io/
  - Keys: QDRANT_URL, QDRANT_API_KEY
  - Not recommended - local is faster
```

---

## 💰 Monthly Cost Comparison

### For 1000 Queries Per Month:

| Setup | LLM | Embeddings | APIs | Total |
|-------|-----|-----------|------|-------|
| **Cloud Only** ☁️ | $10 | $5 | ~$1 | **$16/mo** |
| **Open-Source** 🖥️ | FREE | FREE | FREE | **$0/mo** |
| **Hybrid** 🔀 | $10 | $5 | ~$0 | **$15/mo** |

---

## 📋 Environment Variables (.env File)

### Minimal Cloud Setup
```env
deployment_name=gpt-4o-deployment
model_name=gpt-4o
azure_endpoint=https://my-resource.openai.azure.com/
openai_api_key=your-key-here
openai_api_version=2024-05-01
embedding_deployment_name=text-embedding-3-large-deployment
embedding_model_name=text-embedding-3-large
embedding_azure_endpoint=https://my-resource.openai.azure.com/
embedding_openai_api_key=your-key-here
embedding_openai_api_version=2024-05-01
```

### Minimal Open-Source Setup
```env
# Leave everything empty
# Or comment out all lines
# Just make sure Ollama is running on localhost:11434
```

### Hybrid Setup (Recommended)
```env
# Same as Cloud Setup above
# Qdrant uses local ./data/qdrant_db/ automatically
# (Can skip Tavily and ElevenLabs for cost savings)
```

---

## 🚀 Step-by-Step Execution

### Step 1: Prerequisites
```bash
# Check Python version (needs 3.11+)
python3 --version

# Check git (to clone if needed)
git --version

# On M1/M2 Mac: Check architecture
uname -m  # Should show: arm64
```

### Step 2: Get This Project
```bash
# Clone if you don't have it
git clone https://github.com/souvikmajumder26/Multi-Agent-Medical-Assistant.git
cd Multi-Agent-Medical-Assistant
```

### Step 3: Run Interactive Setup
```bash
# Make setup script executable
chmod +x setup.sh

# Run it (choose 1, 2, or 3)
./setup.sh
```

The script will:
1. Check Python version ✅
2. Create virtual environment ✅
3. Install dependencies ✅
4. Ask which setup you want ✅
5. Create .env file with your choices ✅
6. Create project directories ✅
7. Test your configuration ✅

### Step 4: Start Services
```bash
# For Cloud Setup: Just start the app
python app.py

# For Open-Source Setup: Need 2 terminals
# Terminal 1:
ollama serve

# Terminal 2:
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py

# For Hybrid: Same as Cloud
python app.py
```

### Step 5: Ingest Medical Documents (Optional but Recommended)
```bash
# Copy PDFs to data/raw/
mkdir -p data/raw
# Copy your .pdf files there

# Ingest them
python ingest_rag_data.py --input data/raw/

# Wait for completion, then documents are searchable
```

### Step 6: Test in Browser
```
http://localhost:8000
```

---

## ✅ Verification Checklist

After setup, verify everything works:

```bash
# Test 1: Python and venv
source venv/bin/activate
python --version

# Test 2: LLM connection (included in setup.sh, but can repeat)
python -c "from config import Config; c = Config(); print(c.agent_decision.llm.invoke('Hi'))"

# Test 3: Vector database
python -c "from agents.rag_agent import MedicalRAG; from config import Config; MedicalRAG(Config())"

# Test 4: Server starts
python app.py
# Open http://localhost:8000 in browser

# Test 5: API call
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is diabetes?", "conversation_history": []}'
```

---

## 🆘 Troubleshooting

### "Azure API key invalid"
```
✅ Solution: Copy key again from Azure Portal
✅ Check: No extra spaces in .env file
✅ Try: Delete .env and run setup.sh again
```

### "Ollama: Connection refused"
```
✅ Make sure Ollama is running: ollama serve
✅ Check it's accessible: curl http://localhost:11434
✅ Try: Restart Ollama
```

### "Out of memory"
```
❌ If using Ollama:
  ✅ Use smaller model: ollama pull neural-chat
  ✅ Or use Cloud (Azure OpenAI)
  ✅ Or upgrade your GPU (need 8GB+ for Mistral)
```

### "Very slow (30+ seconds per query)"
```
⚠️  Normal for CPU inference
✅ Solutions:
  1. Use GPU (NVIDIA RTX 3080+)
  2. Use Cloud (Azure - instant)
  3. Reduce context window in config.py
```

### "PDF ingestion fails"
```
✅ Check: PDFs are in ./data/raw/
✅ Check: PDFs are valid (not corrupted)
✅ Try: Start with a small test PDF
✅ See: SETUP_GUIDE.md -> Document Ingestion section
```

---

## 📚 Files & Their Purposes

### Documentation
| File | Read When | Why |
|------|-----------|-----|
| `README.md` | First time setup | Overview of project |
| **API_REQUIREMENTS.md** | Choosing setup | Quick reference for APIs |
| **SETUP_GUIDE.md** | Detailed questions | Complete guide with all options |
| **copilot-instructions.md** | Contributing code | Architecture for developers |

### Configuration
| File | Edit When | For What |
|------|-----------|----------|
| **.env** | Setup | Your API keys (created by setup.sh) |
| **.env.example** | Reference | Template showing all options |
| `config.py` | Open-Source setup | Modify to use Ollama instead of Azure |
| `requirements.txt` | Dependency issues | Lists all Python packages |
| **requirements-alternatives.txt** | Using alternatives | Optional open-source packages |

### Execution
| File | Run When | What It Does |
|------|----------|-------------|
| **setup.sh** | Initial setup | Interactive setup wizard |
| `app.py` | Running | Starts the FastAPI server |
| `ingest_rag_data.py` | After setup | Ingest medical documents |

---

## 🎓 Learning Resources

After setup works, learn more:

1. **API Architecture**: See `copilot-instructions.md`
2. **Setup Details**: See `SETUP_GUIDE.md`
3. **Cost Analysis**: See `API_REQUIREMENTS.md`
4. **Original Project**: See `README.md`
5. **Code Details**: See `agents/README.md`

---

## 🤝 Getting Help

### If Setup Fails
1. Read the error message carefully
2. Check `API_REQUIREMENTS.md` troubleshooting
3. Check `SETUP_GUIDE.md` for your specific setup
4. Run setup.sh again with different choices

### If API Calls Fail
1. Verify .env file has correct keys
2. Test API keys independently:
   - Azure: Try in Azure Portal
   - Ollama: Run `curl http://localhost:11434`
   - Tavily: Check API dashboard

### If Performance is Slow
1. Check which component is slow (LLM, DB, or API)
2. Use cloud (faster) vs local (cheaper)
3. See `API_REQUIREMENTS.md` for tradeoffs

---

## ⚡ Next Steps

1. **Read:** `API_REQUIREMENTS.md` (5 min read)
2. **Choose:** Cloud vs Open-Source vs Hybrid
3. **Run:** `./setup.sh` (automated in ~5 min)
4. **Test:** `python app.py` and open browser
5. **Enjoy:** Chat with medical assistant! 🎉

---

## 📞 Support Links

- **Azure OpenAI**: https://azure.microsoft.com/en-us/products/ai-services/openai-service/
- **Ollama**: https://ollama.ai/
- **Tavily**: https://tavily.com/
- **ElevenLabs**: https://elevenlabs.io/
- **Qdrant**: https://qdrant.tech/
- **Project**: https://github.com/souvikmajumder26/Multi-Agent-Medical-Assistant

---

## 🎯 Choose Your Path Now

- **Production ready?** → Path 1 (Cloud)
- **Learning locally?** → Path 2 (Open-Source)
- **Best of both?** → Path 3 (Hybrid)

Then run: `./setup.sh`

**You're all set! 🚀**
