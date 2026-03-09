"""
認證與授權工具
處理 JWT 驗證、使用者身份識別等
"""
from fastapi import Header, HTTPException, status
from typing import Optional
import logging

logger = logging.getLogger(__name__)


async def get_current_user_id(authorization: str = Header(None)) -> str:
    """
    從 Authorization Header 中提取使用者 ID

    目前實作: 從 Supabase JWT 中提取 (簡化版)
    TODO: 完整 JWT 驗證

    Args:
        authorization: Bearer token

    Returns:
        使用者 ID

    Raises:
        HTTPException: 未授權
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="需要身份驗證"
        )

    try:
        # 簡化實作: 假設 token 為 "Bearer {user_id}"
        # 實際應使用 jwt.decode() 驗證 Supabase JWT
        token = authorization.replace("Bearer ", "")

        # TODO: 實作完整的 JWT 驗證邏輯
        # 目前直接返回 token 作為 user_id (僅用於開發)
        return token

    except Exception as e:
        logger.error(f"Token 解析失敗: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="無效的身份驗證令牌"
        )


async def verify_caregiver_access(
    caregiver_id: str, patient_id: str
) -> bool:
    """
    驗證監看者是否有權限訪問病患數據

    Args:
        caregiver_id: 監看者 ID
        patient_id: 病患 ID

    Returns:
        是否有權限
    """
    from app.services.supabase_client import supabase_service

    return await supabase_service.check_caregiver_access(caregiver_id, patient_id)
