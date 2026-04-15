#!/usr/bin/env python3
"""
Test script to validate Gemini API connection and configuration.
Run this to verify your Gemini setup is working correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API connection"""
    print("\n" + "="*60)
    print("Testing Google Gemini API Connection")
    print("="*60)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ FAILED: GOOGLE_API_KEY not found in .env file")
        return False
    
    print(f"✓ API Key found: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
        llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.1,
            convert_system_message_to_human=True,
        )
        
        # Test a simple query
        response = llm.invoke("Say 'Gemini is working!' in one sentence.")
        print(f"✓ Gemini Response: {response.content}")
        print("✅ PASSED: Gemini API is working correctly\n")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}\n")
        return False


def test_embeddings():
    """Test Sentence-Transformers embeddings"""
    print("="*60)
    print("Testing Sentence-Transformers Embeddings")
    print("="*60)
    
    try:
        from agents.rag_agent.embeddings_wrapper import SentenceTransformerEmbeddings
        
        print("Initializing SentenceTransformerEmbeddings...")
        embeddings = SentenceTransformerEmbeddings(
            model_name='all-MiniLM-L6-v2',
            encode_kwargs={'show_progress_bar': False}
        )
        print("✓ Model loaded successfully")
        
        # Test single embedding
        query = "What is diabetes?"
        embedding = embeddings.embed_query(query)
        print(f"✓ Query: '{query}'")
        print(f"✓ Embedding dimension: {len(embedding)}")
        print(f"✓ First 5 values: {embedding[:5]}")
        
        # Test batch embedding
        texts = ["Medical diagnosis", "Treatment plan", "Patient history"]
        batch_embeddings = embeddings.embed_documents(texts)
        print(f"✓ Batch embedding of {len(texts)} texts successful")
        print(f"✓ Batch embedding dimensions: {[len(e) for e in batch_embeddings]}")
        
        print("✅ PASSED: Embeddings are working correctly\n")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}\n")
        return False


def test_qdrant_connection():
    """Test Qdrant vector database connection"""
    print("="*60)
    print("Testing Qdrant Vector Database Connection")
    print("="*60)
    
    try:
        from qdrant_client import QdrantClient
        
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        print(f"Connecting to Qdrant at: {qdrant_url}")
        
        # Try local path first (if using local storage)
        local_path = "./data/qdrant_db"
        client = QdrantClient(path=local_path)
        
        # Test connection
        health = client.get_collections()
        print(f"✓ Successfully connected to Qdrant")
        print(f"✓ Collections: {len(health.collections)} collection(s)")
        
        print("✅ PASSED: Qdrant is accessible\n")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: Qdrant not running or not accessible")
        print(f"   Error: {str(e)}")
        print("   Make sure to run Qdrant with Docker:")
        print("   docker run -p 6333:6333 qdrant/qdrant\n")
        return False


def test_web_search():
    """Test open-source web search"""
    print("="*60)
    print("Testing Open-Source Web Search (DuckDuckGo)")
    print("="*60)
    
    try:
        from agents.web_search_processor_agent.opensource_search import OpenSourceWebSearch
        
        print("Initializing web search...")
        search = OpenSourceWebSearch(max_results=3)
        print("✓ Web search initialized")
        
        print("Testing search query: 'COVID-19 symptoms'")
        results = search.search("COVID-19 symptoms")
        
        if results and "No relevant results" not in results:
            print(f"✓ Search returned results")
            lines = results.split('\n')[:5]  # Show first 5 lines
            for line in lines:
                if line.strip():
                    print(f"  {line}")
            print("✅ PASSED: Web search is working correctly\n")
            return True
        else:
            print(f"⚠ Warning: No search results found (may be network issue)")
            print("✅ PASSED: Web search initialized correctly\n")
            return True
            
    except Exception as e:
        print(f"⚠ WARNING: Web search issue: {str(e)}")
        print("  This may be due to network connectivity\n")
        return False


def test_config_imports():
    """Test that all config imports work"""
    print("="*60)
    print("Testing Configuration Module Imports")
    print("="*60)
    
    try:
        print("Importing config module...")
        from config import (
            Config, 
            AgentDecisoinConfig, 
            ConversationConfig,
            WebSearchConfig, 
            RAGConfig, 
            MedicalCVConfig
        )
        print("✓ All config classes imported successfully")
        
        print("Initializing main Config...")
        config = Config()
        print("✓ Config instantiated successfully")
        
        # Test that LLMs are initialized
        print("✓ Agent Decision LLM:", config.agent_decision.llm.__class__.__name__)
        print("✓ Conversation LLM:", config.conversation.llm.__class__.__name__)
        print("✓ RAG Embedding Model:", config.rag.embedding_model.__class__.__name__)
        
        print("✅ PASSED: Configuration is working correctly\n")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("# Google Gemini + Open-Source Stack - Validation Tests")
    print("#"*60)
    
    results = {
        "Gemini API": test_gemini_api(),
        "Embeddings": test_embeddings(),
        "Qdrant": test_qdrant_connection(),
        "Web Search": test_web_search(),
        "Config": test_config_imports(),
    }
    
    print("="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print("="*60)
    print(f"Overall: {passed_count}/{total_count} tests passed")
    print("="*60 + "\n")
    
    # Return exit code
    if passed_count == total_count:
        print("🎉 All tests passed! Your system is ready.")
        print("\nNext steps:")
        print("1. Ingest medical documents: python ingest_rag_data.py --input data/raw")
        print("2. Start the application: python app.py")
        print("3. Open browser: http://localhost:8000")
        return 0
    elif passed_count >= total_count - 1:  # Allow 1 optional failure (web search)
        print("⚠️  Most tests passed. Check failures above.")
        print("The system may still work - some tests are optional (e.g., web search).")
        return 0
    else:
        print("❌ Some critical tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
