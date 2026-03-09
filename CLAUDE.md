---
name: vitalguard-core-api
description: 基於 FastAPI 的智慧數據中台，結合 5000 筆臨床數據進行 AI 飲食推薦。
---

# VitalGuard 後端開發規範 (FastAPI + AI)

## 1. 技術棧與環境
- **框架**: FastAPI (Python 3.10+)
- **資料庫**: Supabase (Postgres) + RLS 安全政策
- **AI 引擎**: Google Gemini-1.5-Flash
- **佈署**: Docker 容器化 (Render / Hugging Face)

## 2. 臨床大腦邏輯 (The Brain)
- **知識庫**: `dietary_knowledge_base` (由 `cleaned_diet_data1.csv` 匯入)。
- **比對演算法**: 
  1. 取得使用者年齡、BMI、及當次血壓分類。
  2. SQL 檢索與該使用者特徵（年齡±5, BMI±2）最相似的 3 筆臨床案例。
  3. 提取 `recommended_calories` 與 `recommended_meal_plan`。
- **AI 生成**: 結合上述數據，以「暖心孫女」口吻生成 60 字內建議。

## 3. 數據庫架構 (Core Tables)
| 資料表 | 關鍵欄位 | 安全策略 (RLS) |
| :--- | :--- | :--- |
| **profiles** | `sharing_code` (Unique), `bmi`, `chronic_disease` | 本人/綁定監看者可讀 |
| **health_measurements** | `systolic_bp`, `diastolic_bp`, `pulse`, `deleted_at` | 本人 CRUD, 監看者 SELECT |
| **caregiver_patient_links** | `caregiver_id`, `patient_id`, `status` | 參與者雙方可見 |
| **dietary_knowledge_base** | `age`, `bmi`, `bp_category`, `recommended_calories` | 所有登入者唯讀 |

## 4. 監看者授權流程
- **綁定端點**: `POST /api/v1/caregiver/bind` (輸入 8 位 Sharing Code)。
- **權限控制**: 通過查詢 `caregiver_patient_links` 表驗證讀取權限，拒絕未授權的數據讀取。

## 5. 數據保留政策 (Soft Delete)
- **禁止硬刪除**: 所有測量數據的刪除行為僅更新 `deleted_at` 欄位。
- **資料完整性**: 使用者註冊時自動觸發 Profile 建立，並生成 8 位隨機 Sharing Code。

## 6. 佈署規範
- **CORS**: 嚴格放行 `https://bmp-frontend-eight.vercel.app`。
- **Docker**: 必須配置 `EXPOSE 8000` 並設定正確的環境變數。