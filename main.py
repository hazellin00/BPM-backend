"""
VitalGuard Core API - 主應用程式入口
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
# 1. 這裡補上了 auth 的導入
from app.routes import health, profiles, measurements, caregiver, ai, auth 

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

# 2. 修正 CORS 名單：去掉了結尾斜線，補上 5173
origins = [
    "http://localhost:5173",
    "http://localhost:4173",
    "https://bmp-frontend-eight.vercel.app"  # 🌟 這裡絕對不能有斜線 /
]

# CORS 中介層
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 註冊路由，並統一加上 /api/v1 前綴
# 這樣你的註冊網址就會是 https://.../api/v1/auth/register
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(profiles.router, prefix="/api/v1", tags=["Profiles"])
app.include_router(measurements.router, prefix="/api/v1", tags=["Measurements"])
app.include_router(caregiver.router, prefix="/api/v1", tags=["Caregiver"])
app.include_router(ai.router, prefix="/api/v1", tags=["AI"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])


@app.on_event("startup")
async def startup_event():
    """應用啟動時執行"""
    logger.info("=" * 60)
    logger.info("🩺 VitalGuard Core API 啟動中...")
    logger.info(f"📦 版本: {settings.APP_VERSION}")
    logger.info(f"🌐 CORS 允許來源: {origins}")
    logger.info(f"🚀 API 根路徑: /api/v1")
    logger.info("=" * 60)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )


@app.get("/")
async def root():
    return {"message": "VitalGuard API 運行中", "docs": "/docs"}