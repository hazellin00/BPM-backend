# 🩺 VitalGuard Core API

> **智慧長輩健康守護系統 - 後端數據與 AI 核心**

基於 FastAPI 的智慧數據中台，結合 5000 筆臨床數據進行 AI 飲食推薦。

---

## 📋 技術棧 (Tech Stack)

- **框架**: FastAPI (Python 3.10+)
- **資料庫**: Supabase (PostgreSQL) + RLS 安全政策
- **AI 引擎**: Google Gemini-1.5-Flash
- **部署**: Docker 容器化 (Render)
- **數據處理**: Pandas (處理 5000 筆臨床數據)

---

## 🎯 核心功能

### 1. 智慧血壓監測
- 即時血壓分類 (Normal / Elevated / High)
- 自動記錄測量歷史
- 軟刪除機制確保數據連續性

### 2. AI 飲食推薦引擎 (The Brain)
- **KNN 臨床比對**: 從 5000 筆案例中找出最相似患者
- **智慧推薦**: 根據年齡(±5)、BMI(±2)、血壓分類進行精準配對
- **AI 暖心建議**: Gemini AI 以「孫女護理師」口吻生成 60 字內飲食建議

### 3. 家屬授權系統
- 8 位隨機 Sharing Code 綁定機制
- 監看者可安全訪問長輩健康記錄
- RLS 確保數據隔離

---

## 🚀 快速開始

### 1. 環境設置

```bash
# 複製環境變數範例
cp .env.example .env

# 填入必要憑證
# SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, GEMINI_API_KEY
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 設置 Supabase 資料庫

在 Supabase SQL Editor 中執行:

```bash
# 執行資料庫 Schema
cat database/schema.sql
# 複製內容到 Supabase SQL Editor 執行
```

### 4. 匯入臨床數據

```bash
python scripts/import_clinical_data.py
```

### 5. 本地開發

```bash
# 開發模式 (Hot Reload)
uvicorn main:app --reload

# API 文檔
# http://localhost:8000/docs
```

### 6. Docker 部署

```bash
# 建立映像
docker build -t vitalguard-api .

# 執行容器
docker run -p 8000:8000 --env-file .env vitalguard-api
```

---

## 📡 API 端點總覽

### 健康檢查
- `GET /` - 系統狀態
- `GET /health` - 健康檢查

### 個人檔案
- `GET /api/v1/profiles/me` - 取得個人檔案
- `POST /api/v1/profiles/me` - 創建個人檔案 (自動生成 Sharing Code)
- `PUT /api/v1/profiles/me` - 更新個人檔案

### 健康測量
- `POST /api/v1/measurements` - 創建測量記錄 + AI 建議
- `GET /api/v1/measurements` - 取得測量歷史
- `DELETE /api/v1/measurements/{id}` - 軟刪除記錄

### 監看者功能
- `POST /api/v1/caregiver/bind` - 綁定病患 (透過 Sharing Code)
- `GET /api/v1/caregiver/patients` - 取得監看病患清單
- `GET /api/v1/caregiver/patients/{id}/measurements` - 查看病患測量記錄

### AI 諮詢
- `POST /api/v1/ai/consult` - 獨立 AI 飲食諮詢 (無需登入)

---

## 🧠 核心演算法

### 血壓分類演算法

```python
def classify_blood_pressure(systolic, diastolic):
    if systolic < 120 and diastolic < 80:
        return "Normal"
    elif 120 <= systolic < 130 and diastolic < 80:
        return "Elevated"
    else:
        return "High"
```

### KNN 臨床比對邏輯

```sql
SELECT * FROM dietary_knowledge_base
WHERE age BETWEEN (user_age - 5) AND (user_age + 5)
  AND bmi BETWEEN (user_bmi - 2) AND (user_bmi + 2)
  AND bp_category = user_bp_category
LIMIT 3;
```

### AI Prompt 設計

```
你是一位專業且溫柔的護理師，也是長輩的孫女。
現在要給長輩一段簡短、溫馨的飲食與生活建議。

【長輩資訊】
- 血壓: {systolic}/{diastolic} mmHg
- 年齡: {age} 歲
- BMI: {bmi}
- 建議每日卡路里: {calories} 大卡

