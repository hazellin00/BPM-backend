"""
臨床案例比對服務 (The Brain)
基於 KNN 概念，從 5000 筆臨床數據中找出最相似案例
"""
from typing import List, Dict, Optional
from app.services.supabase_client import supabase_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ClinicalMatcher:
    """臨床案例智慧比對引擎"""

    @staticmethod
    def classify_blood_pressure(systolic: int, diastolic: int) -> str:
        """
        血壓分類演算法

        Args:
            systolic: 收縮壓
            diastolic: 舒張壓

        Returns:
            分類: Normal / Elevated / High
        """
        if systolic < 120 and diastolic < 80:
            return "Normal"
        elif 120 <= systolic < 130 and diastolic < 80:
            return "Elevated"
        else:
            return "High"

    @staticmethod
    def calculate_bmi(height_cm: float, weight_kg: float) -> float:
        """
        計算 BMI

        Args:
            height_cm: 身高 (cm)
            weight_kg: 體重 (kg)

        Returns:
            BMI 值
        """
        height_m = height_cm / 100
        return round(weight_kg / (height_m ** 2), 2)

    async def find_similar_cases(
        self, age: int, bmi: float, bp_category: str, limit: int = None
    ) -> List[Dict]:
        """
        從臨床知識庫中找出最相似的案例

        實作邏輯:
        1. 年齡 ±5 歲
        2. BMI ±2
        3. 相同血壓分類

        Args:
            age: 使用者年齡
            bmi: 使用者 BMI
            bp_category: 血壓分類
            limit: 返回案例數量 (默認使用配置的 KNN_NEIGHBORS)

        Returns:
            相似臨床案例列表
        """
        if limit is None:
            limit = settings.KNN_NEIGHBORS

        try:
            cases = await supabase_service.query_similar_cases(
                age=age, bmi=bmi, bp_category=bp_category, limit=limit
            )

            if not cases:
                logger.warning(
                    f"未找到相似案例: age={age}, bmi={bmi}, bp_category={bp_category}"
                )
                # 如果沒有精確匹配，嘗試只匹配血壓分類
                cases = await self._fallback_query(bp_category, limit)

            return cases

        except Exception as e:
            logger.error(f"臨床案例比對失敗: {e}")
            return []

    async def _fallback_query(self, bp_category: str, limit: int) -> List[Dict]:
        """備用查詢: 僅根據血壓分類查詢"""
        try:
            response = (
                supabase_service.client.table("dietary_knowledge_base")
                .select("*")
                .eq("bp_category", bp_category)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"備用查詢失敗: {e}")
            return []

    def extract_recommendations(self, cases: List[Dict]) -> Dict[str, any]:
        """
        從匹配的案例中提取飲食建議

        取平均值策略:
        - 建議卡路里: 取平均
        - 建議蛋白質/碳水/脂肪: 取平均
        - 飲食計畫: 取最常見的

        Args:
            cases: 臨床案例列表

        Returns:
            彙總的飲食建議
        """
        if not cases:
            return {
                "recommended_calories": None,
                "recommended_meal_plan": "均衡飲食",
                "recommended_protein": None,
                "recommended_carbs": None,
                "recommended_fats": None,
            }

        # 計算平均卡路里
        avg_calories = sum(c.get("recommended_calories", 0) for c in cases) // len(cases)

        # 計算平均營養素
        avg_protein = sum(c.get("recommended_protein", 0) for c in cases) // len(cases)
        avg_carbs = sum(c.get("recommended_carbs", 0) for c in cases) // len(cases)
        avg_fats = sum(c.get("recommended_fats", 0) for c in cases) // len(cases)

        # 找出最常見的飲食計畫
        meal_plans = [c.get("recommended_meal_plan", "") for c in cases]
        most_common_plan = max(set(meal_plans), key=meal_plans.count)

        return {
            "recommended_calories": avg_calories,
            "recommended_meal_plan": most_common_plan,
            "recommended_protein": avg_protein,
            "recommended_carbs": avg_carbs,
            "recommended_fats": avg_fats,
            "clinical_matches": len(cases),
        }


# 全局單例
clinical_matcher = ClinicalMatcher()
