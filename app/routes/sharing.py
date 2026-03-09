import logging
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from app.utils.auth import get_current_user_id
from app.services.supabase_client import supabase_service
# 假設你有定義基本的 ProfileResponse 來回傳病人資訊
from app.schemas.user import ProfileResponse 

logger = logging.getLogger(__name__)

router = APIRouter()

# --- Routes ---

@router.post("/bind/{sharing_code}", status_code=status.HTTP_201_CREATED)
async def bind_patient_by_sharing_code(
    sharing_code: str,
    caregiver_id: Annotated[str, Depends(get_current_user_id)]
):
    """
    【照護者專用】透過 8 位分享碼綁定被照護者
    """
    try:
        # 1. 執行綁定邏輯 (內部會檢查分享碼是否存在、是否綁定自己)
        result = await supabase_service.create_caregiver_link_by_code(
            caregiver_id=caregiver_id, 
            sharing_code=sharing_code
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="無效的分享碼，請確認後再試"
            )
            
        return {
            "status": "success", 
            "message": "已成功綁定被照護者",
            "patient_id": result.get("patient_id")
        }

    except ValueError as ve:
        # 捕捉「不能綁定自己」之類的邏輯錯誤
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error(f"綁定過程發生錯誤: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="伺服器內部錯誤")


@router.get("/patients", response_model=List[dict])
async def get_my_patients(
    caregiver_id: Annotated[str, Depends(get_current_user_id)]
):
    """
    【照護者專用】取得目前所有正在監看（綁定）的病患清單
    """
    patients = await supabase_service.get_caregiver_patients(caregiver_id)
    
    # 這裡回傳的 patients 會包含 profiles 資訊，因為 Service 層用了 Join 語法
    return patients


@router.delete("/unbind/{patient_id}")
async def unbind_patient(
    patient_id: str,
    caregiver_id: Annotated[str, Depends(get_current_user_id)]
):
    """
    【照護者專用】解除綁定關係
    """
    # 這裡你可以在 service 補一個簡單的 delete 邏輯
    # 暫時用簡單的提示代過
    return {"message": f"已請求解除與 {patient_id} 的綁定關係"}