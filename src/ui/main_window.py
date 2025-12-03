"""
Main Window - Primary UI for the Gemma Support Tool
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QTextEdit, QLineEdit, QPushButton,
    QLabel, QComboBox, QFileDialog, QListWidget, QListWidgetItem,
    QFrame, QScrollArea, QMessageBox, QToolBar, QStatusBar,
    QDialog, QFormLayout, QDialogButtonBox, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QAction, QIcon, QColor
import os

from src.services.gemma_service import GemmaService
from src.services.document_service import DocumentService, EducationModeService
from src.services.web_search_service import WebSearchService
from src.utils.config import get_config


class MessageWidget(QFrame):
    """Widget for displaying a single chat message"""
    
    def __init__(self, role: str, content: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Role label
        role_label = QLabel("あなた" if role == "user" else "Gemma")
        role_font = QFont()
        role_font.setBold(True)
        role_label.setFont(role_font)
        
        # Style based on role
        if role == "user":
            self.setStyleSheet("background-color: #e3f2fd; border-radius: 10px;")
            role_label.setStyleSheet("color: #1565c0;")
        else:
            self.setStyleSheet("background-color: #f5f5f5; border-radius: 10px;")
            role_label.setStyleSheet("color: #424242;")
        
        # Content label
        content_label = QLabel(content)
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        layout.addWidget(role_label)
        layout.addWidget(content_label)


class ChatPanel(QWidget):
    """Chat panel widget for the right side of the screen"""
    
    message_sent = pyqtSignal(str)
    
    def __init__(self, gemma_service: GemmaService, parent=None):
        super().__init__(parent)
        self.gemma_service = gemma_service
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the chat panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Title
        title = QLabel("💬 チャット")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Model selector
        model_layout = QHBoxLayout()
        model_label = QLabel("モデル:")
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "gemma-3-1b (軽量)",
            "gemma-3-4b (標準)",
            "gemma-3-12b (高性能)",
            "gemma-3-27b (最高性能)"
        ])
        self.model_combo.setCurrentIndex(1)  # Default to 4B
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)
        
        # Chat history scroll area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(10)
        
        self.chat_scroll.setWidget(self.chat_container)
        layout.addWidget(self.chat_scroll, 1)
        
        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("メッセージを入力...")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("送信")
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field, 1)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
        
        # Clear button
        self.clear_button = QPushButton("履歴をクリア")
        self.clear_button.clicked.connect(self.clear_history)
        layout.addWidget(self.clear_button)
    
    def on_model_changed(self, index: int):
        """Handle model selection change"""
        models = ["gemma-3-1b", "gemma-3-4b", "gemma-3-12b", "gemma-3-27b"]
        if 0 <= index < len(models):
            self.gemma_service.set_model(models[index])
            config = get_config()
            config.set_gemma_model(models[index])
    
    def send_message(self):
        """Send a message and get response"""
        message = self.input_field.text().strip()
        if not message:
            return
        
        self.input_field.clear()
        self.add_message("user", message)
        
        # Get response from Gemma
        response = self.gemma_service.send_message(message)
        self.add_message("assistant", response)
        
        self.message_sent.emit(message)
    
    def add_message(self, role: str, content: str):
        """Add a message to the chat history"""
        message_widget = MessageWidget(role, content)
        self.chat_layout.addWidget(message_widget)
        
        # Scroll to bottom
        self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        )
    
    def clear_history(self):
        """Clear chat history"""
        self.gemma_service.clear_history()
        
        # Remove all message widgets
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


class EmailPanel(QWidget):
    """Panel for email proofreading"""
    
    def __init__(self, gemma_service: GemmaService, parent=None):
        super().__init__(parent)
        self.gemma_service = gemma_service
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the email panel UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("📧 メール添削")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Input area
        input_label = QLabel("添削するメール本文:")
        layout.addWidget(input_label)
        
        self.email_input = QTextEdit()
        self.email_input.setPlaceholderText("ここにメール本文を入力してください...")
        layout.addWidget(self.email_input, 1)
        
        # Proofread button
        self.proofread_button = QPushButton("添削する")
        self.proofread_button.clicked.connect(self.proofread_email)
        layout.addWidget(self.proofread_button)
        
        # Output area
        output_label = QLabel("添削結果:")
        layout.addWidget(output_label)
        
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        layout.addWidget(self.result_output, 1)
    
    def proofread_email(self):
        """Proofread the email"""
        email_text = self.email_input.toPlainText().strip()
        if not email_text:
            QMessageBox.warning(self, "入力エラー", "メール本文を入力してください。")
            return
        
        self.proofread_button.setEnabled(False)
        self.result_output.setText("添削中...")
        
        result = self.gemma_service.proofread_email(email_text)
        self.result_output.setText(result)
        self.proofread_button.setEnabled(True)


class DocumentPanel(QWidget):
    """Panel for document summarization"""
    
    def __init__(self, gemma_service: GemmaService, document_service: DocumentService, parent=None):
        super().__init__(parent)
        self.gemma_service = gemma_service
        self.document_service = document_service
        self.current_file = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the document panel UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("📄 ドキュメント要約")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("ファイルが選択されていません")
        self.select_button = QPushButton("ファイルを選択")
        self.select_button.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label, 1)
        file_layout.addWidget(self.select_button)
        layout.addLayout(file_layout)
        
        # Document content preview
        preview_label = QLabel("ドキュメント内容プレビュー:")
        layout.addWidget(preview_label)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        layout.addWidget(self.preview_text, 1)
        
        # Summarize button
        self.summarize_button = QPushButton("要約する")
        self.summarize_button.clicked.connect(self.summarize_document)
        self.summarize_button.setEnabled(False)
        layout.addWidget(self.summarize_button)
        
        # Summary output
        summary_label = QLabel("要約結果:")
        layout.addWidget(summary_label)
        
        self.summary_output = QTextEdit()
        self.summary_output.setReadOnly(True)
        layout.addWidget(self.summary_output, 1)
    
    def select_file(self):
        """Select a file for summarization"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "ドキュメントを選択",
            "",
            "ドキュメント (*.pdf *.docx *.doc);;すべてのファイル (*)"
        )
        
        if filepath:
            self.current_file = filepath
            self.file_label.setText(os.path.basename(filepath))
            
            # Process the file
            doc_info = self.document_service.process_file(filepath)
            if doc_info:
                preview = self.document_service.get_text_preview(doc_info, 1000)
                self.preview_text.setText(preview)
                self.summarize_button.setEnabled(True)
            else:
                self.preview_text.setText("[ファイルを処理できませんでした]")
                self.summarize_button.setEnabled(False)
    
    def summarize_document(self):
        """Summarize the selected document"""
        if not self.current_file:
            return
        
        doc_info = self.document_service.get_cached_document(self.current_file)
        if not doc_info:
            return
        
        self.summarize_button.setEnabled(False)
        self.summary_output.setText("要約中...")
        
        result = self.gemma_service.summarize_document(
            doc_info.text_content,
            doc_info.file_type
        )
        self.summary_output.setText(result)
        self.summarize_button.setEnabled(True)


