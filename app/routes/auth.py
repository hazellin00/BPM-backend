import logging
import uuid # 🌟 必備：生成隨機碼
from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import UserRegister, UserLogin, AuthResponse
from app.services.supabase_client import supabase_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(auth_data: UserRegister):
    # 1. 自動生成 username 邏輯 (Email前綴 + 4位隨機碼)
    email_prefix = auth_data.email.split('@')[0]
    random_suffix = str(uuid.uuid4())[:4]
    generated_username = f"{email_prefix}_{random_suffix}"

    # 2. 準備存入 Auth Metadata 的資料
    user_metadata = {
        "full_name": auth_data.name,
        "username": generated_username
    }

    # 3. 呼叫 Service 進行註冊
    response = await supabase_service.sign_up(
        auth_data.email, 
        auth_data.password, 
        user_metadata
    )
    
    if not response:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="註冊失敗，Email 可能已被使用"
        )
        
    return {
        "message": "註冊成功，請至信箱查收驗證信",
        "username": generated_username,
        "user_id": response.id
    }

@router.post("/login", response_model=AuthResponse)
async def login(auth_data: UserLogin):
    response = await supabase_service.sign_in(auth_data.email, auth_data.password)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="登入失敗，帳號或密碼錯誤"
        )
    return response