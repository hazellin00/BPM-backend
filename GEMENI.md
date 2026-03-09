# 後端開發規範 (FastAPI + AI)

## 1. 核心目標
作為數據中台處理隱私紀錄，直接連接 **Supabase** 與 **Gemini AI (google-generativeai)**。必須以 Docker 容器化方式佈署於雲端平台，實現全天候 API 服務。

## 2. 技術棧 (Backend Stack)
- **框架**: FastAPI (Python)
- **資料庫**: **Supabase** (PostgreSQL 託管服務)
- **AI 引擎**: Google Gemini API
- **容器化**: **Docker** (Dockerfile 必備)
- **佈署平台**: **Hugging Face Spaces (Docker SDK)** 或 **Render**。

## 3. 註冊與安全驗證流程
- **信箱驗證強制化**: 檢查 JWT 之 `email_confirmed_at`。未驗證則回傳 `403 Forbidden`。
- **JWT 驗證**: 使用 `supabase.auth.get_user(token)` 進行正式核發驗證。

## 4. 安全分享機制 (Secure Share Code)
- **產生/連結**: 6 位隨機碼，10 分鐘時效，原子操作綁定 `viewer_id`。

## 5. 資料庫與保留機制 (Supabase)
- **連線**: 直接與 Supabase 進行正式 HTTPS 連結。
- **Delete (數據保留模式)**: 
    - **禁止使用 CASCADE DELETE**。
    - 使用者刪除帳號時，必須採用 `SET NULL` 或斷開關聯，確保血壓歷史紀錄與 AI 建議永久保留於資料庫。
- **RLS 政策**: 本人 CRUD；Linked Viewer 僅 SELECT。

## 6. AI 分析邏輯 (AI.py)
- **參考資料**: 《Personalized Medical Diet Recommendations Dataset》。
- **輸出**: JSON 結構化數據 (血壓等級、3 點飲食建議)。

## 7. 正式佈署與連線規範 (Docker & CORS)
- **CORS 設定**: 必須在 FastAPI 設定 `CORSMiddleware`，僅允許來自 **Vercel (前端)** 正式網址的請求。
- **Dockerfile**:
    - 基礎鏡像: `python:3.10-slim`
    - Port: 必須 Exposé 正確端口 (80 或 7860)。
    - CMD: `uvicorn main:app --host 0.0.0.0 --port 80`
- **環境變數**: 在佈署平台設定 `GEMINI_API_KEY` 與 `SUPABASE_SERVICE_KEY`