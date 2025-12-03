"""
Gemma AI Service - Handles integration with Google Gemma models
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GemmaModel(Enum):
    """Available Gemma models"""
    GEMMA_1B = "gemma-3-1b"
    GEMMA_4B = "gemma-3-4b"
    GEMMA_12B = "gemma-3-12b"
    GEMMA_27B = "gemma-3-27b"
    
    @classmethod
    def from_string(cls, model_str: str) -> "GemmaModel":
        """Create GemmaModel from string"""
        for model in cls:
            if model.value == model_str:
                return model
        return cls.GEMMA_4B  # Default


@dataclass
class ChatMessage:
    """Represents a chat message"""
    role: str  # 'user' or 'assistant'
    content: str


class GemmaService:
    """Service for interacting with Gemma AI models"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemma-3-4b"):
        """Initialize the Gemma service"""
        self.api_key = api_key or os.environ.get("GEMMA_API_KEY", "")
        self.model_name = model
        self.model = None
        self.chat_history: List[ChatMessage] = []
        self.temperature = 0.7
        self.max_tokens = 2048
        self._is_demo_mode = not bool(self.api_key)
        
        if GENAI_AVAILABLE and self.api_key:
            self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the Gemma model"""
        if not GENAI_AVAILABLE:
            return
        
        try:
            genai.configure(api_key=self.api_key)
            # Map our model names to Google's model names
            model_mapping = {
                "gemma-3-1b": "gemini-1.5-flash",  # Fallback for demo
                "gemma-3-4b": "gemini-1.5-flash",
                "gemma-3-12b": "gemini-1.5-pro",
                "gemma-3-27b": "gemini-1.5-pro"
            }
            google_model = model_mapping.get(self.model_name, "gemini-1.5-flash")
            self.model = genai.GenerativeModel(google_model)
        except Exception:
            self._is_demo_mode = True
    
    def set_model(self, model: str) -> None:
        """Change the current model"""
        self.model_name = model
        if GENAI_AVAILABLE and self.api_key:
            self._initialize_model()
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key and reinitialize"""
        self.api_key = api_key
        self._is_demo_mode = not bool(api_key)
        if GENAI_AVAILABLE and api_key:
            self._initialize_model()
    
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode (no API key)"""
        return self._is_demo_mode
    
    async def send_message_async(self, message: str, context: str = "") -> str:
        """Send a message and get a response asynchronously"""
        return self.send_message(message, context)
    
    def send_message(self, message: str, context: str = "") -> str:
        """Send a message and get a response"""
        # Add to history
        self.chat_history.append(ChatMessage(role="user", content=message))
        
        if self._is_demo_mode or self.model is None:
            response = self._get_demo_response(message, context)
        else:
            response = self._get_model_response(message, context)
        
        # Add response to history
        self.chat_history.append(ChatMessage(role="assistant", content=response))
        
        return response
    
    def _get_model_response(self, message: str, context: str = "") -> str:
        """Get response from the actual model"""
        try:
            # Build prompt with context
            prompt = ""
            if context:
                prompt += f"コンテキスト: {context}\n\n"
            prompt += message
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens
                )
            )
            return response.text
        except Exception as e:
            return f"エラーが発生しました: {e}"
    
    def _get_demo_response(self, message: str, context: str = "") -> str:
        """Get a demo response when no API key is available"""
        # Provide helpful demo responses based on the message content
        message_lower = message.lower()
        
        if "メール" in message or "mail" in message_lower or "添削" in message:
            return self._demo_email_response(message)
        elif "pdf" in message_lower or "要約" in message:
            return self._demo_summary_response(message)
        elif "検索" in message or "search" in message_lower:
            return self._demo_search_response(message)
        elif "教育" in message or "学習" in message:
            return self._demo_education_response(message)
        else:
            return self._demo_general_response(message)
    
    def _demo_email_response(self, message: str) -> str:
        """Demo response for email proofreading"""
        return """【デモモード】メール添削機能

