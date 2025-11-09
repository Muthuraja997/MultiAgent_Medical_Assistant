#!/usr/bin/env python3
"""
Check and verify all required models are accessible and can be downloaded.

This script:
1. Checks HuggingFace connectivity
2. Verifies all required models are accessible
3. Pre-downloads models to cache for faster startup
4. Reports on model sizes and cache status
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelChecker:
    """Check and verify all required models."""
    
    # Models required by the project
    REQUIRED_MODELS = {
        'embeddings': {
            'model': 'all-MiniLM-L6-v2',
            'type': 'sentence-transformer',
            'size': '22 MB',
            'dimension': 384,
            'purpose': 'Generate embeddings for RAG',
        },
        'reranker': {
            'model': 'cross-encoder/ms-marco-TinyBERT-L-6',
            'type': 'cross-encoder',
            'size': '22 MB',
            'purpose': 'Rerank retrieved documents',
        },
        'sparse': {
            'model': 'Qdrant/bm25',
            'type': 'sparse-embedding',
            'size': '~1 MB',
            'purpose': 'Sparse embedding for hybrid search',
        }
    }
    
    def __init__(self):
        """Initialize the model checker."""
        load_dotenv()
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')
        self.cache_dir = Path.home() / '.cache' / 'huggingface' / 'hub'
        self.results = {}
        
    def check_huggingface_connection(self) -> bool:
        """Check if we can connect to HuggingFace Hub."""
        try:
            import requests
            logger.info("Testing HuggingFace Hub connection...")
            
            response = requests.head('https://huggingface.co', timeout=5)
            if response.status_code == 200:
                logger.info("✅ HuggingFace Hub is accessible")
                return True
            else:
                logger.error(f"❌ HuggingFace Hub returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to connect to HuggingFace Hub: {e}")
            return False
    
    def check_huggingface_token(self) -> bool:
        """Check if HuggingFace token is configured."""
        if self.hf_token:
            logger.info(f"✅ HuggingFace token found: {self.hf_token[:20]}...")
            return True
        else:
            logger.warning("⚠️  No HuggingFace token configured (may be needed for private models)")
            return False
    
    def check_embedding_model(self) -> bool:
        """Check if embedding model is accessible."""
        try:
            logger.info("Checking embedding model (all-MiniLM-L6-v2)...")
            from sentence_transformers import SentenceTransformer
            
            model = SentenceTransformer('all-MiniLM-L6-v2')
            dim = model.get_sentence_embedding_dimension()
            logger.info(f"✅ Embedding model loaded: {dim}-dimensional")
            self.results['embeddings'] = {'status': 'success', 'dimension': dim}
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            self.results['embeddings'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def check_reranker_model(self) -> bool:
        """Check if reranker model is accessible."""
        try:
            logger.info("Checking reranker model (ms-marco-TinyBERT-L-6)...")
            from sentence_transformers import CrossEncoder
            
            model = CrossEncoder('cross-encoder/ms-marco-TinyBERT-L-6')
            logger.info(f"✅ Reranker model loaded successfully")
            self.results['reranker'] = {'status': 'success'}
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load reranker model: {e}")
            self.results['reranker'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def check_sparse_model(self) -> bool:
        """Check if sparse embedding model is accessible."""
        try:
            logger.info("Checking sparse embedding model (Qdrant/bm25)...")
            from langchain_qdrant import FastEmbedSparse
            
            model = FastEmbedSparse(model_name="Qdrant/bm25")
            logger.info(f"✅ Sparse embedding model loaded successfully")
            self.results['sparse'] = {'status': 'success'}
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load sparse embedding model: {e}")
            self.results['sparse'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def check_qdrant_client(self) -> bool:
        """Check if Qdrant client is accessible."""
        try:
            logger.info("Checking Qdrant client...")
            from qdrant_client import QdrantClient
            
            client = QdrantClient()
            logger.info("✅ Qdrant client initialized successfully")
            self.results['qdrant'] = {'status': 'success'}
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Qdrant client: {e}")
            self.results['qdrant'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def check_langchain_dependencies(self) -> bool:
        """Check if LangChain dependencies are available."""
        try:
            logger.info("Checking LangChain dependencies...")
            import langchain
            import langchain_core
            import langchain_google_genai
            import langchain_qdrant
            
            logger.info("✅ All LangChain dependencies available")
            self.results['langchain'] = {'status': 'success'}
            return True
        except Exception as e:
            logger.error(f"❌ Missing LangChain dependencies: {e}")
            self.results['langchain'] = {'status': 'failed', 'error': str(e)}
            return False
    
    def check_gemini_api(self) -> bool:
        """Check if Gemini API is configured."""
        try:
            logger.info("Checking Google Gemini API...")
            google_api_key = os.getenv('GOOGLE_API_KEY')
            
            if not google_api_key:
                logger.warning("⚠️  No GOOGLE_API_KEY configured")
                self.results['gemini'] = {'status': 'warning', 'configured': False}
                return False
            
            from config import Config
            config = Config()
            llm = config.agent_decision.llm
            
            logger.info("✅ Gemini API configured")
            self.results['gemini'] = {'status': 'success', 'configured': True}
            return True
        except Exception as e:
            logger.error(f"⚠️  Gemini API check failed: {e}")
            self.results['gemini'] = {'status': 'warning', 'error': str(e)}
            return False
    
    def get_cache_size(self) -> Tuple[int, str]:
        """Get size of HuggingFace cache."""
        try:
            if self.cache_dir.exists():
                total_size = sum(f.stat().st_size for f in self.cache_dir.rglob('*') if f.is_file())
                size_gb = total_size / (1024 ** 3)
                return total_size, f"{size_gb:.2f} GB"
            return 0, "0 GB"
        except Exception as e:
            logger.error(f"Error calculating cache size: {e}")
            return 0, "Unknown"
    
    def run_all_checks(self) -> bool:
        """Run all model checks."""
        logger.info("=" * 70)
        logger.info("CHECKING ALL REQUIRED MODELS")
        logger.info("=" * 70)
        
        checks = [
            ("HuggingFace Connection", self.check_huggingface_connection),
            ("HuggingFace Token", self.check_huggingface_token),
            ("LangChain Dependencies", self.check_langchain_dependencies),
            ("Embedding Model", self.check_embedding_model),
            ("Reranker Model", self.check_reranker_model),
            ("Sparse Embedding Model", self.check_sparse_model),
            ("Qdrant Client", self.check_qdrant_client),
            ("Gemini API", self.check_gemini_api),
        ]
        
        results = []
        for check_name, check_func in checks:
            logger.info(f"\n[Check] {check_name}...")
            try:
                result = check_func()
                results.append(result)
            except Exception as e:
                logger.error(f"Error during {check_name}: {e}")
                results.append(False)
        
        return all(results)
    
    def print_summary(self):
        """Print a summary of all checks."""
        logger.info("\n" + "=" * 70)
        logger.info("MODEL CHECK SUMMARY")
        logger.info("=" * 70)
        
        logger.info("\n📦 REQUIRED MODELS:")
        logger.info("━" * 70)
        
        for model_key, model_info in self.REQUIRED_MODELS.items():
            status = self.results.get(model_key, {}).get('status', 'unknown')
            status_emoji = '✅' if status == 'success' else '❌'
            
            logger.info(f"\n{status_emoji} {model_key.upper()}")
            logger.info(f"   Model: {model_info['model']}")
            logger.info(f"   Type: {model_info['type']}")
            logger.info(f"   Size: {model_info['size']}")
            logger.info(f"   Purpose: {model_info['purpose']}")
            
            if 'dimension' in model_info:
                logger.info(f"   Dimension: {model_info['dimension']}")
        
        logger.info("\n" + "━" * 70)
        logger.info("🔧 SYSTEM COMPONENTS:")
        logger.info("━" * 70)
        
        components = ['langchain', 'qdrant', 'gemini']
        for comp in components:
            if comp in self.results:
                status = self.results[comp].get('status', 'unknown')
                status_emoji = '✅' if status == 'success' else '⚠️ ' if status == 'warning' else '❌'
                logger.info(f"{status_emoji} {comp.upper()}: {status}")
        
        # Cache info
        cache_size, cache_size_str = self.get_cache_size()
        logger.info("\n" + "━" * 70)
        logger.info("💾 HUGGINGFACE CACHE:")
        logger.info("━" * 70)
        logger.info(f"Cache Location: {self.cache_dir}")
        logger.info(f"Cache Size: {cache_size_str}")
        
        logger.info("\n" + "=" * 70)


def main():
    """Main function."""
    try:
        checker = ModelChecker()
        success = checker.run_all_checks()
        checker.print_summary()
        
        logger.info("\n" + "=" * 70)
        if success:
            logger.info("✅ ALL MODELS ACCESSIBLE - Ready to use!")
            logger.info("=" * 70)
            logger.info("\n🚀 You can now start the application:")
            logger.info("   python3 app.py")
            return True
        else:
            logger.warning("⚠️  Some models or components are not accessible")
            logger.info("=" * 70)
            logger.info("\n📝 Troubleshooting steps:")
            logger.info("   1. Check your internet connection")
            logger.info("   2. Verify HUGGINGFACE_TOKEN in .env")
            logger.info("   3. Check GOOGLE_API_KEY in .env")
            logger.info("   4. Run: pip install -r requirements.txt")
            logger.info("   5. See HUGGINGFACE_GUIDE.md for details")
            return False
            
    except Exception as e:
        logger.error(f"Fatal error during model check: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
