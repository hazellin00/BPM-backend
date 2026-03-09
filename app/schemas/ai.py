"""
AI 建議相關數據模型
"""
from pydantic import BaseModel, Field
from typing import Optional


class AIConsultRequest(BaseModel):
    """AI 諮詢請求"""
    systolic_bp: int = Field(..., ge=50, le=250, description="收縮壓")
    diastolic_bp: int = Field(..., ge=30, le=150, description="舒張壓")
    age: Optional[int] = Field(None, ge=0, le=120, description="年齡")
    bmi: Optional[float] = Field(None, ge=0, description="BMI")


class AIConsultResponse(BaseModel):
    """AI 諮詢回應"""
    suggestion: str = Field(..., description="暖心飲食建議")
    bp_category: str = Field(..., description="血壓分類")
    recommended_calories: Optional[int] = Field(None, description="建議卡路里")
    recommended_meal_plan: Optional[str] = Field(None, description="建議飲食計畫")
    clinical_matches: Optional[int] = Field(None, description="匹配的臨床案例數")


class DietRecommendation(BaseModel):
    """臨床飲食推薦"""
    patient_id: str
    age: int
    bmi: float
    bp_category: str
    recommended_calories: int
    recommended_protein: Optional[int] = None
    recommended_carbs: Optional[int] = None
    recommended_fats: Optional[int] = None
    recommended_meal_plan: str