class SearchPanel(QWidget):
    """Panel for web search"""
    
    def __init__(self, gemma_service: GemmaService, search_service: WebSearchService, parent=None):
        super().__init__(parent)
        self.gemma_service = gemma_service
        self.search_service = search_service
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the search panel UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🔍 オンライン検索")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Search input
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("検索キーワードを入力...")
        self.search_input.returnPressed.connect(self.perform_search)
        
        self.search_button = QPushButton("検索")
        self.search_button.clicked.connect(self.perform_search)
        
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        # Results list
        results_label = QLabel("検索結果:")
        layout.addWidget(results_label)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.analyze_result)
        layout.addWidget(self.results_list, 1)
        
        # Analyze button
        self.analyze_button = QPushButton("選択した結果を分析")
        self.analyze_button.clicked.connect(self.analyze_selected)
        layout.addWidget(self.analyze_button)
        
        # Analysis output
        analysis_label = QLabel("分析結果:")
        layout.addWidget(analysis_label)
        
        self.analysis_output = QTextEdit()
        self.analysis_output.setReadOnly(True)
        layout.addWidget(self.analysis_output, 1)
    
    def perform_search(self):
        """Perform a web search"""
        query = self.search_input.text().strip()
        if not query:
            return
        
        self.search_button.setEnabled(False)
        self.results_list.clear()
        
        results = self.search_service.search(query)
        
        for result in results:
            item = QListWidgetItem(f"{result.title}\n{result.snippet[:100]}...")
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.results_list.addItem(item)
        
        self.search_button.setEnabled(True)
    
    def analyze_result(self, item: QListWidgetItem):
        """Analyze a search result"""
        result = item.data(Qt.ItemDataRole.UserRole)
        if result:
            self.analysis_output.setText("分析中...")
            
            # Get formatted results for context
            formatted = f"タイトル: {result.title}\nURL: {result.url}\n概要: {result.snippet}"
            
            response = self.gemma_service.send_message(
                "以下の検索結果について詳しく説明してください。",
                context=formatted
            )
            self.analysis_output.setText(response)
    
    def analyze_selected(self):
        """Analyze the selected result"""
        current_item = self.results_list.currentItem()
        if current_item:
            self.analyze_result(current_item)


