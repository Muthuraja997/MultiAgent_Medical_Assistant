#!/usr/bin/env python3
"""
Reset and reinitialize local Qdrant instance with medical documents.

This script:
1. Connects to local Qdrant instance at http://localhost:6333
2. Deletes the old collection (if exists) with wrong dimensions
3. Creates a fresh 'medical_assistance_rag' collection
4. Ingests medical documents from data/raw/ directory with correct 384-dim embeddings
"""

import os
import sys
import logging
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from qdrant_client import QdrantClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_qdrant_connection():
    """Check if Qdrant is running and accessible."""
    try:
        from qdrant_client import QdrantClient
        
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        logger.info(f"Attempting to connect to Qdrant at {qdrant_url}...")
        
        # Try HTTP connection first
        try:
            client = QdrantClient(url=qdrant_url)
            collections = client.get_collections()
            logger.info(f"✅ Successfully connected to Qdrant at {qdrant_url}")
            logger.info(f"   Collections: {[c.name for c in collections.collections]}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Qdrant at {qdrant_url}: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Error checking Qdrant connection: {e}")
        return False


def verify_documents_exist():
    """Verify that medical documents exist in data/raw directory."""
    raw_dir = Path("./data/raw")
    
    if not raw_dir.exists():
        logger.warning(f"⚠️  Directory {raw_dir} does not exist")
        return False
    
    pdf_files = list(raw_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning(f"⚠️  No PDF files found in {raw_dir}")
        return False
    
    logger.info(f"✅ Found {len(pdf_files)} PDF files:")
    for pdf in pdf_files:
        logger.info(f"   - {pdf.name}")
    
    return True


def setup_qdrant_collection():
    """Create Qdrant collection and ingest medical documents."""
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = Config()
        
        # Initialize Medical RAG
        logger.info("Initializing Medical RAG system...")
        rag = MedicalRAG(config)
        
        # Check if collection already exists
        logger.info(f"Checking if collection '{config.rag.collection_name}' exists...")
        if rag.vector_store._does_collection_exist():
            logger.info(f"✅ Collection '{config.rag.collection_name}' already exists")
            return True
        
        logger.info(f"Creating collection '{config.rag.collection_name}'...")
        rag.vector_store._create_collection()
        logger.info(f"✅ Collection created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up Qdrant collection: {e}")
        import traceback
        traceback.print_exc()
        return False


def ingest_medical_documents():
    """Ingest medical documents from data/raw directory."""
    try:
        logger.info("=" * 60)
        logger.info("STARTING DOCUMENT INGESTION")
        logger.info("=" * 60)
        
        # Load configuration
        config = Config()
        
        # Initialize Medical RAG
        rag = MedicalRAG(config)
        
        # Ingest documents
        raw_dir = "./data/raw"
        
        if not os.path.exists(raw_dir):
            logger.error(f"Directory not found: {raw_dir}")
            return False
        
        logger.info(f"Starting ingestion of documents from {raw_dir}...")
        start_time = time.time()
        
        result = rag.ingest_directory(raw_dir)
        
        elapsed_time = time.time() - start_time
        
        # Display results
        logger.info("=" * 60)
        logger.info("INGESTION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"✅ Documents ingested: {result.get('documents_ingested', 0)}")
        logger.info(f"✅ Chunks processed: {result.get('chunks_processed', 0)}")
        logger.info(f"✅ Processing time: {elapsed_time:.2f} seconds")
        
        if result.get('failed_ingestions', 0) > 0:
            logger.warning(f"⚠️  Failed ingestions: {result.get('failed_ingestions', 0)}")
        
        logger.info("=" * 60)
        
        return result.get('success', False)
        
    except Exception as e:
        logger.error(f"Error ingesting medical documents: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_ingestion():
    """Verify that documents were successfully ingested."""
    try:
        logger.info("Verifying ingestion...")
        
        config = Config()
        from qdrant_client import QdrantClient
        
        # Connect to Qdrant
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        client = QdrantClient(url=qdrant_url)
        
        # Get collection info
        collection_info = client.get_collection(config.rag.collection_name)
        
        logger.info(f"✅ Collection: {config.rag.collection_name}")
        logger.info(f"✅ Total vectors: {collection_info.points_count}")
        logger.info(f"✅ Vector size: {collection_info.config.params.vectors.size}")
        
        if collection_info.points_count > 0:
            logger.info("✅ Collection has data - ingestion successful!")
            return True
        else:
            logger.warning("⚠️  Collection is empty - ingestion may have failed")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying ingestion: {e}")
        return False


def main():
    """Main setup routine."""
    logger.info("=" * 60)
    logger.info("QDRANT LOCAL SETUP - MEDICAL DOCUMENTS INGESTION")
    logger.info("=" * 60)
    
    # Step 1: Check Qdrant connection
    logger.info("\n[1/5] Checking Qdrant connection...")
    if not check_qdrant_connection():
        logger.error("❌ Failed to connect to Qdrant")
        logger.info("\n📝 Quick fix: Start Qdrant with:")
        logger.info("   docker run -p 6333:6333 qdrant/qdrant")
        return False
    
    # Step 2: Verify documents exist
    logger.info("\n[2/5] Verifying medical documents...")
    if not verify_documents_exist():
        logger.error("❌ No medical documents found")
        logger.info("\n📝 Please add PDF files to: ./data/raw/")
        return False
    
    # Step 3: Setup Qdrant collection
    logger.info("\n[3/5] Setting up Qdrant collection...")
    if not setup_qdrant_collection():
        logger.error("❌ Failed to setup collection")
        return False
    
    # Step 4: Ingest documents
    logger.info("\n[4/5] Ingesting medical documents...")
    if not ingest_medical_documents():
        logger.error("❌ Failed to ingest documents")
        return False
    
    # Step 5: Verify ingestion
    logger.info("\n[5/5] Verifying ingestion...")
    if not verify_ingestion():
        logger.warning("⚠️  Verification incomplete (collection may be empty)")
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ SETUP COMPLETE!")
    logger.info("=" * 60)
    logger.info("\nYou can now:")
    logger.info("  1. Start the app: python app.py")
    logger.info("  2. Query medical documents through the RAG agent")
    logger.info("  3. Access Qdrant UI: http://localhost:6333/dashboard")
    logger.info("=" * 60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
