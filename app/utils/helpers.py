"""
通用工具函數
"""
import random
import string
from app.config import settings

def calculate_bp_category(systolic: int, diastolic: int) -> str:
    """
    根據 AHA (美國心臟協會) 標準分類血壓等級
    
    Args:
        systolic: 收縮壓
        diastolic: 舒張壓
    Returns:
        分類名稱 (Normal/Elevated/Stage 1/Stage 2/Crisis)
    """
    if systolic < 120 and diastolic < 80:
        return "Normal"
    elif 120 <= systolic <= 129 and diastolic < 80:
        return "Elevated"
    elif 130 <= systolic <= 139 or 80 <= diastolic <= 89:
        return "High Blood Pressure (Stage 1)"
    elif systolic >= 140 or diastolic >= 90:
        return "High Blood Pressure (Stage 2)"
    else:
        # 任何一項數值過高即為危機
        return "Hypertensive Crisis"

def generate_sharing_code(length: int = None) -> str:
    """
    生成隨機分享碼
    """
    if length is None:
        # 確保你的 settings 裡有 SHARING_CODE_LENGTH，通常是 8
        length = getattr(settings, "SHARING_CODE_LENGTH", 8)

    # 使用大寫字母和數字, 避免混淆字符 (去除 0, O, I, 1)
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(random.choices(chars, k=length))

def calculate_age_from_birth_year(birth_year: int) -> int:
    """
    根據出生年份計算年齡
    """
    from datetime import datetime
    current_year = datetime.now().year
    return current_year - birth_year