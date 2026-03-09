"""
健康檢查與系統狀態路由
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    """系統根路徑"""
    return {
        "service": "VitalGuard Core API",
        "status": "operational",
        "message": "守護長輩健康,智慧血壓監測系統已就緒",
        "version": "1.0.0",
    }


@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "message": "系統運作正常"}
