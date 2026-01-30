"""
Wrapper to make Sentence-Transformers compatible with LangChain's embedding interface.
This allows SentenceTransformer to be used directly with LangChain components like QdrantVectorStore.
"""

from typing import List
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer


class SentenceTransformerEmbeddings(Embeddings):
    """
    Wrapper class to make SentenceTransformer compatible with LangChain's Embeddings interface.
    
    This allows SentenceTransformer models to be used seamlessly with LangChain components
    like QdrantVectorStore.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", model_kwargs: dict = None, 
                 encode_kwargs: dict = None):
        """
        Initialize the SentenceTransformerEmbeddings wrapper.
        
        Args:
            model_name: Name of the SentenceTransformer model to use
            model_kwargs: Keyword arguments to pass to SentenceTransformer initialization
            encode_kwargs: Keyword arguments to pass to the encode method
        """
        self.model_name = model_name
        self.model_kwargs = model_kwargs or {}
        self.encode_kwargs = encode_kwargs or {"show_progress_bar": False}
        
        # Initialize the SentenceTransformer model
        self.model = SentenceTransformer(model_name, **self.model_kwargs)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        embeddings = self.model.encode(texts, **self.encode_kwargs)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query text.
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding as a list of floats
        """
        embedding = self.model.encode(text, **self.encode_kwargs)
        return embedding.tolist()
