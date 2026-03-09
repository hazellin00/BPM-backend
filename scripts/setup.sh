#!/bin/bash

# VitalGuard 快速設置腳本
# 使用方式: bash scripts/setup.sh

set -e  # 遇到錯誤立即停止

echo "============================================"
echo "🩺 VitalGuard Core API - 快速設置"
echo "============================================"
echo ""

# 1. 檢查 Python 版本
echo "📌 檢查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   當前版本: $python_version"

if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "❌ 錯誤: 需要 Python 3.10 或更高版本"
    exit 1
fi
echo "✅ Python 版本符合要求"
echo ""

# 2. 創建虛擬環境 (可選)
echo "📌 是否創建虛擬環境? (y/n)"
read -r create_venv

if [ "$create_venv" = "y" ]; then
    echo "   創建虛擬環境中..."
    python3 -m venv venv
    echo "   啟用虛擬環境..."
    source venv/bin/activate
    echo "✅ 虛擬環境已啟用"
else
    echo "⏭️  跳過虛擬環境創建"
fi
echo ""

# 3. 安裝依賴
echo "📌 安裝 Python 依賴..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ 依賴安裝完成"
echo ""

# 4. 檢查環境變數
echo "📌 檢查環境變數..."
if [ ! -f .env ]; then
    echo "⚠️  未找到 .env 檔案"
    echo "   複製 .env.example 為 .env..."
    cp .env.example .env
    echo "✅ .env 檔案已創建"
    echo ""
    echo "🔧 請編輯 .env 檔案,填入以下資訊:"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_SERVICE_ROLE_KEY"
    echo "   - GEMINI_API_KEY"
    echo ""
    echo "⏸️  設置暫停,請完成環境變數配置後再繼續"
    exit 0
else
    echo "✅ .env 檔案已存在"
fi
echo ""

# 5. 驗證環境變數
echo "📌 驗證環境變數..."
source .env

if [ -z "$SUPABASE_URL" ]; then
    echo "❌ 錯誤: SUPABASE_URL 未設定"
    exit 1
fi

if [ -z "$SUPABASE_SERVICE_ROLE_KEY" ]; then
    echo "❌ 錯誤: SUPABASE_SERVICE_ROLE_KEY 未設定"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ 錯誤: GEMINI_API_KEY 未設定"
    exit 1
fi

echo "✅ 環境變數驗證通過"
echo ""

# 6. 提示資料庫設置
echo "📌 Supabase 資料庫設置"
echo "   請確認已在 Supabase SQL Editor 執行:"
echo "   database/schema.sql"
echo ""
echo "   完成後請輸入 y 繼續: "
read -r db_ready

if [ "$db_ready" != "y" ]; then
    echo "⏸️  請先完成資料庫設置"
    exit 0
fi
echo ""

# 7. 匯入臨床數據 (可選)
echo "📌 是否匯入臨床數據? (y/n)"
read -r import_data

if [ "$import_data" = "y" ]; then
    echo "   匯入 5000 筆臨床數據中..."
    python scripts/import_clinical_data.py
    echo "✅ 臨床數據匯入完成"
else
    echo "⏭️  跳過數據匯入"
fi
echo ""

# 8. 啟動服務
echo "============================================"
echo "🎉 設置完成!"
echo "============================================"
echo ""
echo "🚀 啟動開發伺服器:"
echo "   uvicorn main:app --reload"
echo ""
echo "📚 API 文檔:"
echo "   http://localhost:8000/docs"
echo ""
echo "❓ 測試 API:"
echo "   curl http://localhost:8000/health"
echo ""
