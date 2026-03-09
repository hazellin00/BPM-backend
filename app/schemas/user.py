"""
使用者相關數據模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProfileBase(BaseModel):
    """使用者基本資料"""
    age: Optional[int] = Field(None, ge=0, le=120, description="年齡")
    height: Optional[float] = Field(None, gt=0, description="身高 (cm)")
    weight: Optional[float] = Field(None, gt=0, description="體重 (kg)")
    bmi: Optional[float] = Field(None, ge=0, description="BMI")
    chronic_disease: Optional[str] = Field(None, description="慢性病")
    gender: Optional[str] = Field(None, description="性別")


class ProfileCreate(ProfileBase):
    """創建個人檔案"""
    pass


class ProfileResponse(ProfileBase):
    """個人檔案回應"""
    id: str
    user_id: str
    sharing_code: str = Field(..., description="8位分享碼")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SharingCodeRequest(BaseModel):
    """Sharing Code 綁定請求"""
    sharing_code: str = Field(..., min_length=8, max_length=8, description="8位分享碼")
