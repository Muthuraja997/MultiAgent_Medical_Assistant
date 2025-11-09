# Qdrant Database Connection Guide

## ✅ Connection Status: VERIFIED

Your Qdrant database is successfully running and accessible at **http://localhost:6333**

---

## 📊 Quick Status Check

### Current State
- **Connection**: ✅ Working
- **URL**: http://localhost:6333
- **Collections**: 0 (empty, ready for data)
- **Permissions**: Read/Write ✅
- **Status**: Ready to ingest documents

### Run Anytime
```bash
python3 check_qdrant_connection.py
```

---

## 🔧 Configuration Details

### Connection Settings (from `.env`)
```properties
QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=your-api-key-here  # Not needed for localhost
```

### Project Configuration (from `config.py`)
```python
# RAG Configuration
collection_name = "medical_assistance_rag"
embedding_dim = 384
distance_metric = "Cosine"
vector_search_type = 'hybrid'  # Dense + Sparse (BM25)
top_k = 5
reranker_model = "cross-encoder/ms-marco-TinyBERT-L-6"
```

### Storage Paths
```
Local Vector DB:    ./data/qdrant_db/
Document Store:     ./data/docs_db/
Parsed Content:     ./data/parsed_docs/
Medical PDFs:       ./data/raw/
```

---

## 🚀 Getting Started

### Step 1: Verify Connection (Already Done ✅)
```bash
python3 check_qdrant_connection.py
```
Result: ✅ Connection established

### Step 2: Create Collection & Ingest Documents
```bash
python3 setup_qdrant_local.py
```
This will:
- Create `medical_assistance_rag` collection
- Parse medical PDFs (4 PDFs in `./data/raw/`)
- Generate embeddings (384-dimensional)
- Index documents in Qdrant
- Store document metadata

**Estimated time**: 15-30 minutes (depending on PDF size)

### Step 3: Start the Medical Assistant
```bash
python3 app.py
```
Server will start on: http://localhost:8000

### Step 4: Access the Application
- **Web UI**: http://localhost:8000
- **Qdrant Dashboard**: http://localhost:6333/dashboard

---

## 🔍 Understanding Hybrid Search

Your Qdrant database is configured for **Hybrid Search**:

### Dense Vectors (Vector Search)
- **Model**: all-MiniLM-L6-v2
- **Dimensions**: 384
- **Method**: Cosine similarity
- **Use case**: Semantic understanding

### Sparse Vectors (BM25 Search)
- **Model**: Qdrant/bm25
- **Method**: Keyword matching
- **Use case**: Exact term matching

### Combined Result
1. Dense search finds semantically similar documents
2. Sparse search finds keyword-matching documents
3. Results are ranked and merged
4. Cross-encoder reranking for final sorting

**Benefit**: Better retrieval accuracy combining both approaches

---

## 📝 Available Collections

### Current Collections
```
None yet (database empty)
```

### After Running setup_qdrant_local.py
```
medical_assistance_rag
├─ Documents: Medical PDFs
├─ Vectors: 384-dimensional embeddings
├─ Count: 50-100+ chunks (depending on PDFs)
└─ Status: Ready for queries
```

---

## 💻 Testing the Connection

### Test 1: Basic Connection
```bash
python3 check_qdrant_connection.py
```
Expected: ✅ Connected

### Test 2: Python Code Connection
```python
from qdrant_client import QdrantClient
import os

url = os.getenv("QDRANT_URL", "http://localhost:6333")
client = QdrantClient(url=url)
collections = client.get_collections()
print(f"Collections: {len(collections.collections)}")
print("✅ Connection successful!")
```

### Test 3: HTTP API
```bash
# Check if Qdrant is responding
curl http://localhost:6333

# Get collections
curl http://localhost:6333/collections

# Check health
curl http://localhost:6333/health
```

### Test 4: Web Dashboard
```
Open: http://localhost:6333/dashboard
```

---

