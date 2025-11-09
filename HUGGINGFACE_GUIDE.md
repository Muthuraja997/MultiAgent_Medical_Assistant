# HuggingFace Free Models Guide

## Overview

This project uses HuggingFace models for embeddings, reranking, and other NLP tasks. All models used are **free and open-source** - no subscription required!

## Current Free Models in Use

### 1. **Sentence Transformers - Embeddings** ✅ FREE
- **Model**: `all-MiniLM-L6-v2`
- **Purpose**: Generate 384-dimensional embeddings for RAG
- **Size**: ~22 MB
- **License**: Apache 2.0 (Open Source)
- **Cost**: FREE
- **Location**: Used in `agents/rag_agent/embeddings_wrapper.py`

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
```

### 2. **Cross-Encoder - Reranking** ✅ FREE
- **Model**: `cross-encoder/ms-marco-TinyBERT-L-6`
- **Purpose**: Rerank retrieved documents for better relevance
- **Size**: ~22 MB
- **License**: Apache 2.0 (Open Source)
- **Cost**: FREE
- **Location**: Used in `agents/rag_agent/reranker.py`

```python
from sentence_transformers import CrossEncoder
model = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-6')
```

### 3. **FastEmbed - Sparse Embeddings (BM25)** ✅ FREE
- **Model**: `Qdrant/bm25`
- **Purpose**: Sparse embedding for hybrid search
- **Size**: Minimal (~1 MB)
- **License**: Open Source
- **Cost**: FREE
- **Location**: Used in `agents/rag_agent/vectorstore_qdrant.py`

```python
from langchain_qdrant import FastEmbedSparse
sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
```

---

## Available Free Alternatives

### **Embedding Models** (Swap in `config.py`)

| Model | Dimensions | Size | Speed | Quality | Cost |
|-------|-----------|------|-------|---------|------|
| `all-MiniLM-L6-v2` | 384 | 22 MB | Fast | Good | FREE ✅ |
| `all-mpnet-base-v2` | 768 | 438 MB | Medium | Excellent | FREE ✅ |
| `distiluse-base-multilingual-cased-v2` | 512 | 134 MB | Fast | Good | FREE ✅ |
| `sentence-t5-base` | 768 | 223 MB | Medium | Good | FREE ✅ |

**Change in `config.py` line ~108:**
```python
self._embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Change this
```

### **Reranker Models** (Swap in `config.py`)

| Model | Size | Speed | Quality | Cost |
|-------|------|-------|---------|------|
| `cross-encoder/ms-marco-TinyBERT-L-6` | 22 MB | Fast | Good | FREE ✅ |
| `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` | 117 MB | Medium | Excellent | FREE ✅ |
| `cross-encoder/qnli-distilroberta-base` | 250 MB | Medium | Good | FREE ✅ |

**Change in `config.py` line ~118:**
```python
self.reranker_model = "cross-encoder/ms-marco-TinyBERT-L-6"  # Change this
```

---

## How to Use Alternative Models

### Step 1: Identify Your Need
- **Faster Processing**: Use smaller models (TinyBERT, MiniLM)
- **Better Accuracy**: Use larger models (MPNet, RoBERTa)
- **Lower Memory**: Use 384-dim models

### Step 2: Update `config.py`

```python
# For embeddings
self._embedding_model = SentenceTransformer('all-mpnet-base-v2')

# For reranking
self.reranker_model = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
```

### Step 3: First Run
On first run, HuggingFace will:
1. Download the model (~50-500 MB depending on choice)
2. Cache it locally in `~/.cache/huggingface/`
3. Use it for subsequent runs (no re-download)

### Step 4: Verify Setup

```bash
# Test if HUGGINGFACE_TOKEN is loaded
python3 -c "from config import Config; c = Config(); print('HF Token:', c.rag.huggingface_token[:20] + '...')"

