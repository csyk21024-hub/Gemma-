"""
Tests for the Document Service
"""

import pytest
import sys
import os
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.document_service import DocumentService, EducationModeService, DocumentInfo


class TestDocumentService:
    """Tests for DocumentService"""
    
    def test_init(self):
        """Test service initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = DocumentService(cache_dir=tmpdir)
            assert service.cache_dir.exists()
    
    def test_is_supported_pdf(self):
        """Test PDF is supported"""
        service = DocumentService()
        assert service.is_supported("test.pdf") is True
    
    def test_is_supported_docx(self):
        """Test DOCX is supported"""
        service = DocumentService()
        assert service.is_supported("test.docx") is True
    
    def test_is_supported_doc(self):
        """Test DOC is supported"""
        service = DocumentService()
        assert service.is_supported("test.doc") is True
    
    def test_is_supported_unsupported(self):
        """Test unsupported file types"""
        service = DocumentService()
        assert service.is_supported("test.txt") is False
        assert service.is_supported("test.xlsx") is False
    
    def test_process_nonexistent_file(self):
        """Test processing non-existent file returns None"""
        service = DocumentService()
        result = service.process_file("/nonexistent/file.pdf")
        assert result is None
    
    def test_get_text_preview(self):
        """Test text preview generation"""
        service = DocumentService()
        doc_info = DocumentInfo(
            filename="test.pdf",
            file_type="PDF",
            page_count=1,
            text_content="A" * 1000,
            metadata={}
        )
        
        preview = service.get_text_preview(doc_info, max_chars=100)
        assert len(preview) == 103  # 100 chars + "..."
        assert preview.endswith("...")
    
    def test_clear_cache(self):
        """Test clearing cache"""
        service = DocumentService()
        service.processed_documents["test"] = DocumentInfo(
            filename="test.pdf",
            file_type="PDF",
            page_count=1,
            text_content="test",
            metadata={}
        )
        
        service.clear_cache()
        assert len(service.processed_documents) == 0


class TestEducationModeService:
    """Tests for EducationModeService"""
    
    def test_init(self):
        """Test service initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            service = EducationModeService(learned_documents_path=tmpdir)
            assert service.documents_path.exists()
    
    def test_add_document_nonexistent(self):
        """Test adding non-existent document returns False"""
        service = EducationModeService()
        result = service.add_document("/nonexistent/file.pdf")
        assert result is False
    
    def test_get_knowledge_base_stats_empty(self):
        """Test getting stats from empty knowledge base"""
        service = EducationModeService()
        stats = service.get_knowledge_base_stats()
        
        assert stats["document_count"] == 0
        assert stats["total_characters"] == 0
        assert stats["total_pages"] == 0
    
    def test_list_documents_empty(self):
        """Test listing documents from empty knowledge base"""
        service = EducationModeService()
        docs = service.list_documents()
        assert len(docs) == 0
    
    def test_clear_knowledge_base(self):
        """Test clearing knowledge base"""
        service = EducationModeService()
        # Manually add a document to knowledge base
        service.knowledge_base["test"] = DocumentInfo(
            filename="test.pdf",
            file_type="PDF",
            page_count=1,
            text_content="test",
            metadata={}
        )
        
        service.clear_knowledge_base()
        assert len(service.knowledge_base) == 0
    
    def test_get_context_for_query_empty(self):
        """Test getting context from empty knowledge base"""
        service = EducationModeService()
        context = service.get_context_for_query("test query")
        assert context == ""
    
    def test_get_context_with_relevance(self):
        """Test getting context uses keyword relevance scoring"""
        service = EducationModeService()
        
        # Manually add documents to knowledge base
        service.knowledge_base["doc1"] = DocumentInfo(
            filename="general.pdf",
            file_type="PDF",
            page_count=1,
            text_content="This is a general document with no specific keywords",
            metadata={}
        )
        service.knowledge_base["doc2"] = DocumentInfo(
            filename="python.pdf",
            file_type="PDF",
            page_count=1,
            text_content="This document discusses Python programming and Python libraries",
            metadata={}
        )
        
        # Query about Python should return python.pdf content first
        context = service.get_context_for_query("Python programming")
        
        # The context should contain both documents
        assert "python.pdf" in context
        assert "general.pdf" in context
        # Python document should appear first due to higher relevance
        python_pos = context.find("python.pdf")
        general_pos = context.find("general.pdf")
        assert python_pos < general_pos


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