## 🛠️ Troubleshooting

### Issue: "Connection refused at localhost:6333"

**Solution**: Start Qdrant Docker container
```bash
docker run -p 6333:6333 qdrant/qdrant:latest
```

Or if using docker-compose:
```bash
docker-compose up -d qdrant
```

### Issue: "Collection not found"

**Expected**: Collections are created during ingestion

**Solution**: Run the setup script
```bash
python3 setup_qdrant_local.py
```

### Issue: "Permission denied"

**Possible causes**:
- Qdrant running with restricted permissions
- Firewall blocking port 6333

**Solution**:
```bash
# Check if port is in use
netstat -an | grep 6333

# Or restart Qdrant
docker restart qdrant
```

### Issue: "Out of memory" during ingestion

**Solution**: Reduce batch size or increase system RAM
```bash
# Edit setup_qdrant_local.py and reduce batch_size
```

---

## 📊 Database Monitoring

### View Statistics
```python
from qdrant_client import QdrantClient

client = QdrantClient(url="http://localhost:6333")
collection = client.get_collection("medical_assistance_rag")

print(f"Points: {collection.points_count}")
print(f"Status: {collection.status}")
print(f"Vector size: {collection.config.params.vectors.size}")
```

### Monitor via Dashboard
- Open: http://localhost:6333/dashboard
- View:
  - Collection statistics
  - Vector counts
  - Storage usage
  - Performance metrics

---

## 🔐 Security Notes

### Local Development (Current Setup)
- No authentication required
- All connections are local (localhost)
- Perfect for development and testing

### Production Deployment
For production, consider:
1. **API Key Protection**
   ```
   QDRANT_API_KEY=your-secure-key
   ```

2. **TLS/SSL Encryption**
   ```
   QDRANT_URL=https://secure.qdrant.com:6334
   ```

3. **Network Isolation**
   - Run in private network
   - Use firewall rules
   - Implement authentication

---

## 📚 Advanced Features

### Query with Filters
```python
from qdrant_client import models

results = client.search(
    collection_name="medical_assistance_rag",
    query_vector=embedding,
    query_filter=models.Filter(
        must=[
            models.HasIdCondition(has_id=[1, 2, 3])
        ]
    ),
    limit=5
)
```

### Batch Operations
```python
# Upsert multiple vectors
client.upsert(
    collection_name="medical_assistance_rag",
    points=points_list
)

# Delete vectors
client.delete(
    collection_name="medical_assistance_rag",
    points_selector=models.PointIdsList(
        ids=[1, 2, 3]
    )
)
```

### Custom Configuration
Edit `config.py` RAGConfig to:
- Change embedding model
- Adjust chunk size
- Modify reranker
- Update top_k results

---

## 🎯 Workflow Summary

```
┌─────────────────────────────────────────────────────┐
│  Qdrant Connection Verified ✅                      │
│  http://localhost:6333                              │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Setup Qdrant Collection │
        │ (setup_qdrant_local.py)  │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Ingest Medical PDFs     │
        │ (Parse + Embed)         │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Start Medical Assistant  │
        │ (python3 app.py)        │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Query RAG System        │
        │ (http://localhost:8000) │
        └────────────────────────┘
```

---

## 📞 Support Resources

- **Qdrant Documentation**: https://qdrant.tech/documentation/
- **Qdrant GitHub**: https://github.com/qdrant/qdrant
- **Project README**: See README.md
- **Setup Guide**: See SETUP_GUIDE.md

---

## ✨ Ready to Go!

Your Qdrant database connection is fully operational and verified. You're ready to:

✅ Create collections
✅ Ingest documents  
✅ Store embeddings
✅ Run RAG queries
✅ Perform similarity searches

**Next Step**: Run `python3 setup_qdrant_local.py` to populate your database with medical documents!

---

**Last Updated**: November 9, 2025  
**Status**: ✅ Production Ready  
**Connection**: ✅ Verified and Working
