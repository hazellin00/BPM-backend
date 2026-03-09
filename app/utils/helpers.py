"""
通用工具函數
"""
import random
import string
from app.config import settings


def generate_sharing_code(length: int = None) -> str:
    """
    生成隨機分享碼

    Args:
        length: 分享碼長度 (默認使用配置)

    Returns:
        8位隨機字串 (大寫字母+數字)
    """
    if length is None:
        length = settings.SHARING_CODE_LENGTH

    # 使用大寫字母和數字,避免混淆字符 (去除 0, O, I, 1)
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(random.choices(chars, k=length))


def calculate_age_from_birth_year(birth_year: int) -> int:
    """
    根據出生年份計算年齡

    Args:
        birth_year: 出生年份

    Returns:
        年齡
    """
    from datetime import datetime

    current_year = datetime.now().year
    return current_year - birth_year
