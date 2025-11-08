# ⚡ Quick Reference: Setup Checklist & Command Guide

## 🎯 Before You Start - Pre-Flight Checklist

### System Requirements
- [ ] **Python 3.11+** installed: `python3 --version`
- [ ] **Git** installed (if cloning): `git --version`
- [ ] **10GB+ free disk space**: `df -h`
- [ ] **Stable internet connection** (required for setup)
- [ ] **RAM**: 4GB minimum (8GB+ recommended)

### Choose Your Path
- [ ] **Path 1 (Cloud)**: Have Azure OpenAI account ready
- [ ] **Path 2 (Open-Source)**: Have 8GB+ RAM, 16GB+ VRAM for GPU (optional but recommended)
- [ ] **Path 3 (Hybrid)**: Have Azure OpenAI account ready

---

## 🚀 Quick Setup Commands

### One-Line Setup (All 3 Paths)
```bash
# Clone, setup, and run all at once
git clone https://github.com/souvikmajumder26/Multi-Agent-Medical-Assistant.git && \
cd Multi-Agent-Medical-Assistant && \
chmod +x setup.sh && \
./setup.sh
```

### Step-by-Step Commands

**Step 1: Clone Repository**
```bash
git clone https://github.com/souvikmajumder26/Multi-Agent-Medical-Assistant.git
cd Multi-Agent-Medical-Assistant
```

**Step 2: Run Setup (Choose ONE)**
```bash
# Make executable first
chmod +x setup.sh

# Then run (interactive - choose 1, 2, or 3)
./setup.sh
```

**Step 3: Start Services (Based on Your Choice)**
```bash
# For Cloud or Hybrid: Just start server
python app.py

# For Open-Source: Start 2 services
# Terminal 1:
ollama serve

# Terminal 2:
source venv/bin/activate
python app.py
```

**Step 4: Access**
```
Open browser: http://localhost:8000
```

---

## 📋 API Requirements by Path

### Path 1: Cloud (Azure OpenAI) ☁️

**Get These from Azure Portal:**
```
deployment_name        = gpt-4o-deployment
model_name            = gpt-4o
azure_endpoint        = https://YOUR-RESOURCE.openai.azure.com/
openai_api_key        = Your-API-Key-Here
openai_api_version    = 2024-05-01
embedding_deployment  = text-embedding-3-large-deployment
embedding_model       = text-embedding-3-large
```

**Sign up:**
https://azure.microsoft.com/en-us/products/ai-services/openai-service/

**Cost:** $0.01-0.10 per query (varies by model size)

---

### Path 2: Open-Source (Ollama) 🖥️

**Install Ollama:**
```bash
# Download from https://ollama.ai
# Then in terminal:
ollama serve              # Terminal 1
ollama pull mistral       # Terminal 2
```

**Cost:** $0 (free! only electricity)

**Required hardware:**
- CPU: Any modern processor
- RAM: 8GB+ (16GB recommended)
- GPU: Optional (16GB+ VRAM for Mistral/Llama2)

---

### Path 3: Hybrid (Azure LLM + Local DB) 🔀

**Same as Path 1** (Azure credentials needed)
**Vector DB** uses local Qdrant (automatic, no setup)

**Cost:** $0.01-0.10 per query (LLM only, DB is free)

---

## 🔐 Complete .env Template

Create `.env` file with minimum required:

### Cloud Setup
```env
# Required
deployment_name=gpt-4o-deployment
model_name=gpt-4o
azure_endpoint=https://your-resource.openai.azure.com/
openai_api_key=YOUR-KEY
openai_api_version=2024-05-01
embedding_deployment_name=text-embedding-3-large-deployment
embedding_model_name=text-embedding-3-large
embedding_azure_endpoint=https://your-resource.openai.azure.com/
embedding_openai_api_key=YOUR-KEY
embedding_openai_api_version=2024-05-01

# Optional
TAVILY_API_KEY=
ELEVEN_LABS_API_KEY=
```