こちらはデモモードです。実際のGemma APIキーを設定すると、以下のような機能が利用できます：

✓ メールの文法チェック
✓ ビジネス敬語の修正
✓ より適切な表現の提案
✓ 文章の構成改善

設定からAPIキーを入力してください。"""
    
    def _demo_summary_response(self, message: str) -> str:
        """Demo response for document summarization"""
        return """【デモモード】PDF要約機能

こちらはデモモードです。実際のGemma APIキーを設定すると、以下のような機能が利用できます：

✓ PDFドキュメントの内容抽出
✓ 要点の自動まとめ
✓ 重要なキーワードの抽出
✓ 章ごとの概要生成

設定からAPIキーを入力してください。"""
    
    def _demo_search_response(self, message: str) -> str:
        """Demo response for web search"""
        return """【デモモード】オンライン検索機能

こちらはデモモードです。実際のGemma APIキーを設定すると、以下のような機能が利用できます：

✓ ウェブ検索による情報収集
✓ 検索結果の要約
✓ 関連情報の提案
✓ ソースの引用

設定からAPIキーを入力してください。"""
    
    def _demo_education_response(self, message: str) -> str:
        """Demo response for education mode"""
        return """【デモモード】専門教育モード

こちらはデモモードです。実際のGemma APIキーを設定すると、以下のような機能が利用できます：

✓ PDF/Wordドキュメントからの学習
✓ 専門知識に基づく回答
✓ 業務サポート
✓ カスタム知識ベースの構築

設定からAPIキーを入力してください。"""
    
    def _demo_general_response(self, message: str) -> str:
        """Demo response for general questions"""
        return f"""【デモモード】

こんにちは！Gemmaサポートツールのデモモードです。

ご質問: 「{message[:50]}...」

このツールでは以下の機能をご利用いただけます：
1. 📧 メール添削
2. 📄 PDF要約
3. 🔍 オンライン検索
4. 📚 専門教育モード

実際の回答を得るには、設定画面でGemma APIキーを入力してください。"""
    
    def proofread_email(self, email_text: str) -> str:
        """Proofread an email and suggest improvements"""
        prompt = f"""以下のメール文を添削してください。
文法の誤り、敬語の使い方、より適切な表現があれば修正してください。
修正箇所は【】で囲み、修正理由も説明してください。

メール内容:
{email_text}

添削結果を日本語で回答してください。"""
        
        return self.send_message(prompt)
    
    def summarize_document(self, document_text: str, doc_type: str = "PDF") -> str:
        """Summarize a document"""
        prompt = f"""以下の{doc_type}ドキュメントの内容を要約してください。
主要なポイントを箇条書きでまとめ、全体の概要を3〜5文で説明してください。

ドキュメント内容:
{document_text}

要約を日本語で回答してください。"""
        
        return self.send_message(prompt)
    
    def answer_with_context(self, question: str, context: str) -> str:
        """Answer a question based on provided context (for education mode)"""
        prompt = f"""以下のコンテキスト情報に基づいて質問に回答してください。
コンテキストに含まれていない情報については、そのことを明示してください。

コンテキスト:
{context}

質問:
{question}

回答を日本語で提供してください。"""
        
        return self.send_message(prompt)
    
    def clear_history(self) -> None:
        """Clear chat history"""
        self.chat_history = []
    
    def get_history(self) -> List[ChatMessage]:
        """Get chat history"""
        return self.chat_history.copy()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        model_descriptions = {
            "gemma-3-1b": "軽量モデル（1B パラメータ）- 低スペックPC向け",
            "gemma-3-4b": "標準モデル（4B パラメータ）- バランスの取れた性能",
            "gemma-3-12b": "高性能モデル（12B パラメータ）- 高品質な回答",
            "gemma-3-27b": "最高性能モデル（27B パラメータ）- 最も高品質な回答"
        }
        
        return {
            "model": self.model_name,
            "description": model_descriptions.get(self.model_name, "不明なモデル"),
            "is_demo_mode": self._is_demo_mode,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
