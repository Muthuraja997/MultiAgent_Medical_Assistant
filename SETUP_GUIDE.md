# Setup Guide: Multi-Agent Medical Assistant

## 📋 API Requirements & Open-Source Alternatives

### Summary of All Requirements

| Component | Purpose | Cloud API | Open-Source Alternative | Status |
|-----------|---------|-----------|------------------------|--------|
| **LLM** | Query routing, responses, chunking | ✅ Azure OpenAI | ✅ Ollama / LM Studio | Recommended |
| **Embeddings** | Vector embeddings for RAG | ✅ Azure OpenAI | ✅ sentence-transformers (local) | Recommended |
| **Vector DB** | Document storage & retrieval | ⚠️ Qdrant Cloud | ✅ Qdrant Local | Already Supported |
| **Web Search** | PubMed + Medical research | ✅ Tavily API | ✅ DuckDuckGo / Free web search | Alternative |
| **Speech-to-Text** | Audio transcription | ✅ ElevenLabs | ✅ Vosk / Whisper | Alternative |
| **Text-to-Speech** | Audio generation | ✅ ElevenLabs | ✅ pyttsx3 / Festival | Alternative |
| **Vision Models** | Chest X-ray, skin lesion, brain tumor | ✅ Azure OpenAI | ✅ Local PyTorch models | Already Included |

---

## 🔧 Installation & Setup

### Step 1: Clone Repository & Install Dependencies

```bash
# Clone the repository
git clone https://github.com/Muthuraja997/Multi-Agent-Medical-Assistant.git
cd Multi-Agent-Medical-Assistant

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Create Environment Configuration File

Create a `.env` file in the project root:

```bash
cp README.md .env  # Copy structure from README
```

---

## 🎯 Configuration Options

### Option A: Cloud-Based Setup (Azure OpenAI) - Full Features

**Best for:** Production, team projects, maximum accuracy

**Required API Keys:**
```env
# Azure OpenAI LLM Configuration
deployment_name=gpt-4o-deployment
model_name=gpt-4o
azure_endpoint=https://your-resource.openai.azure.com/
openai_api_key=your-azure-openai-api-key
openai_api_version=2024-05-01

# Azure OpenAI Embeddings Configuration
embedding_deployment_name=text-embedding-3-large-deployment
embedding_model_name=text-embedding-3-large
embedding_azure_endpoint=https://your-resource.openai.azure.com/
embedding_openai_api_key=your-embedding-api-key
embedding_openai_api_version=2024-05-01

# Web Search (Optional)
TAVILY_API_KEY=your-tavily-api-key

# Speech Processing (Optional)
ELEVEN_LABS_API_KEY=your-elevenlabs-api-key

# Qdrant Vector Database (Optional, defaults to local)
# QDRANT_URL=http://qdrant-cloud-url:6333
# QDRANT_API_KEY=your-qdrant-api-key
```

**Sign Up Links:**
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service/)
- [Tavily API](https://tavily.com/)
- [ElevenLabs](https://elevenlabs.io/)

---

### Option B: Fully Open-Source Setup (Recommended for Local Development)

**Best for:** Local development, testing, no cloud costs

#### Step 1: Setup Local LLM with Ollama

```bash
# Download and install Ollama
# macOS: https://ollama.ai
# Linux: curl https://ollama.ai/install.sh | sh
# Windows: https://ollama.ai/download

# Pull a medical-suitable model
ollama pull mistral          # Fast, lightweight (7B)
# OR
ollama pull neural-chat      # More specialized (7B)
# OR
ollama pull llama2           # More powerful (13B, requires 8GB RAM)

# Start Ollama server (runs on http://localhost:11434)
ollama serve
```

#### Step 2: Setup Local Embeddings with FastEmbed

The project already includes `fastembed` in requirements. No additional setup needed.

#### Step 3: Configure `.env` for Open-Source

```env
# Local LLM via Ollama
# Note: Modify config.py to use LangChain's Ollama integration instead of Azure OpenAI
# See "Modifying config.py" section below

# Vector Database - Local Qdrant (default, no setup needed)
# Uses ./data/qdrant_db/ directory locally

# Optional: Web Search (using free APIs)
# Comment out TAVILY_API_KEY - uses DuckDuckGo instead

# Optional: Speech (using local open-source alternatives)
# Comment out ELEVEN_LABS_API_KEY - will use pyttsx3 for TTS
```

#### Step 4: Modify `config.py` for Ollama

Replace Azure OpenAI imports with Ollama:

**In `config.py`, line 6-7, change from:**
```python
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
```

**To:**
```python
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
```

**Then replace LLM initializations in config classes:**

```python
# Example for AgentDecisoinConfig (line ~18)
class AgentDecisoinConfig:
    def __init__(self):
        # Using Ollama instead of Azure OpenAI
        self.llm = OllamaLLM(
            model="mistral",
            base_url="http://localhost:11434",
            temperature=0.1
        )

