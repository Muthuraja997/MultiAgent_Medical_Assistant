#!/usr/bin/env python3
"""
Qdrant Collection Creation Script

This script creates a properly configured Qdrant collection for the Medical Assistant.

Configuration:
- Collection Name: medical_assistance_rag
- Vector Size (Dense): 384 dimensions (from all-MiniLM-L6-v2 embedding model)
- Vector Type: Dense vectors (COSINE distance)
- Sparse Vectors: BM25 sparse embeddings for hybrid search
- Payload: Metadata storage for document source and IDs
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, SparseVectorParams, VectorParams, PointStruct

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION - Derived from config.py
# ============================================================================
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "medical_assistance_rag"

# From RAGConfig in config.py
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 dimension
DISTANCE_METRIC = Distance.COSINE  # Recommended for semantic embeddings
VECTOR_SEARCH_TYPE = "hybrid"  # Dense + Sparse (BM25)

# Reranker configuration
RERANKER_MODEL = "cross-encoder/ms-marco-TinyBERT-L-6"
TOP_K = 5
RERANKER_TOP_K = 3


def test_connection():
    """Test connection to Qdrant server."""
    try:
        logger.info(f"🔌 Testing connection to Qdrant at {QDRANT_URL}...")
        client = QdrantClient(url=QDRANT_URL)
        
        # Get collections to verify connection
        collections = client.get_collections()
        logger.info(f"✅ Connected to Qdrant server")
        logger.info(f"   Current collections: {len(collections.collections)}")
        
        return client
    except Exception as e:
        logger.error(f"❌ Failed to connect to Qdrant at {QDRANT_URL}")
        logger.error(f"   Error: {e}")
        logger.info("\n📝 Quick fix: Start Qdrant with Docker:")
        logger.info("   docker run -p 6333:6333 qdrant/qdrant")
        sys.exit(1)


def check_existing_collection(client):
    """Check if collection already exists."""
    try:
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        if COLLECTION_NAME in collection_names:
            logger.info(f"ℹ️  Collection '{COLLECTION_NAME}' already exists")
            
            # Get collection info
            collection_info = client.get_collection(COLLECTION_NAME)
            logger.info(f"   Vectors count: {collection_info.points_count}")
            logger.info(f"   Vector size: {collection_info.config.params.vectors.size}")
            
            return True
        else:
            logger.info(f"ℹ️  Collection '{COLLECTION_NAME}' does not exist")
            return False
    except Exception as e:
        logger.error(f"Error checking collections: {e}")
        return False


def delete_collection(client):
    """Delete existing collection."""
    try:
        logger.warning(f"🗑️  Deleting existing collection '{COLLECTION_NAME}'...")
        client.delete_collection(collection_name=COLLECTION_NAME)
        logger.info(f"✅ Successfully deleted collection '{COLLECTION_NAME}'")
        return True
    except Exception as e:
        logger.error(f"❌ Error deleting collection: {e}")
        return False


def create_collection(client):
    """
    Create a new Qdrant collection with proper configuration for medical documents.
    
    Collection Structure:
    - Dense vectors: 384-dimensional (from all-MiniLM-L6-v2)
    - Sparse vectors: BM25 for full-text search
    - Hybrid search: Combines dense semantic + sparse keyword search
    """
    try:
        logger.info(f"\n📦 Creating collection '{COLLECTION_NAME}'...")
        logger.info(f"   Dense vectors: {EMBEDDING_DIM} dimensions (Cosine distance)")
        logger.info(f"   Sparse vectors: BM25 (keyword search)")
        logger.info(f"   Search mode: Hybrid (semantic + keyword)")
        
        # Create collection with both dense and sparse vectors
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "dense": VectorParams(
                    size=EMBEDDING_DIM,
                    distance=DISTANCE_METRIC,
                    on_disk=False  # Keep in memory for better performance
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(
                    index=models.SparseIndexParams(on_disk=False)
                )
            }
        )
        
        logger.info(f"✅ Collection '{COLLECTION_NAME}' created successfully!")
        
        # Verify collection
        collection_info = client.get_collection(COLLECTION_NAME)
        logger.info(f"\n📊 Collection Configuration:")
        logger.info(f"   Name: {COLLECTION_NAME}")
        logger.info(f"   Status: {collection_info.status}")
        logger.info(f"   Points count: {collection_info.points_count}")
        logger.info(f"   Dense vector size: {collection_info.config.params.vectors['dense'].size}")
        logger.info(f"   Distance metric: {collection_info.config.params.vectors['dense'].distance}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating collection: {e}")
        import traceback
        traceback.print_exc()
        return False


def display_collection_summary(client):
    """Display final collection summary."""
    try:
        collection_info = client.get_collection(COLLECTION_NAME)
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ QDRANT COLLECTION SETUP COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Collection Name:     {COLLECTION_NAME}")
        logger.info(f"Status:              {collection_info.status}")
        logger.info(f"Vector Dimensions:   {collection_info.config.params.vectors['dense'].size}")
        logger.info(f"Distance Metric:     {collection_info.config.params.vectors['dense'].distance}")
        logger.info(f"Documents in DB:     {collection_info.points_count}")
        logger.info(f"Qdrant URL:          {QDRANT_URL}")
        logger.info("=" * 70)
        logger.info("\n📝 Next steps:")
        logger.info("   1. Ingest medical documents: python3 setup_qdrant_local.py")
        logger.info("   2. Start the app: python3 app.py")
        logger.info("   3. Visit: http://localhost:8000")
        logger.info("\n🔍 Monitor collection at:")
        logger.info(f"   {QDRANT_URL}/dashboard")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Error displaying summary: {e}")


def main():
    """Main setup routine."""
    logger.info("=" * 70)
    logger.info("🚀 QDRANT COLLECTION SETUP")
    logger.info("=" * 70)
    
    # Step 1: Connect to Qdrant
    logger.info("\n[1/3] Connecting to Qdrant...")
    client = test_connection()
    
    # Step 2: Check and handle existing collection
    logger.info("\n[2/3] Checking for existing collection...")
    exists = check_existing_collection(client)
    
    if exists:
        user_input = input(f"\n❓ Collection '{COLLECTION_NAME}' already exists. Do you want to recreate it? (y/n): ").strip().lower()
        if user_input == 'y':
            if not delete_collection(client):
                logger.error("Failed to delete collection. Exiting.")
                sys.exit(1)
        else:
            logger.info("Keeping existing collection.")
            display_collection_summary(client)
            return
    
    # Step 3: Create collection
    logger.info("\n[3/3] Creating collection...")
    if not create_collection(client):
        logger.error("Failed to create collection. Exiting.")
        sys.exit(1)
    
    # Display summary
    display_collection_summary(client)


if __name__ == "__main__":
    main()
