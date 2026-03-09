from pydantic import BaseModel, Field, ConfigDict, AliasChoices
from typing import Optional
from datetime import datetime, date

class ProfileBase(BaseModel):
    """使用者基本資料 (定義輸入輸出的欄位映射)"""
    full_name: Optional[str] = Field(None, description="全名")
    
    # 🌟 修正：輸入輸出都對應到資料庫的 height_cm
    height: Optional[float] = Field(
        None, 
        validation_alias=AliasChoices("height", "height_cm"), 
        serialization_alias="height_cm",
        description="身高 (cm)"
    )
    
    # 🌟 修正：輸入輸出都對應到資料庫的 current_weight_kg
    weight: Optional[float] = Field(
        None, 
        validation_alias=AliasChoices("weight", "current_weight_kg"), 
        serialization_alias="current_weight_kg",
        description="體重 (kg)"
    )
    
    gender: Optional[str] = Field(None, description="性別")
    chronic_disease: Optional[str] = Field(None, description="慢性病")
    
    # 🌟 修正：輸入輸出都對應到資料庫的 birth_date
    birthday: Optional[date] = Field(
        None, 
        validation_alias=AliasChoices("birthday", "birth_date"),
        serialization_alias="birth_date",
        description="生日"
    )

    # 這裡很關鍵：告訴 Pydantic 同時支援名稱與別名
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class ProfileCreate(ProfileBase):
    """創建個人檔案"""
    full_name: str 

class ProfileResponse(ProfileBase):
    """個人檔案回應"""
    # 將資料庫的 id 對應到 user_id
    user_id: str = Field(..., validation_alias="id") 
    sharing_code: str = Field(..., description="8位分享碼")
    created_at: datetime
    updated_at: Optional[datetime] = None

class ProfileUpdate(ProfileBase):
    """
    用於 PATCH 請求的 Schema
    直接繼承 ProfileBase 即可，因為 Base 裡所有欄位本來就是 Optional
    這樣可以確保 serialization_alias (別名) 也能被繼承
    """
    pass