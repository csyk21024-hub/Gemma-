#!/bin/bash
# =============================================================================
# Gemma Support Tool - Linux/Mac Build Script
# =============================================================================
# This script builds the executable for Gemma Support Tool
# Note: Creating Windows installer (.exe) requires Windows with Inno Setup
# This script is for cross-platform development and testing
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "============================================================"
echo " Gemma Support Tool - Build Script (Linux/Mac)"
echo "============================================================"
echo ""

cd "$PROJECT_ROOT"

# Check Python installation
echo "[1/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Found Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
echo ""
echo "[2/4] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Install dependencies
echo ""
echo "[3/4] Installing dependencies..."
pip install --upgrade pip
pip install --upgrade pyinstaller
pip install -r requirements.txt

# Build with PyInstaller
echo ""
echo "[4/4] Building with PyInstaller..."
pyinstaller --clean pyinstaller.spec

echo ""
echo "============================================================"
echo " Build completed successfully!"
echo "============================================================"
echo ""
echo "Executable location: dist/GemmaSupportTool/"
echo ""
echo "Note: To create a Windows installer (.exe):"
echo "  1. Copy the built files to a Windows machine"
echo "  2. Install Inno Setup 6 from https://jrsoftware.org/isinfo.php"
echo "  3. Run: installer/build_installer.bat"
echo ""

# Platform-specific notes
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macOS Note: The built application is for macOS."
    echo "To build a Windows executable, use a Windows machine or VM."
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Linux Note: The built application is for Linux."
    echo "To build a Windows executable, use a Windows machine or VM."
fi
