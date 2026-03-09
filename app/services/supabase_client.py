"""
Supabase 資料庫客戶端
統一管理與 Supabase 的所有互動
"""
from app.utils.helpers import calculate_bp_category
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
        """呼叫 Supabase Auth 註冊並回傳 (用戶, 錯誤訊息)"""
        try:
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata
                }
            })
            # 成功時，錯誤訊息為 None
            return response.user, None
        except Exception as e:
            logger.error(f"Supabase Auth 註冊錯誤: {e}")
            # 失敗時，回傳 None 和 具體的錯誤字串
            return None, str(e)

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
            # 將 key 從 "user_id" 改為 "id"
            data = {"id": user_id, **profile_data}
            response = self.client.table("profiles").insert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"創建個人檔案失敗: {e}")
            raise

    async def update_profile(self, user_id: str, profile_data: dict):
        """更新個人檔案"""
        try:
            # 將過濾條件從 "user_id" 改為 "id"
            response = (
                self.client.table("profiles")
                .update(profile_data)
                .eq("id", user_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"更新個人檔案失敗: {e}")
            raise

    async def create_measurement(self, user_id: str, measurement_data: dict):
        """創建健康測量記錄"""
        try:
            # 🌟 修正：自動計算血壓分類，因為 MeasurementResponse 需要它
            systolic = measurement_data.get("systolic_bp")
            diastolic = measurement_data.get("diastolic_bp")
            
            bp_category = calculate_bp_category(systolic, diastolic)
            
            data = {
                "user_id": user_id, 
                "bp_category": bp_category, # 補上自動分類
                **measurement_data
            }
            # 請確認資料表名稱是 health_measurements 還是 measurements
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
        """軟刪除測量記錄 (正確 Python 語法版)"""
        try:
            from datetime import datetime
            now = datetime.utcnow().isoformat()

            # 🌟 Python SDK 直接這樣寫即可，不要加 .select()
            response = (
                self.client.table("health_measurements")
                .update({"deleted_at": now})
                .eq("id", measurement_id)
                .eq("user_id", user_id)
                .execute()
            )
            
            # response.data 如果是 []，代表 0 筆資料被更新
            return response.data[0] if response.data else None
            
        except Exception as e:
            logger.error(f"❌ 軟刪除測量記錄失敗: {str(e)}")
            raise e

    # --- Caregiver Links 操作 ---

    async def get_id_by_sharing_code(self, sharing_code: str) -> Optional[str]:
        """
        根據分享碼獲取使用者 ID
        """
        try:
            # 🌟 使用 .maybe_single()，如果找不到會回傳 data: None 而不是報錯
            response = self.client.table("profiles") \
                .select("id") \
                .eq("sharing_code", sharing_code) \
                .maybe_single() \
                .execute()
            
            # 檢查 response 本身是否存在（防止連線問題）
            if response and hasattr(response, 'data') and response.data:
                return response.data["id"]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 透過分享碼查詢 ID 失敗: {str(e)}")
            return None

    async def create_caregiver_link(self, caregiver_id: str, patient_id: str, status: str = "active"):
        """
        建立照護綁定紀錄
        """
        try:
            data = {
                "caregiver_id": caregiver_id,
                "patient_id": patient_id,
                "status": status
            }
            response = self.client.table("caregiver_patient_links").upsert(data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"❌ 建立綁定紀錄失敗: {str(e)}")
            return None

    async def get_caregiver_patients(self, caregiver_id: str):
        """
        取得照護者綁定的所有病患清單 (包含病患個人檔案資訊)
        """
        try:
            # 🌟 使用 Supabase 的 Join 語法：
            # 意思是：從 links 表出發，順便把 profiles 表中 id 符合 patient_id 的資料抓過來
            response = self.client.table("caregiver_patient_links") \
                .select("""
                    *,
                    patient_profile:profiles!patient_id (
                        id,
                        full_name,
                        gender,
                        birth_year,
                        sharing_code
                    )
                """) \
                .eq("caregiver_id", caregiver_id) \
                .eq("status", "active") \
                .execute()
            
            return response.data if response and response.data else []
            
        except Exception as e:
            logger.error(f"❌ 取得病患清單失敗: {str(e)}")
            return []

    # async def check_caregiver_access(self, caregiver_id: str, patient_id: str) -> bool:
    #     try:
    #         response = self.client.table("caregiver_patient_links") \
    #             .select("id") \
    #             .eq("caregiver_id", caregiver_id) \
    #             .eq("patient_id", patient_id) \
    #             .eq("status", "active") \
    #             .execute()

    #         # 🌟 加這行 debug
    #         print(f"DEBUG - Caregiver: {caregiver_id}")
    #         print(f"DEBUG - Patient: {patient_id}")
    #         print(f"DEBUG - Data from DB: {response.data}")

    #         return len(response.data) > 0
    #     except Exception as e:
    #         print(f"DEBUG - Error: {e}")
    #         return False

    async def check_caregiver_access(self, caregiver_id: str, patient_id: str) -> bool:
        """
        檢查監看者權限 (除錯版本：暫時拿掉 status 過濾)
        """
        try:
            # 🌟 這裡暫時拿掉 .eq("status", "active")，只看這兩個人有沒有連線紀錄
            response = self.client.table("caregiver_patient_links") \
                .select("id") \
                .eq("caregiver_id", caregiver_id) \
                .eq("patient_id", patient_id) \
                .execute()

            # 保持 Debug 輸出，讓我們在 Terminal 看到結果
            print(f"DEBUG - Caregiver: {caregiver_id}")
            print(f"DEBUG - Patient: {patient_id}")
            print(f"DEBUG - Data from DB: {response.data}")

            return len(response.data) > 0
        except Exception as e:
            logger.error(f"❌ 檢查權限失敗: {str(e)}")
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
