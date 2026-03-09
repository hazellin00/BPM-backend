"""
使用者個人檔案路由
"""
from fastapi import APIRouter, HTTPException, Header, status
from app.schemas.user import ProfileCreate, ProfileResponse
from app.services.supabase_client import supabase_service
from app.utils.auth import get_current_user_id
from app.utils.helpers import generate_sharing_code
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(authorization: str = Header(None)):
    """取得當前使用者的個人檔案"""
    user_id = await get_current_user_id(authorization)

    profile = await supabase_service.get_profile_by_user_id(user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="個人檔案不存在"
        )

    return profile


@router.post("/me", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_my_profile(
    profile_data: ProfileCreate, authorization: str = Header(None)
):
    """創建個人檔案 (自動生成 Sharing Code)"""
    user_id = await get_current_user_id(authorization)

    # 檢查是否已存在
    existing = await supabase_service.get_profile_by_user_id(user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="個人檔案已存在"
        )

    # 生成唯一的 Sharing Code
    sharing_code = generate_sharing_code()

    # TODO: 檢查 sharing_code 是否重複 (機率極低)

    # 創建檔案
    data = {
        **profile_data.dict(exclude_none=True),
        "sharing_code": sharing_code,
    }

    profile = await supabase_service.create_profile(user_id, data)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="創建個人檔案失敗"
        )

    logger.info(f"✅ 使用者 {user_id} 創建個人檔案,分享碼: {sharing_code}")
    return profile


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_data: ProfileCreate, authorization: str = Header(None)
):
    """更新個人檔案"""
    user_id = await get_current_user_id(authorization)

    data = profile_data.dict(exclude_none=True)

    profile = await supabase_service.update_profile(user_id, data)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="個人檔案不存在"
        )

    logger.info(f"✅ 使用者 {user_id} 更新個人檔案")
    return profile
