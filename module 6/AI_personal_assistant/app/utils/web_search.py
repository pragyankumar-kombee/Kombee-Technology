import requests
from datetime import datetime
from duckduckgo_search import DDGS


class WebSearchTool:
    """Tool for searching the web and getting real-time information"""
    
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query, max_results=5):
        """
        Search the web using DuckDuckGo
        Returns a list of search results with title, snippet, and link
        """
        try:
            results = []
            search_results = self.ddgs.text(query, max_results=max_results)
            
            for result in search_results:
                results.append({
                    'title': result.get('title', ''),
                    'snippet': result.get('body', ''),
                    'link': result.get('href', '')
                })
            
            return results
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []
    
    def get_current_date(self):
        """Get current date and time"""
        return datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    def should_search(self, query):
        """
        Determine if a query needs web search
        Returns True if query is about current events, news, weather, etc.
        """
        search_keywords = [
            'today', 'now', 'current', 'latest', 'recent', 'news',
            'weather', 'stock', 'price', 'what is happening',
            '2024', '2025', '2026', 'this year', 'this month',
            'who is', 'what happened', 'when did', 'score',
            'update', 'breaking', 'live'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in search_keywords)
    
    def format_search_results(self, results):
        """Format search results into a readable string"""
        if not results:
            return "No search results found."
        
        formatted = "Here's what I found from the web:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. {result['title']}\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   Source: {result['link']}\n\n"
        
        return formatted
