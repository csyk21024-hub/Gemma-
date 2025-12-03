#!/bin/bash
# =============================================================================
# Gemma Support Tool - ワンクリックセットアップ＆起動スクリプト
# =============================================================================
# このスクリプトを実行すると、必要なセットアップを自動で行い、
# アプリケーションを起動します。
#
# 使用方法:
#   chmod +x setup_and_run.sh  # 初回のみ
#   ./setup_and_run.sh
# =============================================================================

set -e

# スクリプトのディレクトリに移動
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "============================================================"
echo " Gemma Support Tool - セットアップ＆起動"
echo "============================================================"
echo ""

# =============================================================================
# [1/4] Pythonのチェック
# =============================================================================
echo "[1/4] Pythonのインストール確認中..."

# Python3コマンドを探す
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    # pythonが3.x系かどうか確認
    if python --version 2>&1 | grep -q "Python 3"; then
        PYTHON_CMD="python"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo ""
    echo "============================================================"
    echo " Python 3が見つかりません"
    echo "============================================================"
    echo ""
    echo "このアプリケーションを実行するにはPython 3.10以上が必要です。"
    echo ""
    
    # OSを検出してインストール方法を表示
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macOSでのインストール方法:"
        echo "  brew install python@3.12"
        echo ""
        echo "Homebrewがない場合:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    elif [[ -f /etc/debian_version ]]; then
        echo "Ubuntu/Debianでのインストール方法:"
        echo "  sudo apt update"
        echo "  sudo apt install python3 python3-venv python3-pip"
    elif [[ -f /etc/redhat-release ]]; then
        echo "RHEL/CentOS/Fedoraでのインストール方法:"
        echo "  sudo dnf install python3 python3-pip"
    else
        echo "お使いのシステムのパッケージマネージャーでPython 3.10以上をインストールしてください。"
    fi
    echo ""
    exit 1
fi

# Pythonバージョン取得
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
echo "  Python $PYTHON_VERSION が見つかりました。"

# バージョンチェック（3.10以上）
MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
    echo ""
    echo "エラー: Python 3.10以上が必要です。現在のバージョン: $PYTHON_VERSION"
    echo ""
    exit 1
fi

# python3-venvパッケージがあるか確認（Ubuntu/Debianの場合必要）
if ! $PYTHON_CMD -m venv --help &> /dev/null; then
    echo ""
    echo "警告: venvモジュールが見つかりません。"
    if [[ -f /etc/debian_version ]]; then
        echo "以下のコマンドでインストールしてください:"
        echo "  sudo apt install python3-venv"
    fi
    echo ""
    exit 1
fi

echo ""

# =============================================================================
# [2/4] 仮想環境のセットアップ
# =============================================================================
echo "[2/4] 仮想環境のセットアップ中..."

if [ ! -d "venv" ]; then
    echo "  仮想環境を作成しています..."
    $PYTHON_CMD -m venv venv
    echo "  仮想環境を作成しました。"
else
    echo "  既存の仮想環境が見つかりました。"
fi

# 仮想環境をアクティベート
source venv/bin/activate

echo ""

# =============================================================================
# [3/4] 依存関係のインストール
# =============================================================================
echo "[3/4] 依存関係のインストール中..."
echo "  これには数分かかる場合があります..."

# pipのアップグレード
pip install --upgrade pip --quiet

# requirements.txtから依存関係をインストール
pip install -r requirements.txt --quiet

echo "  すべての依存関係をインストールしました。"
echo ""

# =============================================================================
# [4/4] アプリケーションの起動
# =============================================================================
echo "[4/4] アプリケーションを起動しています..."
echo ""
echo "============================================================"
echo " セットアップ完了！アプリケーションを起動します。"
echo "============================================================"
echo ""
echo "※次回以降は同じスクリプトを実行すると、すぐにアプリが起動します。"
echo ""

python run.py

echo ""
echo "アプリケーションが終了しました。"
