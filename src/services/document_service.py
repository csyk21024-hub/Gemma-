"""
Document Processing Service - Handles PDF and Word document processing
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from pathlib import Path

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


@dataclass
class DocumentInfo:
    """Information about a processed document"""
    filename: str
    file_type: str
    page_count: int
    text_content: str
    metadata: Dict[str, Any]


class DocumentService:
    """Service for processing PDF and Word documents"""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc'}
    
    def __init__(self, cache_dir: str = "cache"):
        """Initialize document service"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.processed_documents: Dict[str, DocumentInfo] = {}
    
    def is_supported(self, filepath: str) -> bool:
        """Check if a file type is supported"""
        ext = Path(filepath).suffix.lower()
        return ext in self.SUPPORTED_EXTENSIONS
    
    def process_file(self, filepath: str) -> Optional[DocumentInfo]:
        """Process a file and extract its content"""
        if not os.path.exists(filepath):
            return None
        
        ext = Path(filepath).suffix.lower()
        
        if ext == '.pdf':
            return self._process_pdf(filepath)
        elif ext in {'.docx', '.doc'}:
            return self._process_word(filepath)
        
        return None
    
    def _process_pdf(self, filepath: str) -> Optional[DocumentInfo]:
        """Process a PDF file"""
        text_content = ""
        page_count = 0
        metadata: Dict[str, Any] = {}
        
        # Try pdfplumber first (better extraction)
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(filepath) as pdf:
                    page_count = len(pdf.pages)
                    text_parts = []
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    text_content = "\n\n".join(text_parts)
                    metadata = pdf.metadata or {}
            except Exception:
                pass
        
        # Fallback to PyPDF2
        if not text_content and PYPDF2_AVAILABLE:
            try:
                with open(filepath, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    page_count = len(reader.pages)
                    text_parts = []
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                    text_content = "\n\n".join(text_parts)
                    if reader.metadata:
                        metadata = dict(reader.metadata)
            except Exception:
                pass
        
        if not text_content:
            text_content = "[PDF内容を抽出できませんでした]"
        
        doc_info = DocumentInfo(
            filename=os.path.basename(filepath),
            file_type="PDF",
            page_count=page_count,
            text_content=text_content,
            metadata=metadata
        )
        
        self.processed_documents[filepath] = doc_info
        return doc_info
    
    def _process_word(self, filepath: str) -> Optional[DocumentInfo]:
        """Process a Word document"""
        if not DOCX_AVAILABLE:
            return DocumentInfo(
                filename=os.path.basename(filepath),
                file_type="Word",
                page_count=0,
                text_content="[python-docx ライブラリがインストールされていません]",
                metadata={}
            )
        
        try:
            doc = DocxDocument(filepath)
            
            # Extract text from paragraphs
            text_parts = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text_parts.append(para.text)
            
            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text for cell in row.cells if cell.text.strip())
                    if row_text:
                        text_parts.append(row_text)
            
            text_content = "\n\n".join(text_parts)
            
            # Get metadata from core properties
            metadata = {}
            if doc.core_properties:
                props = doc.core_properties
                if props.title:
                    metadata['title'] = props.title
                if props.author:
                    metadata['author'] = props.author
                if props.created:
                    metadata['created'] = str(props.created)
            
            doc_info = DocumentInfo(
                filename=os.path.basename(filepath),
                file_type="Word",
                page_count=len(text_parts),  # Approximate
                text_content=text_content if text_content else "[ドキュメントは空です]",
                metadata=metadata
            )
            
            self.processed_documents[filepath] = doc_info
            return doc_info
            
        except Exception as e:
            return DocumentInfo(
                filename=os.path.basename(filepath),
                file_type="Word",
                page_count=0,
                text_content=f"[エラー: {e}]",
                metadata={}
            )
    
    def get_cached_document(self, filepath: str) -> Optional[DocumentInfo]:
        """Get a previously processed document from cache"""
        return self.processed_documents.get(filepath)
    
    def clear_cache(self) -> None:
        """Clear the document cache"""
        self.processed_documents.clear()
    
    def get_text_preview(self, doc_info: DocumentInfo, max_chars: int = 500) -> str:
        """Get a text preview of a document"""
        text = doc_info.text_content
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "..."
    
    def get_document_summary_prompt(self, doc_info: DocumentInfo) -> str:
        """Generate a prompt for summarizing the document"""
        return f"""ドキュメント情報:
ファイル名: {doc_info.filename}
種類: {doc_info.file_type}
ページ数: {doc_info.page_count}

内容:
{doc_info.text_content}"""


class EducationModeService:
    """Service for education mode - learning from documents"""
    
    def __init__(self, learned_documents_path: str = "learned_documents"):
        """Initialize education mode service"""
        self.documents_path = Path(learned_documents_path)
        self.documents_path.mkdir(parents=True, exist_ok=True)
        self.document_service = DocumentService()
        self.knowledge_base: Dict[str, DocumentInfo] = {}
    
    def add_document(self, filepath: str) -> bool:
        """Add a document to the knowledge base"""
        doc_info = self.document_service.process_file(filepath)
        if doc_info:
            self.knowledge_base[filepath] = doc_info
            return True
        return False
    
    def remove_document(self, filepath: str) -> bool:
        """Remove a document from the knowledge base"""
        if filepath in self.knowledge_base:
            del self.knowledge_base[filepath]
            return True
        return False
    
    def get_context_for_query(self, query: str, max_context_length: int = 4000) -> str:
        """Get relevant context from knowledge base for a query"""
        if not self.knowledge_base:
            return ""
        
        # Simple approach: concatenate all document contents
        # In production, you'd want semantic search/embeddings
        context_parts = []
        current_length = 0
        
        for doc_info in self.knowledge_base.values():
            doc_text = f"[{doc_info.filename}]\n{doc_info.text_content}"
            if current_length + len(doc_text) <= max_context_length:
                context_parts.append(doc_text)
                current_length += len(doc_text)
            else:
                # Add truncated version
                remaining = max_context_length - current_length
                if remaining > 100:
                    context_parts.append(f"[{doc_info.filename}]\n{doc_info.text_content[:remaining]}...")
                break
        
        return "\n\n---\n\n".join(context_parts)
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        total_chars = sum(len(doc.text_content) for doc in self.knowledge_base.values())
        total_pages = sum(doc.page_count for doc in self.knowledge_base.values())
        
        return {
            "document_count": len(self.knowledge_base),
            "total_characters": total_chars,
            "total_pages": total_pages,
            "documents": [doc.filename for doc in self.knowledge_base.values()]
        }
    
    def list_documents(self) -> List[str]:
        """List all documents in the knowledge base"""
        return list(self.knowledge_base.keys())
    
    def clear_knowledge_base(self) -> None:
        """Clear all documents from the knowledge base"""
        self.knowledge_base.clear()
