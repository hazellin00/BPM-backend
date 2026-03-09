"""
Supabase 資料庫客戶端
統一管理與 Supabase 的所有互動
"""
from supabase import create_client, Client
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SupabaseService:
    """Supabase 數據庫服務"""

    def __init__(self):
        """初始化 Supabase 客戶端"""
        try:
            self.client: Client = create_client(
                settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY
            )
            logger.info("✅ Supabase 連線成功")
        except Exception as e:
            logger.error(f"❌ Supabase 連線失敗: {e}")
            raise
    async def sign_up(self, email: str, password: str, metadata: dict = None):
        """呼叫 Supabase Auth 註冊"""
    try:
        response = self.client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": metadata  # 這裡會存入 auth.users 的 raw_user_meta_data
            }
        })
        return response.user
    except Exception as e:
        logger.error(f"Supabase Auth 註冊錯誤: {e}")
        return None

    async def sign_in(self, email: str, password: str):
        """呼叫 Supabase Auth 登入"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            return {
                "access_token": response.session.access_token,
                "token_type": "bearer",
                "user_id": response.user.id,
                "email": response.user.email
            }
        except Exception as e:
            logger.error(f"Supabase Auth 登入錯誤: {e}")
            return None

    # --- Profiles 操作 ---

    async def get_profile_by_user_id(self, user_id: str):
        try:
            response = (
                self.client.table("profiles")
                .select("*")
                .eq("id", user_id) 
                .maybe_single()
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"取得檔案失敗: {e}")
            raise

    async def get_profile_by_sharing_code(self, sharing_code: str):
        """根據 sharing_code 取得個人檔案"""
        try:
            response = (
                self.client.table("profiles")
                .select("*")
                .eq("sharing_code", sharing_code)
                .maybe_single()
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"分享碼查詢失敗: {e}")
            raise

    async def create_profile(self, user_id: str, profile_data: dict):
        """創建個人檔案"""
        try:
            data = {"user_id": user_id, **profile_data}
            response = self.client.table("profiles").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"創建個人檔案失敗: {e}")
            raise

    async def update_profile(self, user_id: str, profile_data: dict):
        """更新個人檔案"""
        try:
            response = (
                self.client.table("profiles")
                .update(profile_data)
                .eq("user_id", user_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"更新個人檔案失敗: {e}")
            raise

    # --- Health Measurements 操作 ---

    async def create_measurement(self, user_id: str, measurement_data: dict):
        """創建健康測量記錄"""
        try:
            data = {"user_id": user_id, **measurement_data}
            response = self.client.table("health_measurements").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"創建測量記錄失敗: {e}")
            raise

    async def get_measurements(
        self, user_id: str, limit: int = 30, include_deleted: bool = False
    ):
        """取得使用者的測量記錄"""
        try:
            query = (
                self.client.table("health_measurements")
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .limit(limit)
            )

            if not include_deleted:
                query = query.is_("deleted_at", "null")

            response = query.execute()
            return response.data
        except Exception as e:
            logger.error(f"取得測量記錄失敗: {e}")
            raise

    async def soft_delete_measurement(self, measurement_id: str, user_id: str):
        """軟刪除測量記錄 (僅更新 deleted_at)"""
        try:
            from datetime import datetime

            response = (
                self.client.table("health_measurements")
                .update({"deleted_at": datetime.utcnow().isoformat()})
                .eq("id", measurement_id)
                .eq("user_id", user_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"軟刪除測量記錄失敗: {e}")
            raise

    # --- Caregiver Links 操作 ---

    async def create_caregiver_link(
        self, caregiver_id: str, patient_id: str, status: str = "active"
    ):
        """創建監看者與病患的綁定關係"""
        try:
            data = {
                "caregiver_id": caregiver_id,
                "patient_id": patient_id,
                "status": status,
            }
            response = self.client.table("caregiver_patient_links").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"創建監看者綁定失敗: {e}")
            raise

    async def get_caregiver_patients(self, caregiver_id: str):
        """取得監看者的所有病患"""
        try:
            response = (
                self.client.table("caregiver_patient_links")
                .select("*, profiles!patient_id(*)")
                .eq("caregiver_id", caregiver_id)
                .eq("status", "active")
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"取得監看者病患清單失敗: {e}")
            raise

    async def check_caregiver_access(self, caregiver_id: str, patient_id: str) -> bool:
        """檢查監看者是否有權限訪問病患數據"""
        try:
            response = (
                self.client.table("caregiver_patient_links")
                .select("id")
                .eq("caregiver_id", caregiver_id)
                .eq("patient_id", patient_id)
                .eq("status", "active")
                .maybe_single()
                .execute()
            )
            return response.data is not None
        except Exception as e:
            logger.error(f"檢查監看者權限失敗: {e}")
            return False

    # --- Dietary Knowledge Base 操作 ---

    async def query_similar_cases(self, age: int, bmi: float, bp_category: str, limit: int = 3):
        """查詢相似的臨床案例 (KNN 概念)"""
        try:
            # 年齡 ±5, BMI ±2 的範圍查詢
            response = (
                self.client.table("dietary_knowledge_base")
                .select("*")
                .gte("age", age - 5)
                .lte("age", age + 5)
                .gte("bmi", bmi - 2)
                .lte("bmi", bmi + 2)
                .eq("bp_category", bp_category)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"查詢臨床案例失敗: {e}")
            raise


# 全局單例
supabase_service = SupabaseService()
