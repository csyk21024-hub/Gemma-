"""
Main entry point for the Gemma Support Tool
"""

import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.ui.main_window import MainWindow
from src.utils.config import get_config


def setup_application() -> QApplication:
    """Set up the Qt application"""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Gemma サポートツール")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Gemma Support Tool")
    
    # Set default font for Japanese text
    font = QFont()
    font.setFamily("Yu Gothic UI, Meiryo, MS Gothic, sans-serif")
    font.setPointSize(10)
    app.setFont(font)
    
    # Set style
    app.setStyle("Fusion")
    
    return app


def main():
    """Main entry point"""
    # Ensure config directories exist
    config = get_config()
    
    # Create necessary directories
    cache_dir = config.get("paths", "cache_dir", default="cache")
    logs_dir = config.get("paths", "logs_dir", default="logs")
    learned_docs_dir = config.get("education", "learned_documents_path", default="learned_documents")
    
    for dir_path in [cache_dir, logs_dir, learned_docs_dir]:
        os.makedirs(dir_path, exist_ok=True)
    
    # Create and run application
    app = setup_application()
    
    # Create main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
