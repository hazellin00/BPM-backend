"""
Google Gemini AI 服務
產生「暖心孫女」風格的飲食建議
"""
import google.generativeai as genai
from app.config import settings
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class AIService:
    """Google Gemini AI 諮詢服務"""

    def __init__(self):
        """初始化 Gemini AI"""
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
            logger.info(f"✅ Google Gemini AI 初始化成功: {settings.GEMINI_MODEL}")
        except Exception as e:
            logger.error(f"❌ Gemini AI 初始化失敗: {e}")
            raise

    async def generate_dietary_advice(
        self,
        systolic: int,
        diastolic: int,
        bp_category: str,
        age: Optional[int] = None,
        bmi: Optional[float] = None,
        clinical_data: Optional[Dict] = None,
    ) -> str:
        """
        產生暖心的飲食建議

        Args:
            systolic: 收縮壓
            diastolic: 舒張壓
            bp_category: 血壓分類
            age: 年齡
            bmi: BMI
            clinical_data: 臨床推薦數據 (卡路里、飲食計畫等)

        Returns:
            AI 生成的建議文字 (限 60 字內)
        """
        try:
            # 構建 Prompt (暖心孫女風格)
            prompt = self._build_prompt(
                systolic, diastolic, bp_category, age, bmi, clinical_data
            )

            # 呼叫 Gemini API
            response = self.model.generate_content(prompt)

            # 提取建議文字並限制長度
            suggestion = response.text.strip()
            if len(suggestion) > settings.AI_SUGGESTION_MAX_LENGTH:
                suggestion = suggestion[: settings.AI_SUGGESTION_MAX_LENGTH] + "..."

            logger.info(f"AI 建議生成成功: {suggestion[:30]}...")
            return suggestion

        except Exception as e:
            logger.error(f"AI 建議生成失敗: {e}")
            # 回退到預設建議
            return self._fallback_suggestion(bp_category)

    def _build_prompt(
        self,
        systolic: int,
        diastolic: int,
        bp_category: str,
        age: Optional[int],
        bmi: Optional[float],
        clinical_data: Optional[Dict],
    ) -> str:
        """
        構建 AI Prompt

        設計原則:
        1. 以「護理師孫女」的溫暖口吻
        2. 結合臨床數據給出具體建議
        3. 限制 60 字內
        4. 白話、溫馨、實用
        """
        base_info = f"""你是一位專業且溫柔的護理師，也是長輩的孫女。
現在要給長輩一段簡短、溫馨的飲食與生活建議。

【長輩資訊】
- 血壓: {systolic}/{diastolic} mmHg
- 血壓狀態: {self._translate_bp_category(bp_category)}"""

        if age:
            base_info += f"\n- 年齡: {age} 歲"

        if bmi:
            base_info += f"\n- BMI: {bmi}"

        if clinical_data:
            calories = clinical_data.get("recommended_calories")
            meal_plan = clinical_data.get("recommended_meal_plan")

            if calories:
                base_info += f"\n- 建議每日卡路里: {calories} 大卡"
            if meal_plan:
                base_info += f"\n- 建議飲食類型: {meal_plan}"

        prompt = f"""{base_info}

【任務】
請以「孫女護理師」的溫暖口吻，給長輩一段 **60 字以內** 的飲食或生活建議。
要求:
1. 白話、溫馨、像家人在關心
2. 具體提到飲食建議或生活習慣
3. 避免醫學術語
4. 正向鼓勵的語氣

請直接輸出建議，不要加任何前綴。
"""
        return prompt

    @staticmethod
    def _translate_bp_category(category: str) -> str:
        """血壓分類中文翻譯"""
        translations = {
            "Normal": "正常",
            "Elevated": "偏高",
            "High": "高血壓",
        }
        return translations.get(category, category)

    @staticmethod
    def _fallback_suggestion(bp_category: str) -> str:
        """備用建議 (當 AI 失效時)"""
        suggestions = {
            "Normal": "阿嬤您的血壓很正常唷!繼續保持清淡飲食,多吃蔬菜水果,每天散步30分鐘,身體會越來越好的!",
            "Elevated": "阿公血壓有點偏高,這陣子要少吃鹹的,多喝水多休息,我們一起加油控制好血壓喔!",
            "High": "血壓有點高,要特別注意!建議少油少鹽,多吃深綠色蔬菜,記得按時吃藥,有不舒服一定要告訴我們。",
        }
        return suggestions.get(bp_category, "請保持健康的生活習慣,多運動、均衡飲食,有任何不適請盡快就醫。")


# 全局單例
ai_service = AIService()
