# Gemini Setup Guide - No Azure, Open-Source Only

## 🚀 Gemini + Open-Source Setup (FREE/Cheap Alternative)

### What You'll Use:
- **LLM:** Google Gemini API (Free tier available!)
- **Embeddings:** sentence-transformers (local, free)
- **Vector DB:** Qdrant (local, free)
- **Web Search:** LangChain built-in tools (open-source)
- **Speech:** pyttsx3 (free, local)

---

## Step 1: Get Your Gemini API Key

### Get API Key:
1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy your API key
4. Save it somewhere safe

Your key: `PASTE-YOUR-GEMINI-API-KEY-HERE`

---

## Step 2: Install Dependencies

```bash
# In your project directory with venv activated
pip install google-generativeai==0.3.0
pip install sentence-transformers==2.2.2
pip install langchain-google-genai==0.0.10
```

---

## Step 3: Create .env File

Create `.env` in project root:

```env
# Google Gemini API
GOOGLE_API_KEY=your-gemini-api-key-here

# Vector Database (local)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# LLM Model
GEMINI_MODEL=gemini-pro
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

---

## Step 4: Modify config.py

Replace Azure OpenAI with Gemini:

```python
# OLD (Azure OpenAI)
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI

# NEW (Google Gemini)
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

class AgentDecisionConfig:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1
        )

class ConversationConfig:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7
        )

class WebSearchConfig:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.3
        )
        self.context_limit = 20

class RAGConfig:
    def __init__(self):
        self.vector_db_type = "qdrant"
        self.embedding_dim = 384  # MiniLM dimension
        self.distance_metric = "Cosine"
        self.use_local = True
        self.vector_local_path = "./data/qdrant_db"
        self.doc_local_path = "./data/docs_db"
        self.parsed_content_dir = "./data/parsed_docs"
        
        # Use local Qdrant
        self.url = os.getenv("QDRANT_HOST", "localhost")
        self.port = int(os.getenv("QDRANT_PORT", "6333"))
        self.api_key = None  # No auth for local
        self.collection_name = "medical_assistance_rag"
        
        # Embeddings - Use sentence-transformers (local)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # LLM for response generation
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.3
        )
        
        # Other LLMs
        self.summarizer_model = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.5
        )
        
        self.chunker_model = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.0
        )
        
        self.chunk_size = 512
        self.chunk_overlap = 50
        self.min_retrieval_confidence = 0.40
```

---

## Step 5: Update RAG Agent for Local Embeddings

File: `agents/rag_agent/__init__.py`

Change embeddings usage:

```python
# OLD
embeddings = config.rag.embedding_model.embed_query(text)

# NEW
embeddings = config.rag.embedding_model.encode(text)
```

---

## Step 6: Start Qdrant Locally (Docker)

```bash
# Option 1: Using Docker (easiest)
docker run -p 6333:6333 qdrant/qdrant

# Option 2: Using Qdrant CLI (if installed)
qdrant

# Option 3: Skip if already running
```

Qdrant will run on: `http://localhost:6333`

---

## Step 7: Run Setup

```bash
chmod +x setup.sh
./setup.sh
# When prompted, choose the Gemini option (if available)
```

---

## Step 8: Start the Application

```bash
python app.py
```

Open: `http://localhost:8000`

---

## ✅ Checklist

- [ ] Gemini API key obtained
- [ ] .env file created with GOOGLE_API_KEY
- [ ] Dependencies installed (google-generativeai, sentence-transformers)
- [ ] config.py modified for Gemini
- [ ] Qdrant running on localhost:6333
- [ ] Application starts without errors
- [ ] Can submit queries in browser

---

## 🔗 Resources

- Gemini API: https://makersuite.google.com/app/apikey
- Sentence Transformers: https://huggingface.co/sentence-transformers
- Qdrant: https://qdrant.tech/
- Docker: https://www.docker.com/

---

## 💡 Next Steps

1. Set up dependencies
2. Create .env file with API key
3. Modify config.py
4. Start Qdrant
5. Run app
6. Test queries

All open-source, no Azure charges! ✅
