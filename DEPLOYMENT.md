# 🚀 VitalGuard 部署指南

完整的部署檢查清單與步驟說明

---

## 📋 部署前檢查清單

### 1. 環境準備

- [ ] Supabase 專案已創建
- [ ] Google Gemini API Key 已取得
- [ ] Render / Hugging Face 帳號已註冊
- [ ] GitHub Repository 已建立

### 2. Supabase 設置

#### 2.1 執行資料庫 Schema

1. 登入 [Supabase Dashboard](https://app.supabase.com)
2. 選擇您的專案
3. 進入 **SQL Editor**
4. 複製 `database/schema.sql` 的完整內容
5. 執行 SQL 腳本
6. 確認所有資料表已創建:
   - profiles
   - health_measurements
   - caregiver_patient_links
   - dietary_knowledge_base

#### 2.2 啟用 Authentication

1. 進入 **Authentication** > **Settings**
2. 啟用 **Email Auth**
3. (可選) 設定 Email Templates 為中文

#### 2.3 設置 RLS 政策

資料表的 RLS 政策已在 schema.sql 中自動創建,請確認:

```sql
-- 檢查 RLS 是否啟用
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public';
```

#### 2.4 取得 API Keys

1. 進入 **Settings** > **API**
2. 複製以下 Keys:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY` (前端使用)
   - `SUPABASE_SERVICE_ROLE_KEY` (後端使用,保密!)

### 3. 匯入臨床數據

```bash
# 在本地執行
python scripts/import_clinical_data.py
```

預期輸出:

```
📁 讀取 CSV: cleaned_diet_data1.csv
✅ 讀取成功,共 5000 筆資料
🚀 開始匯入,分為 50 批次...
✅ 批次 1/50 完成 (100 筆)
...
🎉 匯入完成!總計 5000 筆資料
```

驗證數據:

```sql
SELECT COUNT(*) FROM dietary_knowledge_base;
-- 應該返回 5000
```

---

## 🌐 部署至 Render

### 步驟 1: 創建 Web Service

1. 登入 [Render Dashboard](https://dashboard.render.com)
2. 點擊 **New** > **Web Service**
3. 連接 GitHub Repository

### 步驟 2: 配置服務

| 設定項目 | 值 |
|---------|---|
| **Name** | vitalguard-api |
| **Region** | Singapore (或最近的區域) |
| **Branch** | main |
| **Runtime** | Docker |
| **Instance Type** | Free (或 Starter) |

### 步驟 3: 環境變數

點擊 **Environment** 頁籤,新增以下變數:

```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
SUPABASE_ANON_KEY=eyJhbGc...
GEMINI_API_KEY=AIzaSyC...
DEBUG=False
```

### 步驟 4: Health Check

| 設定項目 | 值 |
|---------|---|
| **Health Check Path** | /health |
| **Health Check Interval** | 30 seconds |

### 步驟 5: 部署

1. 點擊 **Create Web Service**
2. 等待部署完成 (約 3-5 分鐘)
3. 查看 Logs 確認啟動成功

預期 Log 輸出:

```
============================================================
🩺 VitalGuard Core API 啟動中...
📦 版本: 1.0.0
🌐 CORS 允許來源: ['http://localhost:5173', 'https://bmp-frontend-eight.vercel.app']
🤖 AI 模型: gemini-1.5-flash
============================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 步驟 6: 測試 API

取得您的 Render URL (例如: `https://vitalguard-api.onrender.com`)

```bash
# 測試根端點
curl https://vitalguard-api.onrender.com/

# 測試健康檢查
curl https://vitalguard-api.onrender.com/health

# 查看 API 文檔
# https://vitalguard-api.onrender.com/docs
```

---

## 📱 前端配置 (Vercel)

### 更新前端環境變數

在 Vercel 專案設定中新增:

```
VITE_API_BASE_URL=https://vitalguard-api.onrender.com
VITE_SUPABASE_URL=https://xxxxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
```

### 測試前後端連接

```javascript
// 前端測試 API 連接
const testAPI = async () => {
  const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/health`);
  const data = await response.json();
  console.log('API Status:', data);
};
```

---

## 🔍 驗證部署

### 1. 系統健康檢查

```bash
curl https://vitalguard-api.onrender.com/health
```

預期回應:

```json
{
  "status": "healthy",
  "message": "系統運作正常"
}
```

### 2. AI 諮詢測試 (無需登入)

```bash
curl -X POST https://vitalguard-api.onrender.com/api/v1/ai/consult \
  -H "Content-Type: application/json" \
  -d '{
    "systolic_bp": 145,
    "diastolic_bp": 92,
    "age": 65,
    "bmi": 24.5
  }'
