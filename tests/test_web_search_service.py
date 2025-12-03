"""
Tests for the Web Search Service
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.web_search_service import WebSearchService, SearchResult


class TestSearchResult:
    """Tests for SearchResult dataclass"""
    
    def test_create_result(self):
        """Test creating a search result"""
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            source="example.com"
        )
        
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.snippet == "Test snippet"
        assert result.source == "example.com"


class TestWebSearchService:
    """Tests for WebSearchService"""
    
    def test_init(self):
        """Test service initialization"""
        service = WebSearchService()
        # Service should initialize without error
        assert service is not None
    
    def test_format_results_empty(self):
        """Test formatting empty results"""
        service = WebSearchService()
        formatted = service.format_results_for_prompt([])
        assert formatted == "検索結果が見つかりませんでした。"
    
    def test_format_results(self):
        """Test formatting search results"""
        service = WebSearchService()
        results = [
            SearchResult(
                title="Test Title",
                url="https://example.com",
                snippet="Test snippet",
                source="example.com"
            )
        ]
        
        formatted = service.format_results_for_prompt(results)
        assert "Test Title" in formatted
        assert "https://example.com" in formatted
        assert "Test snippet" in formatted
    
    def test_extract_domain(self):
        """Test domain extraction from URL"""
        service = WebSearchService()
        domain = service._extract_domain("https://www.example.com/path/to/page")
        assert domain == "www.example.com"
    
    def test_demo_results(self):
        """Test demo results generation"""
        service = WebSearchService()
        results = service._get_demo_results("test query")
        
        assert len(results) > 0
        assert all(isinstance(r, SearchResult) for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
