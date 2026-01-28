#!/usr/bin/env python3
"""
Clean Qdrant database and remove old collections with wrong dimensions.
"""

import os
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from qdrant_client import QdrantClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_qdrant():
    """Delete all collections to start fresh."""
    try:
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        logger.info(f"Connecting to Qdrant at {qdrant_url}...")
        
        client = QdrantClient(url=qdrant_url)
        
        # Get all collections
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        logger.info(f"Found {len(collection_names)} collections")
        
        # Delete each collection
        for collection_name in collection_names:
            logger.info(f"Deleting collection: {collection_name}...")
            client.delete_collection(collection_name=collection_name)
            logger.info(f"✅ Deleted: {collection_name}")
        
        logger.info("✅ Cleanup complete!")
        return True
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = cleanup_qdrant()
    sys.exit(0 if success else 1)