class EducationPanel(QWidget):
    """Panel for education mode"""
    
    def __init__(self, gemma_service: GemmaService, education_service: EducationModeService, parent=None):
        super().__init__(parent)
        self.gemma_service = gemma_service
        self.education_service = education_service
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the education panel UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("📚 専門教育モード")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Document management
        docs_group = QGroupBox("学習ドキュメント")
        docs_layout = QVBoxLayout(docs_group)
        
        self.docs_list = QListWidget()
        docs_layout.addWidget(self.docs_list)
        
        docs_buttons = QHBoxLayout()
        self.add_doc_button = QPushButton("ドキュメントを追加")
        self.add_doc_button.clicked.connect(self.add_document)
        self.remove_doc_button = QPushButton("削除")
        self.remove_doc_button.clicked.connect(self.remove_document)
        docs_buttons.addWidget(self.add_doc_button)
        docs_buttons.addWidget(self.remove_doc_button)
        docs_layout.addLayout(docs_buttons)
        
        layout.addWidget(docs_group)
        
        # Stats
        self.stats_label = QLabel("学習済み: 0ドキュメント")
        layout.addWidget(self.stats_label)
        
        # Question input
        question_label = QLabel("質問:")
        layout.addWidget(question_label)
        
        question_layout = QHBoxLayout()
        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("学習した内容について質問してください...")
        self.question_input.returnPressed.connect(self.ask_question)
        
        self.ask_button = QPushButton("質問する")
        self.ask_button.clicked.connect(self.ask_question)
        
        question_layout.addWidget(self.question_input, 1)
        question_layout.addWidget(self.ask_button)
        layout.addLayout(question_layout)
        
        # Answer output
        answer_label = QLabel("回答:")
        layout.addWidget(answer_label)
        
        self.answer_output = QTextEdit()
        self.answer_output.setReadOnly(True)
        layout.addWidget(self.answer_output, 1)
    
    def add_document(self):
        """Add a document to the knowledge base"""
        filepaths, _ = QFileDialog.getOpenFileNames(
            self,
            "学習するドキュメントを選択",
            "",
            "ドキュメント (*.pdf *.docx *.doc);;すべてのファイル (*)"
        )
        
        for filepath in filepaths:
            if self.education_service.add_document(filepath):
                self.docs_list.addItem(os.path.basename(filepath))
        
        self.update_stats()
    
    def remove_document(self):
        """Remove a document from the knowledge base"""
        current_item = self.docs_list.currentItem()
        if current_item:
            # Find and remove the document
            docs = self.education_service.list_documents()
            for doc in docs:
                if os.path.basename(doc) == current_item.text():
                    self.education_service.remove_document(doc)
                    break
            
            self.docs_list.takeItem(self.docs_list.currentRow())
            self.update_stats()
    
    def update_stats(self):
        """Update the stats label"""
        stats = self.education_service.get_knowledge_base_stats()
        self.stats_label.setText(
            f"学習済み: {stats['document_count']}ドキュメント / "
            f"{stats['total_pages']}ページ / {stats['total_characters']:,}文字"
        )
    
    def ask_question(self):
        """Ask a question based on learned documents"""
        question = self.question_input.text().strip()
        if not question:
            return
        
        self.ask_button.setEnabled(False)
        self.answer_output.setText("回答を生成中...")
        
        # Get context from knowledge base
        context = self.education_service.get_context_for_query(question)
        
        if context:
            response = self.gemma_service.answer_with_context(question, context)
        else:
            response = "学習したドキュメントがありません。まずドキュメントを追加してください。"
        
        self.answer_output.setText(response)
        self.question_input.clear()
        self.ask_button.setEnabled(True)


