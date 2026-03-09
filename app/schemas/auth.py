# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRegister(BaseModel):
    """註冊時要求的欄位"""
    email: EmailStr = Field(..., description="使用者的電子郵件")
    password: str = Field(..., min_length=6, description="密碼，最少 6 位字元")

class UserLogin(BaseModel):
    """登入時要求的欄位"""
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    """回傳給前端的資料結構"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str

    class Config:
        from_attributes = True