"""
Web Search Service - Handles online search functionality
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import html

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class SearchResult:
    """Represents a search result"""
    title: str
    url: str
    snippet: str
    source: str = ""


class WebSearchService:
    """Service for performing web searches"""
    
    def __init__(self):
        """Initialize web search service"""
        self._is_available = DDGS_AVAILABLE
    
    def is_available(self) -> bool:
        """Check if web search is available"""
        return self._is_available
    
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Perform a web search"""
        if not self._is_available:
            return self._get_demo_results(query)
        
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append(SearchResult(
                        title=html.unescape(r.get('title', '')),
                        url=r.get('href', ''),
                        snippet=html.unescape(r.get('body', '')),
                        source=self._extract_domain(r.get('href', ''))
                    ))
            return results
        except Exception:
            return self._get_demo_results(query)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except (ImportError, ValueError, AttributeError):
            return ""
    
    def _get_demo_results(self, query: str) -> List[SearchResult]:
        """Get demo results when search is not available"""
        return [
            SearchResult(
                title=f"検索結果サンプル: {query}",
                url="https://example.com/result1",
                snippet="これはデモ検索結果です。duckduckgo-search パッケージがインストールされていないか、検索サービスが利用できません。",
                source="example.com"
            ),
            SearchResult(
                title="検索機能について",
                url="https://example.com/about",
                snippet="実際の検索機能を使用するには、インターネット接続とduckduckgo-searchパッケージが必要です。",
                source="example.com"
            )
        ]
    
    def format_results_for_prompt(self, results: List[SearchResult]) -> str:
        """Format search results for use in a prompt"""
        if not results:
            return "検索結果が見つかりませんでした。"
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"""【結果 {i}】
タイトル: {result.title}
URL: {result.url}
概要: {result.snippet}
""")
        
        return "\n".join(formatted)
    
    def fetch_page_content(self, url: str, max_length: int = 5000) -> Optional[str]:
        """Fetch and extract text content from a web page"""
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up multiple newlines
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = '\n'.join(lines)
            
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            return text
            
        except Exception:
            return None