# Repeat for other config classes:
# - ConversationConfig
# - WebSearchConfig
# - RAGConfig.llm
# - RAGConfig.summarizer_model
# - RAGConfig.chunker_model
# - MedicalCVConfig.llm
```

**For embeddings in RAGConfig (line ~75):**

```python
class RAGConfig:
    def __init__(self):
        # ... other settings ...
        # Using local embeddings instead of Azure
        self.embedding_model = OllamaEmbeddings(
            model="mistral",  # or use nomic-embed-text for embeddings
            base_url="http://localhost:11434"
        )
```

---

### Option C: Hybrid Setup (Cloud LLM + Local Vector DB)

**Best for:** Balance of cost and convenience

```env
# Use Azure OpenAI for LLM (expensive calls for large models)
deployment_name=gpt-4o-deployment
model_name=gpt-4o
azure_endpoint=https://your-resource.openai.azure.com/
openai_api_key=your-azure-openai-api-key
openai_api_version=2024-05-01

# Use Azure for embeddings (pre-compute once, then local Qdrant)
embedding_deployment_name=text-embedding-3-large-deployment
embedding_model_name=text-embedding-3-large
embedding_azure_endpoint=https://your-resource.openai.azure.com/
embedding_openai_api_key=your-embedding-api-key
embedding_openai_api_version=2024-05-01

# Local Qdrant (no keys needed)
# Just uses ./data/qdrant_db/

# Skip cloud APIs for optional features
# TAVILY_API_KEY=          # (optional, skip for local search)
# ELEVEN_LABS_API_KEY=     # (optional, skip for local TTS)
```

---

## 🚀 Running the Project

### Setup Step 1: Download Medical Models (Optional but Recommended)

The vision models are already in the codebase:
```bash
# These are automatically loaded by the project:
# - agents/image_analysis_agent/chest_xray_agent/models/covid_chest_xray_model.pth
# - agents/image_analysis_agent/skin_lesion_agent/models/checkpointN25_.pth.tar
# - agents/image_analysis_agent/brain_tumor_agent/models/brain_tumor_segmentation.pth
```

### Setup Step 2: Ingest Medical Documents (Required for RAG)

```bash
# Copy medical PDFs to a directory
mkdir -p data/raw
# Place your medical PDFs in data/raw/

# Ingest documents (uses Docling for parsing)
python ingest_rag_data.py --input data/raw/

# Output: Parsed documents in data/parsed_docs/, indexed in data/qdrant_db/
```

### Setup Step 3: Start the Server

#### For Cloud Setup (Azure OpenAI):
```bash
python app.py
# Or with uvicorn:
uvicorn app:app --reload --port 8000
```

#### For Open-Source Setup (Ollama):
```bash
# Terminal 1: Start Ollama server
ollama serve

# Terminal 2: Start FastAPI app
python app.py
# Or with uvicorn:
uvicorn app:app --reload --port 8000
```

### Step 4: Access the Web Interface

Open browser to: `http://localhost:8000`

---

## 📊 Comparison Table: Which Setup to Use?

| Criteria | Cloud | Open-Source | Hybrid |
|----------|-------|------------|--------|
| **Cost** | $$$ (per API call) | $ (local compute) | $$ (balanced) |
| **Accuracy** | Highest (GPT-4o) | Good (Mistral 7B) | High (GPT-4o LLM) |
| **Speed** | Depends on API | Depends on GPU | Fast (local DB) |
| **Setup Time** | 10 mins | 20 mins (Ollama) | 15 mins |
| **Internet Required** | Yes | No (after setup) | Partial |
| **GPU Required** | No | Yes (recommended) | Optional |
| **Production Ready** | ✅ Yes | ⚠️ Testing | ✅ Yes |
| **Recommended For** | Teams, Production | Local Dev, Testing | Most Users |

---

## 🔗 Web Search Agent: Open-Source Alternative

### Using DuckDuckGo Instead of Tavily

Edit `agents/web_search_processor_agent/tavily_search.py`:

```python
# Install: pip install duckduckgo-search
from duckduckgo_search import DDGS

class TavilySearchAgent:
    def __init__(self):
        pass
    
    def search_tavily(self, query: str) -> str:
        """Use DuckDuckGo instead of Tavily API."""
        try:
            ddgs = DDGS()
            results = ddgs.text(query, max_results=5)
            
            if results:
                return "\n".join([
                    f"title: {res['title']} - url: {res['href']} - content: {res['body']}"
                    for res in results
                ])
            return "No relevant results found."
        except Exception as e:
            return f"Error retrieving results: {e}"
```

**No API key needed** - completely free and open-source!

