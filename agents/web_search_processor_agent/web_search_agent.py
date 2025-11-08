import requests
from typing import Dict

from .pubmed_search import PubmedSearchAgent
from .opensource_search import UnifiedSearchTool  # Use open-source search instead of Tavily

class WebSearchAgent:
    """
    Agent responsible for retrieving real-time medical information from web sources.
    Uses open-source DuckDuckGo search as default (Gemini-only stack).
    """
    
    def __init__(self, config):
        # Use open-source search - no API key needed
        self.search_tool = UnifiedSearchTool()
        
        # self.pubmed_search_agent = PubmedSearchAgent()
        # self.pubmed_api_url = config.pubmed_api_url
    
    def search(self, query: str) -> str:
        """
        Perform web searches using open-source tools (DuckDuckGo).
        """
        # print(f"[WebSearchAgent] Searching for: {query}")
        
        search_results = self.search_tool.search(query=query)
        # pubmed_results = self.pubmed_search_agent.search_pubmed(self.pubmed_api_url, query)
        
        return f"Search Results:\n{search_results}\n"
        # \nPubMed Results:\n{pubmed_results}"
