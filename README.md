# Gemma サポートツール

Google Gemma 3を使用した万能支援ツールです。Windows上で動作し、チャット機能、メール添削、PDF/Word要約、オンライン検索、専門教育モードを提供します。

## 機能

### 💬 チャットパネル
- 画面右側に常駐するチャットインターフェース
- リアルタイムでGemmaモデルと対話
- 複数のモデルサイズから選択可能（1B, 4B, 12B, 27B）

### 📧 メール添削
- ビジネスメールの文法チェック
- 敬語の使い方の修正
- より適切な表現の提案

### 📄 ドキュメント要約
- PDFファイルの内容抽出と要約
- Wordドキュメント（.docx）の処理
- 要点の自動まとめ

### 🔍 オンライン検索
- DuckDuckGoを使用したウェブ検索
- 検索結果の分析と要約
- 情報収集の効率化

### 📚 専門教育モード
- PDF/Wordドキュメントからの学習
- カスタム知識ベースの構築
- 学習した内容に基づく質問応答
- 業務サポート機能

## 動作環境

- **OS**: Windows 10/11
- **Python**: 3.10以上
- **メモリ**: 8GB以上推奨（モデルサイズに依存）

## モデル選択ガイド

| モデル | パラメータ数 | 推奨スペック | 用途 |
|--------|-------------|-------------|------|
| gemma-3-1b | 1B | 4GB RAM | 軽量な処理、低スペックPC |
| gemma-3-4b | 4B | 8GB RAM | 標準的な使用（推奨） |
| gemma-3-12b | 12B | 16GB RAM | 高品質な回答が必要な場合 |
| gemma-3-27b | 27B | 32GB RAM | 最高品質の回答 |

## インストール

### 方法1: ワンクリックセットアップ（推奨）🚀

ダブルクリックするだけで、仮想環境の作成・依存関係のインストール・アプリの起動まで自動で行います。

#### Windows

1. リポジトリをダウンロードまたはクローン
2. `setup_and_run.bat` をダブルクリック
3. 画面の指示に従って完了を待つ

```bash
# または、コマンドラインから実行
.\setup_and_run.bat
```

> **Note**: Pythonがインストールされていない場合、スクリプトがインストール方法を案内します。

#### Linux / macOS

1. リポジトリをダウンロードまたはクローン
2. ターミナルで以下を実行：

```bash
chmod +x setup_and_run.sh  # 初回のみ：実行権限を付与
./setup_and_run.sh
```

### 方法2: インストーラーを使用

1. [Releases](https://github.com/csyk21024-hub/Gemma-/releases)ページから最新のインストーラー（`GemmaSupportTool_Setup_x.x.x.exe`）をダウンロード
2. ダウンロードしたファイルを実行
3. インストールウィザードの指示に従ってインストール
4. スタートメニューまたはデスクトップのショートカットからアプリを起動

### 方法3: 手動セットアップ

#### 1. リポジトリのクローン
```bash
git clone https://github.com/csyk21024-hub/Gemma-.git
cd Gemma-
```

#### 2. 仮想環境の作成（推奨）
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

#### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### APIキーの設定（オプション）

実際のGemma APIを使用する場合は、以下のいずれかの方法でAPIキーを設定してください：

#### 方法1: 環境変数
```bash
set GEMMA_API_KEY=your-api-key-here
```

#### 方法2: アプリ内設定
アプリ起動後、メニューの「ファイル」→「設定」からAPIキーを入力

## 使用方法

### アプリケーションの起動
```bash
python run.py
```

### 基本的な使い方

1. **チャット**: 右側のチャットパネルでメッセージを入力して送信
2. **メール添削**: 「メール添削」タブでメール本文を入力し、「添削する」をクリック
3. **ドキュメント要約**: 「ドキュメント」タブでファイルを選択し、「要約する」をクリック
4. **検索**: 「検索」タブでキーワードを入力して検索
5. **教育モード**: 「教育モード」タブでドキュメントを追加し、質問

## 設定ファイル

アプリケーション起動時に `config.yaml` が自動生成されます。

```yaml
gemma:
  model: gemma-3-4b
  temperature: 0.7
  max_tokens: 2048
  api_key: ""

ui:
  theme: dark
  chat_panel_width: 400
  font_size: 12
  language: ja

features:
  email_proofreading: true
  pdf_summarization: true
  word_processing: true
  web_search: true
  education_mode: true
```

## インストーラーのビルド

開発者向けに、インストーラーを自分でビルドすることもできます。

### Windows

```batch
cd installer
build_installer.bat
```

### Linux/Mac

```bash
cd installer
chmod +x build_installer.sh
./build_installer.sh
```

詳細は [installer/README.md](installer/README.md) を参照してください。

## プロジェクト構造

```
Gemma-/
├── run.py                  # エントリーポイント
├── setup_and_run.bat       # Windowsワンクリックセットアップ
├── setup_and_run.sh        # Linux/Macワンクリックセットアップ
├── pyinstaller.spec        # PyInstaller設定
├── requirements.txt        # 依存関係
├── config.yaml            # 設定ファイル（自動生成）
├── src/
│   ├── main.py            # メインモジュール
│   ├── ui/
│   │   └── main_window.py # メインウィンドウUI
│   ├── services/
│   │   ├── gemma_service.py      # Gemma AI連携
│   │   ├── document_service.py   # ドキュメント処理
│   │   └── web_search_service.py # Web検索
│   └── utils/
│       └── config.py      # 設定管理
├── scripts/                # ユーティリティスクリプト
│   └── install_python.ps1 # Windows用Pythonインストーラー
├── installer/              # インストーラー関連ファイル
│   ├── README.md          # ビルド手順
│   ├── setup.iss          # Inno Setupスクリプト
│   ├── build_installer.bat # Windowsビルドスクリプト
│   └── build_installer.sh  # Linux/Macビルドスクリプト
├── .github/
│   └── workflows/
│       └── build-installer.yml  # CI/CDワークフロー
└── tests/                  # テスト
```

## トラブルシューティング

### Q: アプリが起動しない
A: Python 3.10以上がインストールされているか確認してください。また、PyQt6が正しくインストールされているか確認してください。

### Q: PDFが読み込めない
A: `PyPDF2` または `pdfplumber` がインストールされているか確認してください：
```bash
pip install PyPDF2 pdfplumber
```

### Q: 検索機能が動作しない
A: `duckduckgo-search` がインストールされているか確認してください：
```bash
pip install duckduckgo-search
```

### Q: デモモードと表示される
A: APIキーが設定されていない場合、デモモードで動作します。設定からAPIキーを入力してください。

## ライセンス

MIT License

## 謝辞

- Google Gemma モデル
- PyQt6 フレームワーク
- その他のオープンソースライブラリ