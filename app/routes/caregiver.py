"""
監看者(照護者)路由
"""
from fastapi import APIRouter, HTTPException, Header, status
from typing import List
from app.schemas.caregiver import (
    CaregiverBindRequest,
    CaregiverLinkResponse,
    PatientListItem,
)
from app.schemas.measurement import MeasurementResponse
from app.services.supabase_client import supabase_service
from app.utils.auth import get_current_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/bind", response_model=CaregiverLinkResponse, status_code=status.HTTP_201_CREATED)
async def bind_patient(
    request: CaregiverBindRequest, authorization: str = Header(None)
):
    """
    綁定病患 (透過 8 位 Sharing Code)

    流程:
    1. 驗證監看者身份
    2. 根據 Sharing Code 查找病患
    3. 創建綁定關係
    """
    caregiver_id = await get_current_user_id(authorization)

    # 1. 查找病患
    patient_profile = await supabase_service.get_profile_by_sharing_code(
        request.sharing_code
    )

    if not patient_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="分享碼無效或病患不存在"
        )

    patient_id = patient_profile.get("user_id")

    # 2. 檢查是否已綁定
    existing_link = await supabase_service.check_caregiver_access(
        caregiver_id, patient_id
    )

    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="已綁定此病患"
        )

    # 3. 創建綁定關係
    link = await supabase_service.create_caregiver_link(
        caregiver_id=caregiver_id, patient_id=patient_id, status="active"
    )

    if not link:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="綁定失敗"
        )

    logger.info(f"✅ 監看者 {caregiver_id} 綁定病患 {patient_id}")
    return link


@router.get("/patients", response_model=List[PatientListItem])
async def get_my_patients(authorization: str = Header(None)):
    """取得我監看的所有病患清單"""
    caregiver_id = await get_current_user_id(authorization)

    patients = await supabase_service.get_caregiver_patients(caregiver_id)

    # TODO: 格式化回應,加入最新測量資訊
    return patients


@router.get("/patients/{patient_id}/measurements", response_model=List[MeasurementResponse])
async def get_patient_measurements(
    patient_id: str, limit: int = 30, authorization: str = Header(None)
):
    """
    取得病患的測量記錄

    權限檢查: 僅限已綁定的監看者
    """
    caregiver_id = await get_current_user_id(authorization)

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

    logger.info(f"✅ 監看者 {caregiver_id} 查看病患 {patient_id} 的測量記錄")
    return measurements
