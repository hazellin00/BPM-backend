"""
AI 諮詢路由
獨立的 AI 建議端點 (不儲存測量記錄)
"""
from fastapi import APIRouter, HTTPException, status
from app.schemas.ai import AIConsultRequest, AIConsultResponse
from app.services.clinical_matcher import clinical_matcher
from app.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/consult", response_model=AIConsultResponse)
async def get_ai_consultation(request: AIConsultRequest):
    """
    獨立的 AI 飲食諮詢

    不需要登入,不儲存記錄
    適用於快速體驗或公開頁面
    """
    # 1. 分類血壓
    bp_category = clinical_matcher.classify_blood_pressure(
        request.systolic_bp, request.diastolic_bp
    )

    # 2. 臨床案例比對 (如果提供年齡和 BMI)
    clinical_recommendation = {}

    if request.age and request.bmi:
        similar_cases = await clinical_matcher.find_similar_cases(
            age=request.age, bmi=request.bmi, bp_category=bp_category
        )
        clinical_recommendation = clinical_matcher.extract_recommendations(
            similar_cases
        )

    # 3. 生成 AI 建議
    ai_suggestion = await ai_service.generate_dietary_advice(
        systolic=request.systolic_bp,
        diastolic=request.diastolic_bp,
        bp_category=bp_category,
        age=request.age,
        bmi=request.bmi,
        clinical_data=clinical_recommendation,
    )

    # 4. 組合回應
    response = {
        "suggestion": ai_suggestion,
        "bp_category": bp_category,
        **clinical_recommendation,
    }

    logger.info(
        f"✅ AI 諮詢: BP={request.systolic_bp}/{request.diastolic_bp}, Category={bp_category}"
    )

    return response