# Test model loading
python3 -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('all-MiniLM-L6-v2'); print('✅ Model loaded:', m)"
```

---

## Performance Recommendations

### ⚡ **Fastest Setup** (Recommended for Local Dev)
```python
# Use small, fast models
embedding_model = 'all-MiniLM-L6-v2'        # 384-dim, 22 MB
reranker_model = 'cross-encoder/ms-marco-TinyBERT-L-6'  # 22 MB
```
- **Total Size**: ~50 MB
- **Speed**: Very Fast
- **Memory**: ~500 MB
- **Quality**: Good

### 🎯 **Balanced Setup** (Recommended for Production)
```python
embedding_model = 'all-mpnet-base-v2'       # 768-dim, 438 MB
reranker_model = 'cross-encoder/mmarco-mMiniLMv2-L12-H384-v1'  # 117 MB
```
- **Total Size**: ~600 MB
- **Speed**: Medium
- **Memory**: ~2 GB
- **Quality**: Excellent

### 🚀 **Highest Quality Setup** (Recommended for Research)
```python
embedding_model = 'sentence-transformers/all-mpnet-base-v2'  # 768-dim
reranker_model = 'cross-encoder/mmarco-mMiniLMv2-L12-H384-v1'
```
- **Total Size**: ~600 MB
- **Speed**: Medium-Slow
- **Memory**: ~2-3 GB
- **Quality**: Excellent

---

## Cost Analysis

### ✅ Our Current Setup: **100% FREE**

| Component | Model | Cost | License |
|-----------|-------|------|---------|
| Embeddings | all-MiniLM-L6-v2 | FREE | Apache 2.0 |
| Reranking | TinyBERT-L-6 | FREE | Apache 2.0 |
| Sparse Search | BM25 | FREE | Open Source |
| Vector DB | Qdrant (Local) | FREE | AGPL |
| LLM | Google Gemini | FREE (limited) | Google |
| **Total** | - | **FREE** | - |

### Comparison with Alternatives

| Service | Cost | Quality | Privacy |
|---------|------|---------|---------|
| **HuggingFace Models (Local)** | FREE ✅ | Good | Full ✅ |
| OpenAI Embeddings | $0.02/1K tokens | Good | Limited |
| Cohere Embeddings | $0.10/1M tokens | Better | Limited |
| Azure Cognitive Search | $0.10-5/month | Good | Limited |
| Pinecone (Cloud Vector DB) | $12-750/month | Good | Limited |

---

## Troubleshooting

### Issue: "Model not found" or Download Errors

**Solution 1**: Check HuggingFace Token
```bash
python3 -c "import os; print(os.getenv('HUGGINGFACE_TOKEN'))"
```

**Solution 2**: Pre-cache the model
```bash
python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

**Solution 3**: Check internet connection
- Models are downloaded from HuggingFace Hub
- Ensure internet access on first run

### Issue: Out of Memory

**Solution**: Use smaller models
- Switch from `all-mpnet-base-v2` (768-dim) to `all-MiniLM-L6-v2` (384-dim)
- Reduces memory by ~50%

### Issue: Slow Processing

**Solution**: Use GPU acceleration
```bash
# Install GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Or for CPU optimization
pip install fasttext sentence-transformers[sentence-transformers]
```

---

## Recommended Setup

For **this local medical assistant project**, we recommend:

```python
# config.py - RAGConfig class
self.embedding_model = 'all-MiniLM-L6-v2'  # Fast, good quality
self.reranker_model = 'cross-encoder/ms-marco-TinyBERT-L-6'  # Fast reranking
```

**Why?**
- ✅ All FREE models
- ✅ Fast inference on CPU
- ✅ Low memory requirements (~500 MB)
- ✅ Good quality for medical documents
- ✅ Perfect for local development

---

## Resources

- 🤗 **HuggingFace Hub**: https://huggingface.co/models
- 📚 **Sentence Transformers**: https://www.sbert.net/
- 🔍 **Model Leaderboard**: https://huggingface.co/spaces/mteb/leaderboard
- 💾 **Model Cache**: `~/.cache/huggingface/hub/`

---

## Next Steps

1. ✅ HUGGINGFACE_TOKEN is set in `.env`
2. Test the models:
   ```bash
   python3 app.py
   ```
3. (Optional) Swap models in `config.py` if needed
4. Run the RAG pipeline:
   ```bash
   python3 setup_qdrant_local.py
   ```

**All models are FREE and open-source! Enjoy! 🎉**
