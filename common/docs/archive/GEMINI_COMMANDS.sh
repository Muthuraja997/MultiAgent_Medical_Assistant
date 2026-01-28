#!/usr/bin/env bash
# Gemini Setup - Quick Command Reference
# Usage: Copy and paste these commands into your terminal

echo "🚀 Gemini Setup - Quick Start Commands"
echo "======================================"
echo ""

# Phase 1: Navigate to project
echo "# Phase 1: Navigate to project directory"
echo "cd /home/muthuraja/Project/Multi-Agent-Medical-Assistant"
echo ""

# Phase 2: Install dependencies
echo "# Phase 2: Install dependencies (2-3 min)"
echo "pip install -r requirements.txt"
echo ""

# Phase 3: Setup environment
echo "# Phase 3: Setup environment variables"
echo "cp .env.gemini .env"
echo "# Verify API key:"
echo "cat .env | grep GOOGLE_API_KEY"
echo ""

# Phase 4: Start Qdrant
echo "# Phase 4: Start Qdrant vector database"
echo "docker run -d \\"
echo "  --name qdrant \\"
echo "  -p 6333:6333 \\"
echo "  -v \$(pwd)/data/qdrant_db:/qdrant/storage \\"
echo "  qdrant/qdrant:latest"
echo ""
echo "# Verify Qdrant is running:"
echo "curl http://localhost:6333/health"
echo ""

# Phase 5: Validate setup
echo "# Phase 5: Validate configuration"
echo "python test_gemini_setup.py"
echo ""

# Phase 6: Ingest documents (optional)
echo "# Phase 6: Ingest medical documents (optional)"
echo "mkdir -p data/raw"
echo "# Copy your PDF files to data/raw/"
echo "python ingest_rag_data.py --input data/raw"
echo ""

# Phase 7: Run application
echo "# Phase 7: Start the application"
echo "python app.py"
echo ""
echo "# Open in browser:"
echo "http://localhost:8000"
echo ""

echo "======================================"
echo "✅ Setup complete!"
echo ""
echo "Documentation:"
echo "  Quick Start:    GEMINI_QUICKSTART.md"
echo "  Detailed Guide: GEMINI_SETUP_IMPLEMENTATION.md"
echo "  Status Report:  GEMINI_IMPLEMENTATION_STATUS.md"
echo "  Full Migration: GEMINI_MIGRATION_COMPLETE.md"
echo ""
