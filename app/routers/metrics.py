from fastapi import APIRouter

from app.services import metrics_service

router = APIRouter()


@router.get("/metrics")
async def get_metrics():
    return metrics_service.get_all()
