import os
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai

# 1. 載入環境變數
load_dotenv()

# 2. 專業化系統初始化
app = FastAPI(
    title="VitalGuard Core API",
    description="BMP 智慧血壓監測系統 - 核心數據與 AI 分析引擎",
    version="1.0.0"
)

# 3. CORS 安全防護： Vercel 前端
origins = [
    "http://localhost:5173",                    
    "https://bmp-frontend-eight.vercel.app",   
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. 初始化外部服務 (Supabase & Gemini)
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"), 
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
ai_model = genai.GenerativeModel('gemini-pro')

# --- API 服務路由 ---

@app.get("/", tags=["Status"])
def get_system_status():
    """確認系統連線狀態"""
    return {
        "status": "operational",
        "service": "VitalGuard Core API",
        "message": "系統已就緒，守護長輩健康中"
    }

@app.post("/api/v1/ai/consult", tags=["AI Engine"])
async def get_elderly_advice(blood_pressure: dict):
    """
    接收血壓數據並產生 AI 衛教建議
    """
    sys = blood_pressure.get('sys')
    dia = blood_pressure.get('dia')
    
    if not sys or not dia:
        raise HTTPException(status_code=400, detail="缺少血壓數據")

    # 針對長輩設計的溫馨 Prompt
    prompt = (
        f"我是你的健康助手。目前的血壓是收縮壓 {sys}, 舒張壓 {dia}。 "
        "請以一位溫柔的專業護理師身份，給長輩一段 50 字內、溫馨且白話的飲食或生活建議。"
    )

    try:
        response = ai_model.generate_content(prompt)
        return {"suggestion": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail="AI 引擎暫時休息中，請稍後再試")

@app.get("/api/v1/auth/verify", tags=["Security"])
async def verify_user(authorization: str = Header(None)):
    """驗證長輩身份 (JWT 預留位)"""
    if not authorization:
        raise HTTPException(status_code=401, detail="需要身份驗證")
    return {"status": "authenticated", "message": "身份核對成功"}