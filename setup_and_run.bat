@echo off
REM =============================================================================
REM Gemma Support Tool - ワンクリックセットアップ＆起動スクリプト
REM =============================================================================
REM このスクリプトをダブルクリックするだけで、必要なセットアップを自動で行い、
REM アプリケーションを起動します。
REM =============================================================================

setlocal EnableDelayedExpansion
chcp 65001 >nul 2>&1

echo.
echo ============================================================
echo  Gemma Support Tool - セットアップ＆起動
echo ============================================================
echo.

REM スクリプトのディレクトリに移動
cd /d "%~dp0"

REM =============================================================================
REM [1/4] Pythonのチェック
REM =============================================================================
echo [1/4] Pythonのインストール確認中...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo  Pythonが見つかりません
    echo ============================================================
    echo.
    echo このアプリケーションを実行するにはPython 3.10以上が必要です。
    echo.
    echo 以下の方法でPythonをインストールしてください：
    echo.
    echo [方法1] wingetを使用（推奨）
    echo   1. PowerShellを管理者として実行
    echo   2. 以下のコマンドを実行：
    echo      winget install Python.Python.3.12
    echo.
    echo [方法2] 公式サイトからダウンロード
    echo   https://www.python.org/downloads/
    echo   ※インストール時に「Add Python to PATH」にチェックを入れてください
    echo.
    echo Pythonをインストール後、このスクリプトを再度実行してください。
    echo.
    
    REM wingetでのインストールを試みるか確認
    echo wingetが利用可能な場合、自動インストールを試みますか？
    set /p INSTALL_CHOICE="自動インストールする場合は Y を入力 [Y/N]: "
    
    if /i "!INSTALL_CHOICE!"=="Y" (
        echo.
        echo Pythonのインストールを開始します...
        echo.
        winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
        if !errorlevel! neq 0 (
            echo.
            echo wingetでのインストールに失敗しました。
            echo 手動でPythonをインストールしてください。
            echo.
            pause
            exit /b 1
        )
        echo.
        echo Pythonのインストールが完了しました。
        echo 新しいコマンドプロンプトでこのスクリプトを再度実行してください。
        echo.
        pause
        exit /b 0
    ) else (
        echo.
        echo 手動でPythonをインストールしてください。
        pause
        exit /b 1
    )
)

REM Pythonバージョン表示
for /f "tokens=2 delims= " %%a in ('python --version 2^>^&1') do set PYTHON_VERSION=%%a
echo   Python %PYTHON_VERSION% が見つかりました。

REM Pythonバージョンチェック（3.10以上）
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% lss 3 (
    echo.
    echo エラー: Python 3.10以上が必要です。現在のバージョン: %PYTHON_VERSION%
    echo.
    pause
    exit /b 1
)

if %MAJOR%==3 (
    if %MINOR% lss 10 (
        echo.
        echo エラー: Python 3.10以上が必要です。現在のバージョン: %PYTHON_VERSION%
        echo.
        pause
        exit /b 1
    )
)

echo.

REM =============================================================================
REM [2/4] 仮想環境のセットアップ
REM =============================================================================
echo [2/4] 仮想環境のセットアップ中...

if not exist "venv" (
    echo   仮想環境を作成しています...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo エラー: 仮想環境の作成に失敗しました。
        pause
        exit /b 1
    )
    echo   仮想環境を作成しました。
) else (
    echo   既存の仮想環境が見つかりました。
)

echo.

REM =============================================================================
REM [3/4] 依存関係のインストール
REM =============================================================================
echo [3/4] 依存関係のインストール中...
echo   これには数分かかる場合があります...

call venv\Scripts\activate.bat

REM pipのアップグレード
python -m pip install --upgrade pip --quiet

REM requirements.txtから依存関係をインストール
pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo.
    echo エラー: 依存関係のインストールに失敗しました。
    echo ネットワーク接続を確認し、再度実行してください。
    pause
    exit /b 1
)

echo   すべての依存関係をインストールしました。
echo.

REM =============================================================================
REM [4/4] アプリケーションの起動
REM =============================================================================
echo [4/4] アプリケーションを起動しています...
echo.
echo ============================================================
echo  セットアップ完了！アプリケーションを起動します。
echo ============================================================
echo.
echo ※次回以降は同じスクリプトを実行すると、すぐにアプリが起動します。
echo ※このウィンドウを閉じるとアプリケーションも終了します。
echo.

python run.py

REM アプリケーション終了後
echo.
echo アプリケーションが終了しました。
echo.
pause