### Open-Source Setup
```env
# Leave empty or comment out
# Just make sure: ollama serve is running
```

---

## ✅ Verification Tests

### Test 1: Python Environment
```bash
python3 --version              # Should be 3.11+
source venv/bin/activate       # Activate venv
which python                   # Should show venv path
```

### Test 2: LLM Connection
```bash
python << 'EOF'
from config import Config
from dotenv import load_dotenv
load_dotenv()

config = Config()
response = config.agent_decision.llm.invoke("Say hello")
print("✅ LLM works!" if response else "❌ LLM failed")
EOF
```

### Test 3: Vector Database
```bash
python << 'EOF'
from agents.rag_agent import MedicalRAG
from config import Config

config = Config()
rag = MedicalRAG(config)
print("✅ Vector DB works!")
EOF
```

### Test 4: API Server
```bash
python app.py
# Then in browser: http://localhost:8000
# Should see web interface
```

### Test 5: Query API
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is diabetes?", "conversation_history": []}'
```

---

## 🐛 Troubleshooting Quick Reference

| Problem | Cause | Solution |
|---------|-------|----------|
| "Azure key invalid" | Wrong credentials | Copy again from Azure Portal |
| "Ollama: Connection refused" | Ollama not running | Run: `ollama serve` |
| "ModuleNotFoundError: No module" | Dependencies missing | Run: `pip install -r requirements.txt` |
| "CUDA out of memory" | GPU too small | Use smaller model or cloud |
| "Very slow (30+ sec)" | CPU inference | Use GPU or cloud |
| "PDF ingestion fails" | Bad file format | Check PDFs are valid |
| ".env not found" | Config missing | Run: `cp .env.example .env` |

---

## 📊 Cost Calculator

### Monthly Usage Estimates

**Cloud Setup (1000 queries/month):**
```
LLM calls:        1000 queries × $0.010 = $10
Embeddings:       1000 queries × $0.005 = $5
APIs (optional):  100 web searches × $0.01 = $1
Total:                                      $16/month
```

**Open-Source Setup:**
```
LLM:              $0 (local)
Embeddings:       $0 (local)
APIs:             $0 (optional DuckDuckGo)
Total:                                      $0/month
```

**Hybrid Setup (1000 queries/month):**
```
LLM calls:        1000 × $0.010 = $10
Embeddings:       1000 × $0.005 = $5
Vector DB:        Local (free)
APIs:             Disabled
Total:                                      $15/month
```

---

## 📚 Documentation Files - What Each Does

| File | Purpose | Read Time | Best For |
|------|---------|-----------|----------|
| **GETTING_STARTED.md** | Overview of all 3 paths | 10 min | First-time users |
| **API_REQUIREMENTS.md** | API keys explained | 5 min | Quick reference |
| **SETUP_GUIDE.md** | Detailed setup options | 20 min | In-depth learning |
| **DOCUMENTATION_INDEX.md** | Navigation guide | 5 min | Finding things |
| **.env.example** | Configuration template | 2 min | Setting up .env |
| **setup.sh** | Interactive setup | 5 min | Automated setup |
| **copilot-instructions.md** | For developers | 10 min | Code contributions |

---

## 🎓 Learning Path

### Week 1: Get It Running
- [ ] Read GETTING_STARTED.md (10 min)
- [ ] Choose your path (2 min)
- [ ] Run setup.sh (5 min)
- [ ] Test basic query (5 min)
- [ ] Ingest sample documents (10 min)

### Week 2: Understand It
- [ ] Read copilot-instructions.md (10 min)
- [ ] Review agents/README.md (15 min)
- [ ] Check key files mentioned (20 min)
- [ ] Test different query types (20 min)

### Week 3: Customize It
- [ ] Modify config.py settings (15 min)
- [ ] Adjust LLM temperature (10 min)
- [ ] Ingest custom documents (30 min)
- [ ] Test custom RAG queries (20 min)

### Week 4: Deploy It
- [ ] Read SETUP_GUIDE.md Docker section (15 min)
- [ ] Build Docker image (10 min)
- [ ] Set up for production (30 min)
- [ ] Monitor costs/performance (20 min)

---

## 🔗 Important Links

### Signup / Get Keys
- Azure OpenAI: https://portal.azure.com/
- Tavily API: https://tavily.com/
- ElevenLabs: https://elevenlabs.io/
- Qdrant Cloud: https://cloud.qdrant.io/

### Software to Download
- Ollama: https://ollama.ai/
- Python 3.11: https://www.python.org/downloads/
- Git: https://git-scm.com/

### Project Resources
- GitHub: https://github.com/souvikmajumder26/Multi-Agent-Medical-Assistant
- Issues: https://github.com/souvikmajumder26/Multi-Agent-Medical-Assistant/issues
- Discussions: https://github.com/souvikmajumder26/Multi-Agent-Medical-Assistant/discussions

### Technical Docs
- LangChain: https://python.langchain.com/
- FastAPI: https://fastapi.tiangolo.com/
- Qdrant: https://qdrant.tech/

---

## ⏱️ Time Estimates

| Task | Time | Difficulty |
|------|------|-----------|
| Read documentation | 10-30 min | Easy |
| Run setup.sh | 5-10 min | Easy |
| Get API keys | 10-20 min | Medium |
| Start server | 2-5 min | Easy |
| Test basic query | 2-5 min | Easy |
| Ingest documents | 10-30 min | Medium |
| Full setup complete | **30-90 min** | **Easy** |

---

## 🚨 Emergency Troubleshooting

### Everything Fails - Start Over
```bash
# Remove old setup
rm -rf venv .env data/qdrant_db

