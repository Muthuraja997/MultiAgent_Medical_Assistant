#!/usr/bin/env python3
"""
Simplified medical document ingestion script.
This ingests documents one at a time with clear error handling and progress reporting.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from agents.rag_agent import MedicalRAG

# Configure logging with more detail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 70)
    logger.info("MEDICAL DOCUMENT INGESTION - SIMPLE VERSION")
    logger.info("=" * 70)
    
    try:
        # Initialize config
        logger.info("\n[1] Loading configuration...")
        config = Config()
        logger.info(f"✅ Collection name: {config.rag.collection_name}")
        logger.info(f"✅ Embedding dims: {config.rag.embedding_dim}")
        
        # Initialize RAG
        logger.info("\n[2] Initializing Medical RAG system...")
        rag = MedicalRAG(config)
        logger.info("✅ RAG system initialized")
        
        # Get documents
        raw_dir = "./data/raw"
        if not os.path.exists(raw_dir):
            logger.error(f"❌ Directory not found: {raw_dir}")
            return False
        
        pdf_files = sorted([f for f in os.listdir(raw_dir) if f.endswith('.pdf')])
        if not pdf_files:
            logger.error(f"❌ No PDF files found in {raw_dir}")
            return False
        
        logger.info(f"\n[3] Found {len(pdf_files)} PDF files:")
        for f in pdf_files:
            logger.info(f"   - {f}")
        
        # Ingest each document
        logger.info(f"\n[4] Starting ingestion (force_recreate=True on first file)...")
        total_chunks = 0
        
        for idx, pdf_file in enumerate(pdf_files):
            pdf_path = os.path.join(raw_dir, pdf_file)
            force_recreate = (idx == 0)  # Force recreate on first file
            
            logger.info(f"\n--- Processing {idx + 1}/{len(pdf_files)}: {pdf_file} ---")
            logger.info(f"    force_recreate = {force_recreate}")
            
            try:
                result = rag.ingest_file(pdf_path, force_recreate=force_recreate)
                
                if result["success"]:
                    chunks = result.get("chunks_processed", 0)
                    total_chunks += chunks
                    logger.info(f"✅ SUCCESS: {chunks} chunks ingested")
                else:
                    error = result.get("error", "Unknown error")
                    logger.error(f"❌ FAILED: {error}")
                    
            except Exception as e:
                logger.error(f"❌ EXCEPTION: {e}", exc_info=True)
        
        # Verify
        logger.info(f"\n[5] Verification...")
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(path=config.rag.vector_local_path)
            collections = client.get_collections()
            
            for coll in collections.collections:
                if coll.name == config.rag.collection_name:
                    logger.info(f"✅ Collection '{config.rag.collection_name}' created")
                    logger.info(f"✅ Total vectors in collection: {coll.points_count}")
                    logger.info(f"✅ Total chunks ingested: {total_chunks}")
                    
                    if coll.points_count > 0:
                        logger.info("\n" + "=" * 70)
                        logger.info("✅ INGESTION SUCCESSFUL!")
                        logger.info("=" * 70)
                        return True
            
            logger.error(f"❌ Collection '{config.rag.collection_name}' not found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}", exc_info=True)
            return False
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
