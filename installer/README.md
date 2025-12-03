# Gemma サポートツール - インストーラービルドガイド

このドキュメントでは、Gemma サポートツールのWindowsインストーラーをビルドする方法を説明します。

## 目次

1. [前提条件](#前提条件)
2. [クイックスタート](#クイックスタート)
3. [詳細手順](#詳細手順)
4. [ファイル構成](#ファイル構成)
5. [トラブルシューティング](#トラブルシューティング)

## 前提条件

### 必須
- **Python 3.10以上**
- **pip** (Pythonパッケージマネージャー)
- **PyInstaller** (自動インストールされます)

### Windowsインストーラー作成時に必要
- **Inno Setup 6.x以上**
  - ダウンロード: https://jrsoftware.org/isinfo.php
  - インストール時に日本語ランゲージパックも選択してください

## クイックスタート

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

## 詳細手順

### 1. 実行ファイル（.exe）のビルド

PyInstallerを使用して、Pythonアプリケーションを実行ファイルにパッケージ化します。

```bash
# 依存関係のインストール
pip install pyinstaller
pip install -r requirements.txt

# ビルド実行
pyinstaller --clean pyinstaller.spec
```

ビルドが成功すると、`dist/GemmaSupportTool/` ディレクトリに実行ファイルが生成されます。

### 2. Windowsインストーラーの作成

Inno Setupを使用して、ウィザード形式のインストーラーを作成します。

```batch
REM Inno Setup コンパイラを使用
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss
```

または、Inno Setup GUIを使用:
1. Inno Setupを起動
2. `installer/setup.iss` を開く
3. 「ビルド」→「コンパイル」を選択

インストーラーは `dist/installer/GemmaSupportTool_Setup_1.0.0.exe` に生成されます。

## ファイル構成

```
installer/
├── README.md              # このファイル
├── setup.iss              # Inno Setupスクリプト
├── build_installer.bat    # Windowsビルドスクリプト
└── build_installer.sh     # Linux/Macビルドスクリプト

pyinstaller.spec           # PyInstaller設定ファイル
```

### 各ファイルの説明

| ファイル | 説明 |
|---------|------|
| `pyinstaller.spec` | PyInstallerの設定。依存関係やパッケージ化オプションを定義 |
| `setup.iss` | Inno Setupスクリプト。インストーラーのUI、インストール先、ショートカット作成などを定義 |
| `build_installer.bat` | Windowsでのビルドを自動化するバッチファイル |
| `build_installer.sh` | Linux/Macでのビルドを自動化するシェルスクリプト |

## インストーラーの機能

作成されるインストーラーには以下の機能が含まれます：

### インストールウィザード
1. **ウェルカム画面** - インストール開始の確認
2. **使用許諾画面** - ライセンス条項の表示（設定時）
3. **インストール先選択** - カスタムインストールパスの指定
4. **追加タスク選択** - デスクトップショートカット、スタートメニュー登録
5. **インストール進捗** - ファイルコピーの進捗表示
6. **完了画面** - アプリ起動オプション付き

### その他の機能
- **日本語/英語対応** - インストーラーの言語を自動検出
- **アンインストール機能** - コントロールパネルからの削除に対応
- **管理者権限不要** - ユーザーディレクトリへのインストールに対応

## トラブルシューティング

### Q: PyInstallerビルドが失敗する

**A:** 以下を確認してください：

```bash
# Pythonバージョンの確認
python --version  # 3.10以上が必要

# PyInstallerの再インストール
pip uninstall pyinstaller
pip install pyinstaller

# 依存関係の再インストール
pip install -r requirements.txt
```

### Q: Inno Setupが見つからない

**A:** Inno Setup 6をインストールしてください：
1. https://jrsoftware.org/isinfo.php からダウンロード
2. インストール時に「Japanese」言語パックを選択
3. デフォルトのインストールパスを使用

### Q: インストーラーで日本語が文字化けする

**A:** `setup.iss` ファイルがUTF-8 with BOMで保存されていることを確認してください。

### Q: アンチウイルスソフトが実行ファイルをブロックする

**A:** PyInstallerでビルドした実行ファイルは、一部のアンチウイルスソフトで誤検知されることがあります。以下の対策を試してください：
- アンチウイルスソフトの除外リストに追加
- コード署名証明書を取得して署名する

## CI/CDでの自動ビルド

GitHub Actionsを使用して、リリース時に自動でインストーラーをビルドすることができます。

ワークフローファイル: `.github/workflows/build-installer.yml`

詳細は [GitHub Actions ドキュメント](https://docs.github.com/en/actions) を参照してください。

## ライセンス

MIT License
