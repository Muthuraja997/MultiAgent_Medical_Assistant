"""
Open-source web search implementation using LangChain's DuckDuckGo search tool.
No API key required - completely free and open-source.
"""

import logging
from typing import List, Dict, Any
from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults


class OpenSourceWebSearch:
    """
    Web search implementation using DuckDuckGo - open-source alternative to Tavily.
    No API key or authentication required.
    """
    
    def __init__(self, max_results: int = 5):
        """
        Initialize the open-source web search agent.
        
        Args:
            max_results: Maximum number of search results to return
        """
        self.logger = logging.getLogger(__name__)
        self.max_results = max_results
        self.search_tool = DuckDuckGoSearchResults(max_results=max_results)
    
    def search(self, query: str) -> str:
        """
        Perform a web search using DuckDuckGo.
        
        Args:
            query: Search query string
            
        Returns:
            Formatted search results as a string
        """
        try:
            # Strip any surrounding quotes from the query
            query = query.strip('"\'')
            self.logger.info(f"Performing web search for: {query}")
            
            # Invoke DuckDuckGo search
            search_results = self.search_tool.invoke(query)
            
            if search_results and len(search_results) > 0:
                self.logger.info(f"Found {len(search_results)} results")
                # Parse and format results
                formatted_results = self._format_results(search_results)
                return formatted_results
            else:
                return "No relevant results found."
                
        except Exception as e:
            self.logger.error(f"Error during web search: {e}")
            return f"Error retrieving web search results: {e}"
    
    def _format_results(self, results: Any) -> str:
        """
        Format search results into a readable string.
        
        Args:
            results: Search results from DuckDuckGo
            
        Returns:
            Formatted results string
        """
        try:
            # DuckDuckGoSearchResults returns a list of dictionaries or formatted strings
            if isinstance(results, str):
                return results
            elif isinstance(results, list):
                formatted = []
                for i, result in enumerate(results, 1):
                    if isinstance(result, dict):
                        title = result.get('title', 'N/A')
                        link = result.get('link', 'N/A')
                        snippet = result.get('snippet', 'N/A')
                        formatted.append(f"Result {i}:\ntitle: {title}\nurl: {link}\ncontent: {snippet}\n")
                    else:
                        formatted.append(f"Result {i}: {result}\n")
                return "---\n".join(formatted)
            else:
                return str(results)
                
        except Exception as e:
            self.logger.error(f"Error formatting results: {e}")
            return str(results)


class SearchWrapper:
    """
    Unified search interface that supports both Tavily (if API key available) 
    and DuckDuckGo (open-source fallback).
    """
    
    def __init__(self, tavily_api_key: str = None, max_results: int = 5):
        """
        Initialize the search wrapper.
        
        Args:
            tavily_api_key: Optional Tavily API key. If not provided, uses DuckDuckGo.
            max_results: Maximum number of search results to return
        """
        self.logger = logging.getLogger(__name__)
        self.max_results = max_results
        self.use_tavily = False
        
        # Try to use Tavily if API key is available
        if tavily_api_key:
            try:
                from langchain_community.tools.tavily_search import TavilySearchResults
                self.tavily_search = TavilySearchResults(max_results=max_results)
                self.use_tavily = True
                self.logger.info("Using Tavily Search API")
            except Exception as e:
                self.logger.warning(f"Tavily API not available, falling back to DuckDuckGo: {e}")
                self.search_engine = OpenSourceWebSearch(max_results=max_results)
        else:
            # Use open-source DuckDuckGo
            self.logger.info("Using open-source DuckDuckGo search")
            self.search_engine = OpenSourceWebSearch(max_results=max_results)
    
    def search(self, query: str) -> str:
        """
        Perform a web search using the configured backend.
        
        Args:
            query: Search query string
            
        Returns:
            Formatted search results
        """
        if self.use_tavily:
            try:
                query = query.strip('"\'')
                search_results = self.tavily_search.invoke(query)
                if len(search_results):
                    return "\n".join(["title: " + str(res.get("title", "")) + " - " + 
                                    "url: " + str(res.get("url", "")) + " - " + 
                                    "content: " + str(res.get("content", "")) + " - " + 
                                    "score: " + str(res.get("score", "")) 
                                    for res in search_results])
                return "No relevant results found."
            except Exception as e:
                self.logger.error(f"Tavily search failed, falling back to DuckDuckGo: {e}")
                return self.search_engine.search(query)
        else:
            return self.search_engine.search(query)


# Backwards compatibility: some modules expect `UnifiedSearchTool` symbol.
# Export an alias so older imports keep working.
UnifiedSearchTool = SearchWrapper