請以60字內,白話、溫馨、像家人在關心的口吻給建議。
```

---

## 🗂️ 專案結構

```
BPM-backend/
├── app/                      # 應用程式核心
│   ├── config.py             # 配置管理
│   ├── routes/               # API 路由層
│   │   ├── health.py         # 健康檢查
│   │   ├── profiles.py       # 個人檔案
│   │   ├── measurements.py   # 健康測量
│   │   ├── caregiver.py      # 監看者功能
│   │   └── ai.py             # AI 諮詢
│   ├── schemas/              # Pydantic 數據模型
│   ├── services/             # 業務邏輯層
│   │   ├── supabase_client.py    # 資料庫服務
│   │   ├── clinical_matcher.py   # KNN 臨床比對
│   │   └── ai_service.py         # Gemini AI 服務
│   └── utils/                # 工具函數
│       ├── auth.py           # 認證工具
│       └── helpers.py        # 通用工具
├── database/                 # 資料庫 Schema
│   └── schema.sql            # Supabase SQL 腳本
├── scripts/                  # 管理腳本
│   └── import_clinical_data.py  # CSV 匯入工具
├── main.py                   # 應用入口
├── requirements.txt          # Python 依賴
├── Dockerfile                # Docker 配置
├── .env.example              # 環境變數範例
└── README.md                 # 專案文檔
```

---

## 🗄️ 資料庫架構

| 資料表 | 用途 | 關鍵欄位 |
|--------|------|----------|
| **profiles** | 使用者檔案 | `sharing_code`, `bmi`, `age` |
| **health_measurements** | 測量記錄 | `systolic_bp`, `diastolic_bp`, `deleted_at` |
| **caregiver_patient_links** | 監看者綁定 | `caregiver_id`, `patient_id`, `status` |
| **dietary_knowledge_base** | 臨床數據 | `age`, `bmi`, `bp_category`, `recommended_calories` |

---

## 🔐 安全政策 (RLS)

- ✅ 使用者僅能讀寫自己的數據
- ✅ 監看者需透過 Sharing Code 授權
- ✅ 所有刪除操作為軟刪除 (`deleted_at`)
- ✅ Supabase Row Level Security 確保數據隔離

---

## 🌐 部署至 Render

### 1. 連接 GitHub Repo

### 2. 環境變數設定

在 Render Dashboard 設定:

```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...
GEMINI_API_KEY=AIza...
```

### 3. 啟動命令

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. 健康檢查路徑

```
/health
```

---

## 📊 臨床數據說明

- **數據來源**: `cleaned_diet_data1.csv` (5000 筆)
- **欄位**: 年齡、BMI、血壓、慢性病、飲食習慣、推薦卡路里等
- **用途**: KNN 比對基礎,提供精準飲食建議

---

## 🤝 前端整合

### CORS 配置

已允許以下來源:

```python
CORS_ORIGINS = [
    "http://localhost:5173",              # Vite 開發環境
    "https://bmp-frontend-eight.vercel.app"  # Vercel 生產環境
]
```

### 範例請求

```javascript
// 創建測量記錄 + AI 建議
const response = await fetch('https://your-api.onrender.com/api/v1/measurements', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer {user_token}'
  },
  body: JSON.stringify({
    systolic_bp: 145,
    diastolic_bp: 95,
    pulse: 78
  })
});

const data = await response.json();
// {
//   "id": "...",
//   "bp_category": "High",
//   "ai_suggestion": "阿公血壓有點偏高...",
//   "recommended_calories": 1850,
//   "recommended_meal_plan": "Low-Fat Diet"
// }
```

---

## 🛠️ 開發指令

```bash
# 安裝依賴
pip install -r requirements.txt

# 開發模式
uvicorn main:app --reload

# 格式化程式碼 (可選)
black app/ main.py

# 類型檢查 (可選)
mypy app/

# 執行測試 (待實作)
pytest
```

---

## 📝 授權

此專案為 VitalGuard 智慧健康守護系統的私有後端核心。

---

## 🙋 支援

如有問題,請聯繫開發團隊或查閱 API 文檔:

- 📚 API Docs: `http://localhost:8000/docs`
- 📖 ReDoc: `http://localhost:8000/redoc`

---

**守護長輩健康,從智慧監測開始 🩺**
