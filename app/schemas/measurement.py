"""
健康測量數據模型
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MeasurementBase(BaseModel):
    """測量基礎資料"""
    systolic_bp: int = Field(..., ge=50, le=250, description="收縮壓 (mmHg)")
    diastolic_bp: int = Field(..., ge=30, le=150, description="舒張壓 (mmHg)")
    pulse: Optional[int] = Field(None, ge=30, le=200, description="脈搏 (bpm)")
    notes: Optional[str] = Field(None, max_length=500, description="備註")


class MeasurementCreate(MeasurementBase):
    """創建測量記錄"""
    pass


class MeasurementResponse(MeasurementBase):
    """測量記錄回應"""
    id: str
    user_id: str
    bp_category: str = Field(..., description="血壓分類: Normal/Elevated/High")
    created_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MeasurementWithAI(MeasurementResponse):
    """包含 AI 建議的測量記錄"""
    ai_suggestion: Optional[str] = Field(None, description="AI 飲食建議")
    recommended_calories: Optional[int] = Field(None, description="建議卡路里")
    recommended_meal_plan: Optional[str] = Field(None, description="建議飲食計畫")