---

## 🎤 Speech Processing: Open-Source Alternatives

### Text-to-Speech (pyttsx3)

Edit `app.py`, replace ElevenLabs with pyttsx3:

```python
# Install: pip install pyttsx3
import pyttsx3
import io

# In speech endpoint (around line 329)
def tts_local(text: str) -> bytes:
    """Generate speech locally using pyttsx3"""
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    
    audio_path = f"uploads/speech/{uuid.uuid4()}.wav"
    engine.save_to_file(text, audio_path)
    engine.runAndWait()
    
    with open(audio_path, 'rb') as f:
        return f.read()
```

### Speech-to-Text (Vosk or Whisper)

```bash
# Option 1: Vosk (lightweight, offline)
pip install vosk pysounddevice

# Option 2: Whisper (better accuracy)
pip install openai-whisper
```

---

## ⚠️ Important Notes

### Memory & GPU Requirements

| Component | Cloud | Open-Source |
|-----------|-------|------------|
| **RAM** | 4GB | 8GB+ |
| **GPU** | Not needed | Recommended (16GB VRAM for Mistral) |
| **Storage** | 10GB | 20GB (models + data) |

### Known Limitations with Open-Source

1. **Accuracy**: Mistral 7B is good but not GPT-4o level for medical reasoning
2. **Speed**: First inference is slow (~3-5 seconds on CPU)
3. **Context Window**: Mistral has 32K tokens vs GPT-4 128K tokens
4. **Multi-GPU**: Setup more complex for distributed inference

### Recommended: Use GPU-Accelerated Setup

```bash
# For NVIDIA GPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For Metal (macOS)
pip install torch torchvision torchaudio

# Test GPU
python -c "import torch; print(torch.cuda.is_available())"
```

---

## 🧪 Testing Your Setup

### Test LLM Connection

```python
# Save as test_llm.py
from config import Config

config = Config()
try:
    response = config.agent_decision.llm.invoke("What is medical AI?")
    print("✅ LLM is working:", response)
except Exception as e:
    print("❌ LLM error:", e)
```

### Test Vector Database

```python
# Save as test_qdrant.py
from agents.rag_agent import MedicalRAG
from config import Config

config = Config()
rag = MedicalRAG(config)

# Try to ingest a test document
result = rag.ingest_file("path/to/test.pdf")
print("✅ Qdrant working:", result)
```

### Test Embeddings

```python
# Save as test_embeddings.py
from config import Config

config = Config()
try:
    embeddings = config.rag.embedding_model.embed_query("medical test")
    print("✅ Embeddings working, dimension:", len(embeddings))
except Exception as e:
    print("❌ Embeddings error:", e)
```

### Run All Tests

```bash
python test_llm.py
python test_qdrant.py
python test_embeddings.py
```

---

## 📝 Troubleshooting

### "CUDA out of memory" Error
→ Reduce model size: use `neural-chat` instead of `llama2`
→ Or add `max_tokens=512` to reduce output length

### "Connection refused" to Ollama
→ Make sure Ollama is running: `ollama serve`
→ Check it's on `localhost:11434`: `curl http://localhost:11434`

### Tavily API not working
→ Use DuckDuckGo instead (see Web Search section)
→ Or comment out web search in decision prompt

### ElevenLabs key invalid
→ Use pyttsx3 instead (see Speech Processing section)
→ Or comment out speech features in `app.py`

### First request is very slow (30+ seconds)
→ Normal for local inference, subsequent requests are faster
→ Consider using cloud LLM if latency is critical
→ Or upgrade GPU/RAM

---

## 🎓 Next Steps

1. **Choose your setup**: Cloud, Open-Source, or Hybrid
2. **Create `.env` file** with appropriate keys
3. **Modify `config.py`** if using Ollama
4. **Ingest medical documents**: `python ingest_rag_data.py`
5. **Start server**: `python app.py`
6. **Test in browser**: `http://localhost:8000`

---

## 📚 References

- **Ollama**: https://ollama.ai/
- **Mistral Model**: https://mistral.ai/
- **FastEmbed**: https://github.com/qdrant/fastembed
- **LangChain**: https://python.langchain.com/
- **Qdrant**: https://qdrant.tech/
- **DuckDuckGo**: https://duckduckgo.com/
- **pyttsx3**: https://pypi.org/project/pyttsx3/

---

## ✅ Verification Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] `.env` file created with required keys
- [ ] LLM service running (Azure OpenAI or Ollama)
- [ ] Medical documents ingested
- [ ] Vector DB populated with embeddings
- [ ] FastAPI server started on port 8000
- [ ] Web interface accessible at `http://localhost:8000`
- [ ] Can submit text query and get response
- [ ] Can upload medical image (optional)

**All checked? You're ready to go! 🚀**
