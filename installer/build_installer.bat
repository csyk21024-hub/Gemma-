@echo off
REM =============================================================================
REM Gemma Support Tool - Windows Installer Build Script
REM =============================================================================
REM This script builds the Windows installer for Gemma Support Tool
REM Prerequisites:
REM   - Python 3.10+ with pip
REM   - PyInstaller (will be installed if missing)
REM   - Inno Setup 6.x (must be installed manually)
REM =============================================================================

setlocal EnableDelayedExpansion

echo.
echo ============================================================
echo  Gemma Support Tool - Installer Build Script
echo ============================================================
echo.

REM Change to project root directory
cd /d "%~dp0\.."

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher
    goto :error
)

for /f "tokens=2 delims= " %%a in ('python --version') do set PYTHON_VERSION=%%a
echo Found Python %PYTHON_VERSION%

REM Install/upgrade PyInstaller
echo.
echo [2/5] Installing/upgrading PyInstaller...
pip install --upgrade pyinstaller
if %errorlevel% neq 0 (
    echo ERROR: Failed to install PyInstaller
    goto :error
)

REM Install project dependencies
echo.
echo [3/5] Installing project dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    goto :error
)

REM Build executable with PyInstaller
echo.
echo [4/5] Building executable with PyInstaller...
pyinstaller --clean pyinstaller.spec
if %errorlevel% neq 0 (
    echo ERROR: PyInstaller build failed
    goto :error
)

REM Check if Inno Setup is installed
echo.
echo [5/5] Building installer with Inno Setup...

REM Try to find Inno Setup compiler
set ISCC_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe
) else if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe
)

if not defined ISCC_PATH (
    echo WARNING: Inno Setup not found
    echo Please install Inno Setup 6 from https://jrsoftware.org/isinfo.php
    echo.
    echo The PyInstaller build completed successfully.
    echo The executable is located at: dist\GemmaSupportTool\
    echo.
    echo After installing Inno Setup, run this script again to create the installer.
    goto :success_exe_only
)

REM Create output directory for installer
if not exist "dist\installer" mkdir "dist\installer"

REM Build installer
"%ISCC_PATH%" installer\setup.iss
if %errorlevel% neq 0 (
    echo ERROR: Inno Setup build failed
    goto :error
)

echo.
echo ============================================================
echo  Build completed successfully!
echo ============================================================
echo.
echo Executable: dist\GemmaSupportTool\GemmaSupportTool.exe
echo Installer:  dist\installer\GemmaSupportTool_Setup_1.0.0.exe
echo.
goto :eof

:success_exe_only
echo.
echo ============================================================
echo  PyInstaller build completed successfully!
echo ============================================================
echo.
echo Executable: dist\GemmaSupportTool\GemmaSupportTool.exe
echo.
goto :eof

:error
echo.
echo ============================================================
echo  Build failed! See error messages above.
echo ============================================================
echo.
exit /b 1