class SettingsDialog(QDialog):
    """Settings dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the settings dialog UI"""
        layout = QVBoxLayout(self)
        
        # API Key
        api_group = QGroupBox("API設定")
        api_layout = QFormLayout(api_group)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Gemma APIキーを入力")
        
        config = get_config()
        self.api_key_input.setText(config.get_api_key())
        
        api_layout.addRow("APIキー:", self.api_key_input)
        layout.addWidget(api_group)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def accept(self):
        """Save settings and close"""
        config = get_config()
        config.set_api_key(self.api_key_input.text())
        super().accept()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gemma サポートツール")
        self.setMinimumSize(1200, 700)
        
        # Initialize services
        config = get_config()
        self.gemma_service = GemmaService(
            api_key=config.get_api_key(),
            model=config.get_gemma_model()
        )
        self.document_service = DocumentService()
        self.education_service = EducationModeService()
        self.search_service = WebSearchService()
        
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
    
    def setup_ui(self):
        """Set up the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create splitter for left/right panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Tab widget with features
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_widget = QTabWidget()
        
        # Add tabs
        self.email_panel = EmailPanel(self.gemma_service)
        self.tab_widget.addTab(self.email_panel, "📧 メール添削")
        
        self.document_panel = DocumentPanel(self.gemma_service, self.document_service)
        self.tab_widget.addTab(self.document_panel, "📄 ドキュメント")
        
        self.search_panel = SearchPanel(self.gemma_service, self.search_service)
        self.tab_widget.addTab(self.search_panel, "🔍 検索")
        
        self.education_panel = EducationPanel(self.gemma_service, self.education_service)
        self.tab_widget.addTab(self.education_panel, "📚 教育モード")
        
        left_layout.addWidget(self.tab_widget)
        
        # Right side - Chat panel
        self.chat_panel = ChatPanel(self.gemma_service)
        self.chat_panel.setMinimumWidth(350)
        self.chat_panel.setMaximumWidth(500)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(self.chat_panel)
        splitter.setSizes([700, 400])
        
        main_layout.addWidget(splitter)
    
    def setup_menu(self):
        """Set up the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("ファイル")
        
        settings_action = QAction("設定", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("終了", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menubar.addMenu("ヘルプ")
        
        about_action = QAction("このアプリについて", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_statusbar(self):
        """Set up the status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Model info
        model_info = self.gemma_service.get_model_info()
        mode_text = "デモモード" if model_info['is_demo_mode'] else "接続済み"
        self.statusbar.showMessage(
            f"モデル: {model_info['model']} | ステータス: {mode_text}"
        )
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Reinitialize Gemma service with new API key
            config = get_config()
            self.gemma_service.set_api_key(config.get_api_key())
            
            # Update status bar
            model_info = self.gemma_service.get_model_info()
            mode_text = "デモモード" if model_info['is_demo_mode'] else "接続済み"
            self.statusbar.showMessage(
                f"モデル: {model_info['model']} | ステータス: {mode_text}"
            )
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "Gemma サポートツールについて",
            """<h2>Gemma サポートツール</h2>
            <p>バージョン 1.0.0</p>
            <p>Google Gemma 3を使用した万能支援ツール</p>
            <h3>機能:</h3>
            <ul>
            <li>📧 メール添削</li>
            <li>📄 PDF/Word要約</li>
            <li>🔍 オンライン検索</li>
            <li>📚 専門教育モード</li>
            </ul>
            <p>Windowsで動作し、複数のGemmaモデル(1B, 4B, 12B, 27B)を選択可能です。</p>
            """
        )
