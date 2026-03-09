"""
健康測量記錄路由
"""
from fastapi import APIRouter, HTTPException, Header, status
from typing import List
from app.schemas.measurement import (
    MeasurementCreate,
    MeasurementResponse,
    MeasurementWithAI,
)
from app.services.supabase_client import supabase_service
from app.services.clinical_matcher import clinical_matcher
from app.services.ai_service import ai_service
from app.utils.auth import get_current_user_id
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/measurements", tags=["Measurements"])


@router.post(
    "/",
    response_model=MeasurementWithAI,
    status_code=status.HTTP_201_CREATED,
)
async def create_measurement(
    measurement: MeasurementCreate, authorization: str = Header(None)
):
    """
    創建健康測量記錄 + AI 飲食建議

    流程:
    1. 儲存測量記錄
    2. 分類血壓等級
    3. 從臨床知識庫查找相似案例
    4. 生成 AI 暖心建議
    """
    user_id = await get_current_user_id(authorization)

    # 1. 取得使用者個人檔案
    profile = await supabase_service.get_profile_by_user_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="請先完成個人檔案設定",
        )

    # 2. 分類血壓
    bp_category = clinical_matcher.classify_blood_pressure(
        measurement.systolic_bp, measurement.diastolic_bp
    )

    # 3. 儲存測量記錄
    measurement_data = {
        **measurement.dict(exclude_none=True),
        "bp_category": bp_category,
    }

    saved_measurement = await supabase_service.create_measurement(
        user_id, measurement_data
    )

    if not saved_measurement:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="儲存測量記錄失敗",
        )

    # 4. 臨床案例比對 (如果有年齡和 BMI)
    clinical_recommendation = {}
    age = profile.get("age")
    bmi = profile.get("bmi")

    if age and bmi:
        similar_cases = await clinical_matcher.find_similar_cases(
            age=age, bmi=bmi, bp_category=bp_category
        )
        clinical_recommendation = clinical_matcher.extract_recommendations(
            similar_cases
        )

    # 5. 生成 AI 建議
    ai_suggestion = await ai_service.generate_dietary_advice(
        systolic=measurement.systolic_bp,
        diastolic=measurement.diastolic_bp,
        bp_category=bp_category,
        age=age,
        bmi=bmi,
        clinical_data=clinical_recommendation,
    )

    # 6. 組合回應
    response = {
        **saved_measurement,
        "ai_suggestion": ai_suggestion,
        **clinical_recommendation,
    }

    logger.info(
        f"✅ 使用者 {user_id} 新增測量記錄: {measurement.systolic_bp}/{measurement.diastolic_bp}"
    )

    return response


@router.get("/", response_model=List[MeasurementResponse])
async def get_my_measurements(
    limit: int = 30,
    include_deleted: bool = False,
    authorization: str = Header(None),
):
    """取得我的測量記錄"""
    user_id = await get_current_user_id(authorization)

    measurements = await supabase_service.get_measurements(
        user_id, limit=limit, include_deleted=include_deleted
    )

    return measurements


@router.get("/{measurement_id}", response_model=MeasurementResponse)
async def get_measurement(measurement_id: str, authorization: str = Header(None)):
    """取得單筆測量記錄"""
    user_id = await get_current_user_id(authorization)

    # TODO: 實作單筆查詢
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="功能開發中"
    )


@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_measurement(measurement_id: str, authorization: str = Header(None)):
    """
    軟刪除測量記錄

    僅更新 deleted_at,不實際刪除數據
    """
    user_id = await get_current_user_id(authorization)

    result = await supabase_service.soft_delete_measurement(measurement_id, user_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="測量記錄不存在"
        )

    logger.info(f"✅ 使用者 {user_id} 軟刪除測量記錄: {measurement_id}")
    return None
