# app/routes/auth.py
from fastapi import APIRouter, HTTPException, status
# 🌟 改成從 schemas 導入
from app.schemas.auth import UserRegister, UserLogin, AuthResponse
from app.services.supabase_client import supabase_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(auth_data: UserRegister): # 🌟 使用 UserRegister schema
    response = await supabase_service.sign_up(auth_data.email, auth_data.password)
    if not response:
        raise HTTPException(status_code=400, detail="註冊失敗")
    return {"message": "註冊成功", "user": response}

@router.post("/login", response_model=AuthResponse) # 🌟 定義回傳格式
async def login(auth_data: UserLogin): # 🌟 使用 UserLogin schema
    response = await supabase_service.sign_in(auth_data.email, auth_data.password)
    if not response:
        raise HTTPException(status_code=401, detail="帳號或密碼錯誤")
    return response