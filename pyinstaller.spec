# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Gemma Support Tool
Packages the Python application into a Windows executable
"""

import os
import sys

# Get the project root directory
project_root = os.path.dirname(os.path.abspath(SPEC))

# Analysis: Collect all required modules and data
a = Analysis(
    ['run.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        # Include src directory modules
        ('src', 'src'),
    ],
    hiddenimports=[
        # PyQt6 modules
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        # Google Generative AI
        'google.generativeai',
        # Document processing
        'PyPDF2',
        'pdfplumber',
        'docx',
        # Web search
        'duckduckgo_search',
        'bs4',
        'requests',
        # Configuration
        'yaml',
        'dotenv',
        # Standard library
        'json',
        'os',
        'sys',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GemmaSupportTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Hide console window for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if available: 'assets/icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GemmaSupportTool',
)
