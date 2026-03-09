from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated, List
from app.schemas.caregiver import (
    CaregiverBindRequest,
    CaregiverLinkResponse,
    PatientListItem,
)
from app.schemas.measurement import MeasurementResponse
from app.services.supabase_client import supabase_service
from app.utils.auth import get_current_user_id # 🌟 確保這裏引入的是優化後的版本
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# --- Routes ---

@router.post("/bind", response_model=CaregiverLinkResponse, status_code=status.HTTP_201_CREATED)
async def bind_patient(
    request: CaregiverBindRequest, 
    # 🌟 改用 Depends，FastAPI 會幫你擋掉沒帶 Token 的人，並直接傳回解碼後的 caregiver_id
    caregiver_id: Annotated[str, Depends(get_current_user_id)]
):
    """
    綁定病患 (透過 8 位 Sharing Code)
    """
    # 1. 查找病患 (確保 Service 裡的方法名稱與此一致)
    patient_profile = await supabase_service.get_id_by_sharing_code(
        request.sharing_code
    )

    if not patient_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="分享碼無效或病患不存在"
        )

    # 🌟 修正：根據我們先前的 profiles 表結構，UUID 欄位叫做 'id'
    patient_id = patient_profile 

    if caregiver_id == patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="不能綁定自己的分享碼"
        )

    # 2. 檢查是否已綁定
    has_access = await supabase_service.check_caregiver_access(
        caregiver_id, patient_id
    )

    if has_access:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="已綁定過此病患"
        )

    # 3. 創建綁定關係
    link = await supabase_service.create_caregiver_link(
        caregiver_id=caregiver_id, patient_id=patient_id, status="active"
    )

    if not link:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="綁定失敗"
        )

    logger.info(f"✅ 監看者 {caregiver_id} 成功綁定病患 {patient_id}")
    return link


@router.get("/patients", response_model=List[PatientListItem])
async def get_my_patients(
    caregiver_id: Annotated[str, Depends(get_current_user_id)]
):
    """取得我監看的所有病患清單"""
    patients = await supabase_service.get_caregiver_patients(caregiver_id)
    return patients


@router.get("/patients/{patient_id}/measurements", response_model=List[MeasurementResponse])
async def get_patient_measurements(
    patient_id: str, 
    caregiver_id: Annotated[str, Depends(get_current_user_id)],
    limit: int = 30
):
    """
    取得病患的測量記錄 (僅限已綁定的監看者)
    """
    # 1. 權限檢查
    has_access = await supabase_service.check_caregiver_access(
        caregiver_id, patient_id
    )

    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="無權限訪問此病患數據"
        )

    # 2. 取得測量記錄
    measurements = await supabase_service.get_measurements(
        patient_id, limit=limit, include_deleted=False
    )

    logger.info(f"✅ 監看者 {caregiver_id} 查看病患 {patient_id} 的數據")
    return measurements