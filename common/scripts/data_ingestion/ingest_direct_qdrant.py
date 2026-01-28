#!/usr/bin/env python3
"""
Direct Qdrant Ingestion Script

Directly ingest medical documents into Qdrant without using LangChain's QdrantVectorStore.
This bypasses potential performance issues with the wrapper.

Pipeline:
1. Parse PDFs with Docling
2. Extract and summarize images with Gemini
3. Chunk documents semantically
4. Generate embeddings (all-MiniLM-L6-v2, 384-dim)
5. Create BM25 sparse embeddings
6. Directly upsert to Qdrant
"""

import os
import sys
import time
import logging
from pathlib import Path
from uuid import uuid4
from typing import List, Dict, Any, Tuple

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from agents.rag_agent.doc_parser import MedicalDocParser
from agents.rag_agent.content_processor import ContentProcessor
from agents.rag_agent.embeddings_wrapper import SentenceTransformerEmbeddings

from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain.storage import LocalFileStore
from langchain_qdrant import FastEmbedSparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DirectQdrantIngester:
    """Direct ingestion to Qdrant bypassing LangChain wrapper issues."""
    
    def __init__(self, config):
        logger.info("Initializing Direct Qdrant Ingester...")
        self.config = config
        
        # Initialize components
        self.doc_parser = MedicalDocParser()
        self.content_processor = ContentProcessor(config)
        
        # Embeddings
        self.embeddings = SentenceTransformerEmbeddings(
            model_name='all-MiniLM-L6-v2',
            encode_kwargs={'show_progress_bar': False}
        )
        
        # BM25 sparse embeddings
        self.sparse_embeddings = FastEmbedSparse(model_name="Qdrant/bm25")
        
        # Qdrant client
        self.client = QdrantClient(url=config.rag.url)
        self.collection_name = config.rag.collection_name
        
        # Doc store
        self.docstore = LocalFileStore(config.rag.doc_local_path)
        
        logger.info("✅ Direct Qdrant Ingester initialized")
    
    def ingest_directory(self, directory_path: str) -> Dict[str, Any]:
        """Ingest all PDFs from a directory."""
        start_time = time.time()
        logger.info(f"\n{'='*70}")
        logger.info("🚀 STARTING DIRECT QDRANT INGESTION")
        logger.info(f"{'='*70}")
        logger.info(f"Source directory: {directory_path}")
        logger.info(f"Target collection: {self.collection_name}")
        
        # Get all PDF files
        pdf_files = sorted(Path(directory_path).glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        stats = {
            "total_chunks": 0,
            "successful_documents": 0,
            "failed_documents": 0,
            "total_vectors_upserted": 0,
        }
        
        for idx, pdf_path in enumerate(pdf_files, 1):
            logger.info(f"\n[{idx}/{len(pdf_files)}] Processing: {pdf_path.name}")
            
            try:
                # Parse document
                logger.info("   1. Parsing PDF and extracting images...")
                parsed_doc, images = self.doc_parser.parse_document(
                    str(pdf_path),
                    self.config.rag.parsed_content_dir
                )
                logger.info(f"   ✅ Extracted {len(images)} images")
                
                # Summarize images
                logger.info("   2. Summarizing images...")
                image_summaries = self.content_processor.summarize_images(images)
                logger.info(f"   ✅ Generated {len(image_summaries)} image summaries")
                
                # Format document
                logger.info("   3. Formatting document...")
                formatted_doc = self.content_processor.format_document_with_images(
                    parsed_doc,
                    image_summaries
                )
                
                # Chunk document
                logger.info("   4. Chunking document...")
                chunks = self.content_processor.chunk_document(formatted_doc)
                logger.info(f"   ✅ Created {len(chunks)} chunks")
                
                # Generate embeddings and upsert
                logger.info("   5. Generating embeddings and upserting...")
                vectors_upserted = self._upsert_chunks_to_qdrant(
                    chunks,
                    str(pdf_path)
                )
                
                logger.info(f"   ✅ Upserted {vectors_upserted} vectors")
                
                stats["total_chunks"] += len(chunks)
                stats["successful_documents"] += 1
                stats["total_vectors_upserted"] += vectors_upserted
                
            except Exception as e:
                logger.error(f"   ❌ Error processing {pdf_path.name}: {e}")
                import traceback
                traceback.print_exc()
                stats["failed_documents"] += 1
        
        elapsed = time.time() - start_time
        
        # Display results
        logger.info(f"\n{'='*70}")
        logger.info("✅ INGESTION COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"Documents processed:    {stats['successful_documents']}/{len(pdf_files)}")
        logger.info(f"Total chunks created:   {stats['total_chunks']}")
        logger.info(f"Total vectors upserted: {stats['total_vectors_upserted']}")
        logger.info(f"Processing time:        {elapsed:.2f} seconds")
        logger.info(f"{'='*70}\n")
        
        return stats
    
    def _upsert_chunks_to_qdrant(self, chunks: List[str], source_path: str) -> int:
        """
        Generate embeddings for chunks and upsert directly to Qdrant.
        
        Returns:
            Number of vectors upserted
        """
        logger.info(f"      Generating embeddings for {len(chunks)} chunks...")
        
        # Generate dense embeddings only
        # (sparse embeddings with Qdrant requires special handling, skip for now)
        dense_embeddings = self.embeddings.embed_documents(chunks)
        
        # Prepare points for upsert
        points = []
        for chunk_idx, (chunk, dense_emb) in enumerate(zip(chunks, dense_embeddings)):
            point_id = str(uuid4())
            
            # Create point with just dense vector
            point = models.PointStruct(
                id=abs(hash(point_id)) % (2**31),  # Use positive hash for numeric ID
                vector={"dense": dense_emb},
                payload={
                    "source": Path(source_path).name,
                    "doc_id": point_id,
                    "source_path": f"http://localhost:8000/{source_path}",
                    "chunk_index": chunk_idx,
                    "text": chunk[:500]  # Store first 500 chars as preview
                }
            )
            points.append(point)
            
            # Store full chunk in docstore
            self.docstore.mset([(point_id, chunk.encode('utf-8'))])
        
        # Upsert to Qdrant
        logger.info(f"      Upserting {len(points)} points to Qdrant...")
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"      ✅ Successfully upserted {len(points)} vectors")
            return len(points)
        except Exception as e:
            logger.error(f"      ❌ Error upserting to Qdrant: {e}")
            raise


def main():
    """Main entry point."""
    logger.info("=" * 70)
    logger.info("DIRECT QDRANT MEDICAL DOCUMENTS INGESTION")
    logger.info("=" * 70)
    
    try:
        # Load config
        config = Config()
        
        # Verify Qdrant connection
        logger.info("\n[1/3] Verifying Qdrant connection...")
        try:
            client = QdrantClient(url=config.rag.url)
            collections = client.get_collections()
            logger.info(f"✅ Connected to Qdrant at {config.rag.url}")
            logger.info(f"   Current collections: {len(collections.collections)}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Qdrant: {e}")
            return False
        
        # Verify collection exists
        logger.info("\n[2/3] Checking collection...")
        try:
            collection_info = client.get_collection(config.rag.collection_name)
            logger.info(f"✅ Collection '{config.rag.collection_name}' exists")
            logger.info(f"   Current vectors: {collection_info.points_count}")
        except Exception as e:
            logger.error(f"❌ Collection not found: {e}")
            return False
        
        # Ingest documents
        logger.info("\n[3/3] Ingesting documents...")
        ingester = DirectQdrantIngester(config)
        stats = ingester.ingest_directory("./data/raw")
        
        # Verify ingestion
        logger.info("\n[Verification] Checking final collection state...")
        collection_info = client.get_collection(config.rag.collection_name)
        logger.info(f"\n✅ FINAL COLLECTION STATE")
        logger.info(f"   Total vectors in collection: {collection_info.points_count}")
        logger.info(f"   Vector dimensions: {collection_info.config.params.vectors['dense'].size}")
        logger.info(f"   Distance metric: {collection_info.config.params.vectors['dense'].distance}")
        logger.info(f"\n🎉 Ingestion complete! Ready to use.\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