```

預期回應:

```json
{
  "suggestion": "阿公血壓有點偏高...",
  "bp_category": "High",
  "recommended_calories": 1850,
  "recommended_meal_plan": "Low-Fat Diet",
  "clinical_matches": 3
}
```

### 3. 完整流程測試

1. **前端註冊使用者** (透過 Supabase Auth)
2. **創建個人檔案** → 取得 Sharing Code
3. **新增測量記錄** → 取得 AI 建議
4. **監看者綁定** → 透過 Sharing Code
5. **查看病患記錄** → 驗證權限控制

---

## 🐛 常見問題排查

### 問題 1: CORS 錯誤

**錯誤訊息**: `Access to fetch has been blocked by CORS policy`

**解決方案**:

1. 確認前端 URL 已加入 `app/config.py` 的 `CORS_ORIGINS`
2. 重新部署後端

### 問題 2: Supabase 連接失敗

**錯誤訊息**: `❌ Supabase 連線失敗`

**檢查項目**:

- [ ] `SUPABASE_URL` 格式正確 (包含 https://)
- [ ] `SUPABASE_SERVICE_ROLE_KEY` 沒有多餘空格
- [ ] Supabase 專案未暫停 (Free Plan 7 天無活動會暫停)

### 問題 3: Gemini API 錯誤

**錯誤訊息**: `AI 引擎暫時休息中`

**檢查項目**:

- [ ] `GEMINI_API_KEY` 有效且未過期
- [ ] API Key 有啟用 Gemini 1.5 Flash 模型
- [ ] 未超過免費額度 (每月 1500 次請求)

### 問題 4: 臨床數據查詢為空

**症狀**: AI 建議中 `clinical_matches: 0`

**解決方案**:

```sql
-- 檢查數據是否已匯入
SELECT COUNT(*) FROM dietary_knowledge_base;

-- 檢查 bp_category 欄位
SELECT DISTINCT bp_category FROM dietary_knowledge_base;
-- 應該包含: Normal, Elevated, High
```

---

## 📊 監控與維護

### Render 監控

1. **Logs**: Render Dashboard > Logs
2. **Metrics**: 查看 CPU、Memory 使用率
3. **Alerts**: 設定 Health Check 失敗通知

### Supabase 監控

1. **Database Usage**: 查看資料庫大小
2. **API Requests**: 監控 API 呼叫次數
3. **Auth Users**: 追蹤使用者註冊數

### 建議的監控指標

- API 回應時間 < 2 秒
- AI 建議生成成功率 > 95%
- 資料庫查詢時間 < 500ms

---

## 🔄 更新部署

### 從 Git 更新

```bash
git add .
git commit -m "Update: 新增功能或修復"
git push origin main
```

Render 會自動偵測並重新部署。

### 手動觸發部署

Render Dashboard > Manual Deploy > Deploy latest commit

---

## 📞 技術支援

- **Render 文檔**: https://render.com/docs
- **Supabase 文檔**: https://supabase.com/docs
- **FastAPI 文檔**: https://fastapi.tiangolo.com
- **Gemini API 文檔**: https://ai.google.dev/docs

---

**部署完成後,記得更新前端 API URL! 🎉**
