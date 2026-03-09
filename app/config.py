"""
應用配置管理
集中管理環境變數與系統配置
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """系統設定"""

    # 基本設定
    APP_NAME: str = "VitalGuard Core API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"

    # Supabase 配置
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")

    # Google Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # CORS 設定
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "https://bmp-frontend-eight.vercel.app",
    ]

    # 業務邏輯配置
    SHARING_CODE_LENGTH: int = 8
    AI_SUGGESTION_MAX_LENGTH: int = 60
    KNN_NEIGHBORS: int = 3  # 臨床案例比對數量

    # 血壓分類閾值
    BP_CATEGORIES = {
        "Normal": {"systolic": (0, 120), "diastolic": (0, 80)},
        "Elevated": {"systolic": (120, 130), "diastolic": (0, 80)},
        "High": {"systolic": (130, 999), "diastolic": (80, 999)},
    }


settings = Settings()
