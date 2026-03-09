"""
使用者個人檔案路由
"""
import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends # 移除了 Header
from app.schemas.user import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.supabase_client import supabase_service
from app.utils.auth import get_current_user_id # 這是你寫好的 HTTPBearer 版本
from app.utils.helpers import generate_sharing_code

logger = logging.getLogger(__name__)

router = APIRouter()

# 不需要再自己寫 get_current_user 了，直接用 get_current_user_id 作為 Depends

# --- Routes ---

@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(
    # 直接使用 utils 裡的 get_current_user_id
    user_id: Annotated[str, Depends(get_current_user_id)]
):
    """取得當前使用者的個人檔案"""
    profile = await supabase_service.get_profile_by_user_id(user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="個人檔案不存在"
        )
    return profile


@router.post("/me", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_my_profile(
    profile_data: ProfileCreate,
    user_id: Annotated[str, Depends(get_current_user_id)]
):
    """創建個人檔案 (自動生成 Sharing Code)"""
    
    # 檢查是否已存在 (這部分沒問題)
    existing = await supabase_service.get_profile_by_user_id(user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="個人檔案已存在"
        )

    sharing_code = generate_sharing_code()
    
    # 這會確保 height 變成 height_cm, birthday 變成 birth_date
    insert_data = profile_data.model_dump(
        exclude_none=True, 
        mode='json', 
        by_alias=True
    )
    
    insert_data["sharing_code"] = sharing_code

    # 寫入資料庫
    profile = await supabase_service.create_profile(user_id, insert_data)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="創建個人檔案失敗"
        )

    logger.info(f"✅ 使用者 {user_id} 創建個人檔案, 分享碼: {sharing_code}")
    return profile

@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_data: ProfileUpdate,
    user_id: Annotated[str, Depends(get_current_user_id)]
):
    """更新個人檔案"""
    # 🌟 mode='json' 處理日期轉字串
    # 🌟 by_alias=True 處理 birthday -> birth_date 的欄位轉換
    update_data = profile_data.model_dump(
        exclude_none=True, 
        mode='json', 
        by_alias=True
    )
    
    if not update_data:
        raise HTTPException(status_code=400, detail="請提供要更新的欄位內容")

    # 現在傳給 supabase_service 的資料，欄位名稱就會是正確的 (如 birth_date)
    profile = await supabase_service.update_profile(user_id, update_data)

    if not profile:
        raise HTTPException(status_code=404, detail="個人檔案不存在")

    return profile