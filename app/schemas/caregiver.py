"""
監看者(照護者)相關數據模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CaregiverBindRequest(BaseModel):
    """監看者綁定請求"""
    sharing_code: str = Field(..., min_length=8, max_length=8, description="病患的8位分享碼")


class CaregiverLinkResponse(BaseModel):
    """監看者綁定關係回應"""
    id: str
    caregiver_id: str
    patient_id: str
    status: str = Field(..., description="狀態: active/inactive")
    created_at: datetime

    class Config:
        from_attributes = True


class PatientListItem(BaseModel):
    """監看者的病患清單項目"""
    patient_id: str
    patient_name: Optional[str] = None
    sharing_code: str
    status: str
    latest_measurement: Optional[datetime] = None
    bp_status: Optional[str] = None
