from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# 1. 初始化 Bearer 認證 (讓 Swagger UI 出現鎖頭)
security = HTTPBearer()

# 2. 初始化 Supabase Client 
# 請確保 settings.SUPABASE_URL 和 settings.SUPABASE_ANON_KEY 是正確的
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

async def get_current_user_id(res: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    透過 Supabase SDK 驗證 Token 並回傳 user_id (UUID)
    這會自動處理 ES256 (ECC) 與 HS256 的演算法差異
    """
    token = res.credentials 
    
    try:
        # 3. 呼叫 SDK 驗證 Token
        # 這是最安全的方式，它會直接向 Supabase 驗證這把鑰匙是否合法
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="身分驗證失敗，無效的 Token"
            )
            
        # 4. 提取使用者 UUID
        user_id: str = user_response.user.id
        return user_id

    except Exception as e:
        # 當 Token 過期、簽章錯誤或網路有問題時，會進到這裡
        logger.error(f"❌ Supabase Auth Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="身分驗證失敗，通行證已過期或無效"
        )