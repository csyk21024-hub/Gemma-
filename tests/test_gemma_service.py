"""
Tests for the Gemma Service
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.gemma_service import GemmaService, GemmaModel, ChatMessage


class TestGemmaModel:
    """Tests for GemmaModel enum"""
    
    def test_model_values(self):
        """Test that model values are correct"""
        assert GemmaModel.GEMMA_1B.value == "gemma-3-1b"
        assert GemmaModel.GEMMA_4B.value == "gemma-3-4b"
        assert GemmaModel.GEMMA_12B.value == "gemma-3-12b"
        assert GemmaModel.GEMMA_27B.value == "gemma-3-27b"
    
    def test_from_string(self):
        """Test creating model from string"""
        model = GemmaModel.from_string("gemma-3-4b")
        assert model == GemmaModel.GEMMA_4B
    
    def test_from_string_invalid(self):
        """Test creating model from invalid string returns default"""
        model = GemmaModel.from_string("invalid-model")
        assert model == GemmaModel.GEMMA_4B


class TestChatMessage:
    """Tests for ChatMessage dataclass"""
    
    def test_create_message(self):
        """Test creating a chat message"""
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"


class TestGemmaService:
    """Tests for GemmaService"""
    
    def test_init_demo_mode(self):
        """Test initialization in demo mode (no API key)"""
        service = GemmaService()
        assert service.is_demo_mode() is True
    
    def test_set_model(self):
        """Test setting model"""
        service = GemmaService()
        service.set_model("gemma-3-12b")
        assert service.model_name == "gemma-3-12b"
    
    def test_send_message_demo(self):
        """Test sending message in demo mode"""
        service = GemmaService()
        response = service.send_message("こんにちは")
        assert response is not None
        assert len(response) > 0
        assert "デモモード" in response
    
    def test_chat_history(self):
        """Test chat history is maintained"""
        service = GemmaService()
        service.send_message("テスト")
        
        history = service.get_history()
        assert len(history) == 2  # User message + assistant response
        assert history[0].role == "user"
        assert history[1].role == "assistant"
    
    def test_clear_history(self):
        """Test clearing chat history"""
        service = GemmaService()
        service.send_message("テスト")
        service.clear_history()
        
        history = service.get_history()
        assert len(history) == 0
    
    def test_get_model_info(self):
        """Test getting model info"""
        service = GemmaService(model="gemma-3-4b")
        info = service.get_model_info()
        
        assert info["model"] == "gemma-3-4b"
        assert "description" in info
        assert info["is_demo_mode"] is True
    
    def test_proofread_email_demo(self):
        """Test email proofreading in demo mode"""
        service = GemmaService()
        result = service.proofread_email("テストメール")
        assert result is not None
        assert "デモモード" in result
    
    def test_summarize_document_demo(self):
        """Test document summarization in demo mode"""
        service = GemmaService()
        result = service.summarize_document("テストドキュメント内容")
        assert result is not None
        assert "デモモード" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
