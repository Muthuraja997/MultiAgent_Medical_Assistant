# Copilot Instructions for Multi-Agent Medical Assistant

## Project Overview
A FastAPI-based multi-agent medical chatbot that routes user queries and images to specialized LLM and computer vision agents. The system orchestrates 6 distinct agents using **LangGraph** for medical diagnosis, information retrieval, image analysis, and web search.

## Architecture & Data Flow

### Core Orchestration: `agents/agent_decision.py`
- **Decision Agent** routes queries using LLM-based triage (see `AgentConfig.DECISION_SYSTEM_PROMPT`)
- Creates a **LangGraph workflow** (not a simple function chain) with memory persistence via `MemorySaver()`
- Agents: CONVERSATION_AGENT, RAG_AGENT, WEB_SEARCH_PROCESSOR_AGENT, and 3 medical vision agents
- Detects images via `analyze_input()` node; guardrails check input/output safety

### Six Specialized Agents

1. **RAG Agent** (`agents/rag_agent/__init__.py`): Query expansion → hybrid BM25+semantic search → reranking → LLM response
   - Ingests PDFs via Docling (v2.1+, replaces Unstructured.io)
   - LLM-based semantic chunking with structural awareness
   - Qdrant vector database (local: `data/qdrant_db/` or remote via env vars)
   - Cross-Encoder reranking before LLM generation

2. **Web Search Agent** (`agents/web_search_processor_agent/`): PubMed + Tavily search with confidence-based routing
3. **Chest X-ray Agent**: COVID/abnormality detection (`agents/image_analysis_agent/chest_xray_agent/`)
4. **Skin Lesion Agent**: Segmentation output to `uploads/skin_lesion_output/`
5. **Brain Tumor Agent**: TBD in codebase
6. **Conversation Agent**: General chat fallback

### Request Entry: `app.py`
- `/chat` endpoint: text + conversation history → `process_query()` in agent_decision
- `/upload` endpoint: handles image uploads to `uploads/backend/`
- Session management via cookies; returns `needs_validation` flag for human-in-the-loop

## Configuration & Environment

### `config.py` Structure
- **AgentDecisionConfig**: routing LLM (temp=0.1, deterministic)
- **RAGConfig**: embedding model, chunking (512 tokens, 50 overlap), reranker settings
- **ConversationConfig**: general LLM (temp=0.7)
- **WebSearchConfig**: context_limit=20 messages
- **MedicalCVConfig** (implied): image model paths

### Azure OpenAI Setup (Required)
```env
deployment_name, model_name, azure_endpoint, openai_api_key, openai_api_version
embedding_deployment_name, embedding_model_name, embedding_azure_endpoint, embedding_openai_api_key
QDRANT_URL, QDRANT_API_KEY (optional if using local)
ELEVEN_LABS_API_KEY (for speech)
```

## Key Patterns & Workflows

### Document Ingestion Pipeline
1. `ingest_rag_data.py` → calls `MedicalRAG.ingest_directory()`
2. **Docling** parses PDFs → text + tables + image summaries
3. **ContentProcessor** → LLM-based semantic chunking
4. **VectorStore** → embeddings indexed in Qdrant with BM25 keywords
5. Parsed content saved to `data/parsed_docs/` for debugging

### Query Handling Flow
1. Input guardrails check (`agents/guardrails/local_guardrails.py`)
2. LLM routes to agent based on query + image presence
3. If RAG: expand query → retrieve → rerank → generate response with source links
4. If vision: classify image type → run specialized model → human validation check
5. Output guardrails filter unsafe medical claims

### Confidence-Based Handoff
- RAG agent sets `retrieval_confidence` score
- If confidence < threshold → fallback to web search
- Vision agents may trigger `needs_human_validation=True` for critical diagnoses

## Development Conventions

### File Naming & Location
- Agent modules: `agents/{agent_type_agent}/` with `__init__.py` as public interface
- Config classes: one per agent type in `config.py`
- Guardrails: `agents/guardrails/local_guardrails.py` (input/output filtering)
- Vision models: stored in `data/` or config-specified paths

### LLM Temperature Strategy
- **Decision routing**: temp=0.1 (deterministic)
- **RAG response gen**: temp=0.3 (factual)
- **Conversation**: temp=0.7 (engaging)
- **Chunking/Expansion**: temp=0.0–0.3 (precise extraction)

### State Management (`AgentState` in agent_decision.py)
- `messages`: conversation history (LangChain `BaseMessage` objects)
- `has_image`, `image_type`: image detection results
- `bypass_routing`: guardrail flags input/output blocks
- `needs_human_validation`: vision agent workflows pause here

## Critical Files Reference

| File | Purpose |
|------|---------|
| `app.py` | FastAPI endpoints, session mgmt, file uploads |
| `config.py` | LLM & embedding configs, all temperature settings |
| `agents/agent_decision.py` | LangGraph workflow, routing logic, state definitions |
| `agents/rag_agent/__init__.py` | RAG orchestration & ingestion pipeline |
| `agents/rag_agent/vectorstore_qdrant.py` | Qdrant client initialization |
| `agents/guardrails/local_guardrails.py` | Input/output safety filtering |
| `ingest_rag_data.py` | Script to ingest document directories |
| `agents/README.md` | Human-in-the-loop validation details |

## Common Tasks

### Adding a New Agent
1. Create `agents/new_agent_type/` with `__init__.py` exposing main function
2. Add config class in `config.py` with its own LLM instance
3. Update `DECISION_SYSTEM_PROMPT` routing logic in `AgentConfig`
4. Add node to LangGraph in `create_agent_graph()`

### Ingesting New Medical Documents
```bash
python ingest_rag_data.py --input /path/to/pdfs
```
Uses Docling → semantic chunking → Qdrant indexing. Verify in `data/parsed_docs/`.

### Modifying Chunking Strategy
Edit `RAGConfig.chunk_size`, `chunk_overlap`, or `ContentProcessor.semantic_chunk()` logic.

### Testing Agent Routing
Enable debug logging in `agent_decision.py` to inspect decision chain output before agent execution.

## Integration Points

- **LangChain/LangGraph**: agent orchestration, LLM invocations, output parsing
- **Qdrant**: vector search backend (local or remote)
- **Docling**: document parsing (PDFs → text + tables + images)
- **Azure OpenAI**: all LLM & embedding calls
- **ElevenLabs**: text-to-speech API
- **Tavily & PubMed**: web search sources
- **Computer Vision Models**: pre-trained chest X-ray & skin lesion classifiers

## Notes for AI Agents

- Always check `config.py` first for LLM instances and temperature settings—they're reused across agents
- Human-in-the-loop validation is triggered by vision agents, not routing
- Guardrails can block both input and output; check `local_guardrails.py` when debugging filter behavior
- RAG responses include source document links from `data/docs_db/` and parsed content
- Session IDs persist workflow state; regenerating them may lose context
