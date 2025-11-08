"""
Configuration file for the Multi-Agent Medical Chatbot

This file contains all the configuration parameters for the project.

If you want to change the LLM and Embedding model:

you can do it by changing all 'llm' and 'embedding_model' variables present in multiple classes below.

Each llm definition has unique temperature value relevant to the specific class. 

Current Configuration:
- LLM Provider: Google Gemini API (ChatGoogleGenerativeAI)
- Embedding Model: Sentence-Transformers (all-MiniLM-L6-v2, 384-dim local embeddings)
- Vector DB: Qdrant (localhost:6333)
- Web Search: LangChain open-source tools
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
# Lazy import for embeddings to avoid triggering heavy dependencies
# from agents.rag_agent.embeddings_wrapper import SentenceTransformerEmbeddings

# Load environment variables from .env file
load_dotenv()

# Lazy LLM initialization to avoid hanging on app startup
def get_gemini_llm(temperature=0.1):
    """Factory function for lazy ChatGoogleGenerativeAI initialization"""
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=temperature,
        convert_system_message_to_human=True
    )

class AgentDecisoinConfig:
    def __init__(self):
        self._llm = None  # Lazy initialization
        self._temperature = 0.1
    
    @property
    def llm(self):
        """Lazy property to initialize LLM only when needed"""
        if self._llm is None:
            self._llm = get_gemini_llm(self._temperature)
        return self._llm

class ConversationConfig:
    def __init__(self):
        self._llm = None  # Lazy initialization
        self._temperature = 0.7
    
    @property
    def llm(self):
        """Lazy property to initialize LLM only when needed"""
        if self._llm is None:
            self._llm = get_gemini_llm(self._temperature)
        return self._llm

class WebSearchConfig:
    def __init__(self):
        self._llm = None  # Lazy initialization
        self._temperature = 0.3
    
    @property
    def llm(self):
        """Lazy property to initialize LLM only when needed"""
        if self._llm is None:
            self._llm = get_gemini_llm(self._temperature)
        return self._llm
    
    context_limit = 20  # include last 20 messages (10 Q&A pairs) in history

class RAGConfig:
    def __init__(self):
        self.vector_db_type = "qdrant"
        self.embedding_dim = 384  # Sentence-Transformers all-MiniLM-L6-v2 dimension
        self.distance_metric = "Cosine"  # Add this with a default value
        self.use_local = True  # Add this with a default value
        self.vector_local_path = "./data/qdrant_db"  # Add this with a default value
        self.doc_local_path = "./data/docs_db"
        self.parsed_content_dir = "./data/parsed_docs"
        self.url = os.getenv("QDRANT_URL", "http://localhost:6333")  # Default to localhost
        self.api_key = os.getenv("QDRANT_API_KEY")
        self.collection_name = "medical_assistance_rag"  # Ensure a valid name
        self.chunk_size = 512  # Modify based on documents and performance
        self.chunk_overlap = 50  # Modify based on documents and performance
        
        # Lazy initialization for embedding model (avoids large downloads at startup)
        self._embedding_model = None
        
        # Lazy initialization for Gemini LLMs
        self._llm = None
        self._summarizer_model = None
        self._chunker_model = None
        self._response_generator_model = None
        
        self.top_k = 5
        self.vector_search_type = 'similarity'  # or 'mmr'
        self.huggingface_token = os.getenv("HUGGINGFACE_TOKEN")
        
        self.reranker_model = "cross-encoder/ms-marco-TinyBERT-L-6"
        self.reranker_top_k = 3

        self.max_context_length = 8192  # (Change based on your need) # 1024 proved to be too low (retrieved content length > context length = no context added) in formatting context in response_generator code

        self.include_sources = True  # Show links to reference documents and images along with corresponding query response

        # ADJUST ACCORDING TO ASSISTANT'S BEHAVIOUR BASED ON THE DATA INGESTED:
        self.min_retrieval_confidence = 0.40  # The auto routing from RAG agent to WEB_SEARCH agent is dependent on this value

        self.context_limit = 20     # include last 20 messages (10 Q&A pairs) in history
    
    @property
    def embedding_model(self):
        """Lazy getter for embedding model"""
        if self._embedding_model is None:
            from agents.rag_agent.embeddings_wrapper import SentenceTransformerEmbeddings
            self._embedding_model = SentenceTransformerEmbeddings(
                model_name='all-MiniLM-L6-v2',
                encode_kwargs={'show_progress_bar': False}
            )
        return self._embedding_model
    
    @property
    def llm(self):
        """Lazy getter for general LLM"""
        if self._llm is None:
            self._llm = get_gemini_llm(0.3)
        return self._llm
    
    @property
    def summarizer_model(self):
        """Lazy getter for summarizer model"""
        if self._summarizer_model is None:
            self._summarizer_model = get_gemini_llm(0.5)
        return self._summarizer_model
    
    @property
    def chunker_model(self):
        """Lazy getter for chunker model"""
        if self._chunker_model is None:
            self._chunker_model = get_gemini_llm(0.0)
        return self._chunker_model
    
    @property
    def response_generator_model(self):
        """Lazy getter for response generator model"""
        if self._response_generator_model is None:
            self._response_generator_model = get_gemini_llm(0.3)
        return self._response_generator_model

class MedicalCVConfig:
    def __init__(self):
        self.brain_tumor_model_path = "./agents/image_analysis_agent/brain_tumor_agent/models/brain_tumor_segmentation.pth"
        self.chest_xray_model_path = "./agents/image_analysis_agent/chest_xray_agent/models/covid_chest_xray_model.pth"
        self.skin_lesion_model_path = "./agents/image_analysis_agent/skin_lesion_agent/models/checkpointN25_.pth.tar"
        self.skin_lesion_segmentation_output_path = "./uploads/skin_lesion_output/segmentation_plot.png"
        self._llm = None  # Lazy initialization
        self._temperature = 0.1
    
    @property
    def llm(self):
        """Lazy property to initialize LLM only when needed"""
        if self._llm is None:
            self._llm = get_gemini_llm(self._temperature)
        return self._llm

class SpeechConfig:
    def __init__(self):
        self.eleven_labs_api_key = os.getenv("ELEVEN_LABS_API_KEY")  # Replace with your actual key
        self.eleven_labs_voice_id = "21m00Tcm4TlvDq8ikWAM"    # Default voice ID (Rachel)

class ValidationConfig:
    def __init__(self):
        self.require_validation = {
            "CONVERSATION_AGENT": False,
            "RAG_AGENT": False,
            "WEB_SEARCH_AGENT": False,
            "BRAIN_TUMOR_AGENT": True,
            "CHEST_XRAY_AGENT": True,
            "SKIN_LESION_AGENT": True
        }
        self.validation_timeout = 300
        self.default_action = "reject"

class APIConfig:
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 8000
        self.debug = True
        self.rate_limit = 10
        self.max_image_upload_size = 5  # max upload size in MB

class UIConfig:
    def __init__(self):
        self.theme = "light"
        # self.max_chat_history = 50
        self.enable_speech = True
        self.enable_image_upload = True

class Config:
    def __init__(self):
        self.agent_decision = AgentDecisoinConfig()
        self.conversation = ConversationConfig()
        self.rag = RAGConfig()
        self.medical_cv = MedicalCVConfig()
        self.web_search = WebSearchConfig()
        self.api = APIConfig()
        self.speech = SpeechConfig()
        self.validation = ValidationConfig()
        self.ui = UIConfig()
        self.eleven_labs_api_key = os.getenv("ELEVEN_LABS_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.max_conversation_history = 20  # Include last 20 messsages (10 Q&A pairs) in history

# # Example usage
# config = Config()