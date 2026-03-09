"""
健康測量記錄路由
"""
from fastapi import APIRouter, HTTPException, Header, status, Depends, Query
from typing import List, Annotated
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

router = APIRouter()


# --- Routes ---

@router.post("/", response_model=MeasurementWithAI, status_code=status.HTTP_201_CREATED)
async def create_measurement(
    measurement: MeasurementCreate,
    user_id: Annotated[str, Depends(get_current_user_id)] # 🌟 認證升級
):
    """
    創建健康測量記錄 + AI 飲食建議
    """
    # 1. 取得使用者個人檔案 (獲取年齡與 BMI 供 AI 參考)
    profile = await supabase_service.get_profile_by_user_id(user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="請先完成個人檔案設定，以便 AI 提供精準建議",
        )

    # 2. 分類血壓 (假設你的 clinical_matcher 邏輯已就緒)
    # 若還沒寫好，可暫時用我們之前的 calculate_bp_category 替代
    from app.utils.helpers import calculate_bp_category
    bp_category = calculate_bp_category(
        measurement.systolic_bp, measurement.diastolic_bp
    )

    # 3. 儲存測量記錄 (🌟 關鍵：處理別名與 JSON 轉換)
    measurement_data = measurement.model_dump(
        exclude_none=True, 
        mode='json', 
        by_alias=True
    )
    measurement_data["bp_category"] = bp_category

    saved_measurement = await supabase_service.create_measurement(
        user_id, measurement_data
    )

    if not saved_measurement:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="儲存測量記錄失敗",
        )

    # 4. 生成 AI 建議 (獲取 Age/BMI，若無則傳 None)
    # 注意：這裡的 key 可能要根據你 profile 表的真實欄位調整
    age = profile.get("age") 
    bmi = profile.get("bmi")

    # 呼叫你的 AI Service
    # ai_data = await ai_service.generate_dietary_advice(...)
    ai_suggestion = "建議減少鹽分攝取，多吃深色蔬菜。" # 暫時代替
    
    # 5. 組合回應 (符合 MeasurementWithAI 模型)
    response_data = {
        **saved_measurement,
        "ai_suggestion": ai_suggestion,
        "recommended_calories": 1800, # 暫時代替
        "recommended_meal_plan": "地中海飲食" # 暫時代替
    }

    logger.info(f"✅ 使用者 {user_id} 新增測量記錄: {measurement.systolic_bp}/{measurement.diastolic_bp}")
    return response_data


@router.get("/", response_model=List[MeasurementResponse])
async def get_my_measurements(
    user_id: Annotated[str, Depends(get_current_user_id)],
    limit: int = Query(30, le=100),
    include_deleted: bool = False,
):
    """取得我的歷史測量記錄"""
    measurements = await supabase_service.get_measurements(
        user_id, limit=limit, include_deleted=include_deleted
    )
    return measurements


@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_measurement(
    measurement_id: str, 
    user_id: Annotated[str, Depends(get_current_user_id)]
):
    """軟刪除測量記錄"""
    result = await supabase_service.soft_delete_measurement(measurement_id, user_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="測量記錄不存在或無權限操作"
        )

    logger.info(f"✅ 使用者 {user_id} 軟刪除記錄: {measurement_id}")
    return None