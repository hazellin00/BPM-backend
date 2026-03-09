"""
VitalGuard Core API - 主應用程式入口

智慧長輩健康守護系統後端
基於 FastAPI + Supabase + Google Gemini AI
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 創建 FastAPI 應用
app = FastAPI(
    title=settings.APP_NAME,
    description="🩺 智慧血壓監測系統 - 結合 5000 筆臨床數據的 AI 飲食推薦引擎",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = [
    "http://localhost:5173",
    "http://localhost:4173",                 # 本地開發用
    "https://bmp-frontend-eight.vercel.app"   
]

# CORS 中介層
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 導入路由
from app.routes import health, profiles, measurements, caregiver, ai

# 註冊路由
app.include_router(health.router)
app.include_router(profiles.router)
app.include_router(measurements.router)
app.include_router(caregiver.router)
app.include_router(ai.router)


# 啟動事件
@app.on_event("startup")
async def startup_event():
    """應用啟動時執行"""
    logger.info("=" * 60)
    logger.info("🩺 VitalGuard Core API 啟動中...")
    logger.info(f"📦 版本: {settings.APP_VERSION}")
    logger.info(f"🌐 CORS 允許來源: {origins}")
    logger.info(f"🤖 AI 模型: {settings.GEMINI_MODEL}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉時執行"""
    logger.info("👋 VitalGuard Core API 正在關閉...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
