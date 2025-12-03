# =============================================================================
# Gemma Support Tool - Python自動インストールスクリプト
# =============================================================================
# このスクリプトはWindowsにPython 3.12を自動でインストールします。
#
# 使用方法:
#   1. PowerShellを管理者として実行
#   2. Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
#   3. .\scripts\install_python.ps1
# =============================================================================

param(
    [string]$Version = "3.12"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Python 自動インストールスクリプト" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 管理者権限チェック
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "警告: このスクリプトは管理者権限で実行することを推奨します。" -ForegroundColor Yellow
    Write-Host ""
}

# 既存のPythonをチェック
Write-Host "[1/3] 既存のPythonをチェック中..." -ForegroundColor Green
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(\d+)") {
        $minor = [int]$Matches[1]
        if ($minor -ge 10) {
            Write-Host "  Python $pythonVersion が既にインストールされています。" -ForegroundColor Green
            Write-Host ""
            Write-Host "既存のPythonで十分です。セットアップスクリプトを実行してください:" -ForegroundColor Cyan
            Write-Host "  .\setup_and_run.bat" -ForegroundColor White
            Write-Host ""
            exit 0
        }
    }
    Write-Host "  古いバージョンのPythonが見つかりました: $pythonVersion" -ForegroundColor Yellow
} catch {
    Write-Host "  Pythonが見つかりませんでした。インストールを続行します。" -ForegroundColor Yellow
}
Write-Host ""

# wingetの確認
Write-Host "[2/3] インストール方法を確認中..." -ForegroundColor Green

$useWinget = $false
try {
    $wingetVersion = winget --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  wingetが利用可能です。wingetを使用してインストールします。" -ForegroundColor Green
        $useWinget = $true
    }
} catch {
    Write-Host "  wingetが見つかりませんでした。公式インストーラーを使用します。" -ForegroundColor Yellow
}
Write-Host ""

# Pythonのインストール
Write-Host "[3/3] Python $Version をインストール中..." -ForegroundColor Green

if ($useWinget) {
    # wingetでインストール
    Write-Host "  wingetを使用してPythonをインストールしています..." -ForegroundColor White
    try {
        winget install Python.Python.$Version --accept-source-agreements --accept-package-agreements --silent
        if ($LASTEXITCODE -ne 0) {
            throw "wingetでのインストールに失敗しました"
        }
    } catch {
        Write-Host "  wingetでのインストールに失敗しました。公式インストーラーを試します..." -ForegroundColor Yellow
        $useWinget = $false
    }
}

if (-not $useWinget) {
    # 公式インストーラーをダウンロードして実行
    $installerUrl = "https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe"
    $installerPath = "$env:TEMP\python-installer.exe"
    
    Write-Host "  公式インストーラーをダウンロードしています..." -ForegroundColor White
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath -UseBasicParsing
    } catch {
        Write-Host ""
        Write-Host "エラー: インストーラーのダウンロードに失敗しました。" -ForegroundColor Red
        Write-Host "手動でダウンロードしてください: https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host ""
        exit 1
    }
    
    Write-Host "  インストーラーを実行しています..." -ForegroundColor White
    Write-Host "  ※インストーラーが表示されたら、「Add Python to PATH」にチェックを入れてください" -ForegroundColor Yellow
    
    Start-Process -FilePath $installerPath -ArgumentList "/passive", "InstallAllUsers=0", "PrependPath=1", "Include_test=0" -Wait
    
    # インストーラーを削除
    Remove-Item -Path $installerPath -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " インストール完了！" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "重要: 新しいPowerShellまたはコマンドプロンプトを開いて、" -ForegroundColor Yellow
Write-Host "      以下のコマンドでアプリケーションをセットアップしてください:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  .\setup_and_run.bat" -ForegroundColor White
Write-Host ""
Write-Host "または、エクスプローラーで setup_and_run.bat をダブルクリック" -ForegroundColor White
Write-Host ""