# Start fresh
./setup.sh

# Choose the same option again
# This time it should work!
```

### Can't Find Your API Key
```bash
# For Azure:
1. Go to https://portal.azure.com/
2. Search "OpenAI" in search bar
3. Click your resource
4. Left sidebar: "Keys and Endpoint"
5. Copy "Key 1" and "Endpoint"
```

### Ollama Won't Connect
```bash
# Test if it's running
curl http://localhost:11434

# If not, start it
ollama serve

# In another terminal, download model
ollama pull mistral

# Or use a smaller model
ollama pull neural-chat
```

### Virtual Environment Issues
```bash
# Recreate venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 💡 Pro Tips

1. **Start with Hybrid Setup** (Path 3)
   - Fast performance (Cloud LLM)
   - Low cost ($15/mo vs $16/mo for full cloud)
   - Easy to manage

2. **Use Open-Source for Development** (Path 2)
   - Free to experiment
   - No API cost concerns
   - Good for testing

3. **Save API Keys** in password manager
   - Don't commit .env to git
   - Use environment variables in production
   - Rotate keys regularly

4. **Monitor Your Costs**
   - Check Azure dashboard weekly
   - Set up billing alerts
   - Track query volume

5. **Backup Your Data**
   - Save .env file securely
   - Backup ingested documents
   - Keep Qdrant collection backups

---

## ✨ Final Checklist

Before you're done:
- [ ] .env file created with correct keys
- [ ] setup.sh ran successfully
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] LLM connection test passed
- [ ] Server starts without errors
- [ ] Web interface loads in browser
- [ ] Can submit a query and get response
- [ ] (Optional) Documents ingested successfully

**All checked?** You're ready to use the system! 🎉

---

## 🆘 Still Need Help?

1. **Read relevant docs** (see documentation index)
2. **Check troubleshooting sections** in each doc
3. **Run setup.sh again** with different options
4. **Check GitHub issues** for similar problems
5. **Test each component** individually (see tests above)

**Remember:** Most issues are solved by running `./setup.sh` again!

---

**Last Updated:** November 9, 2025
**Version:** 2.1+
**Status:** Production Ready ✅
