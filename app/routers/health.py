import time

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health_check(request: Request):
    uptime = time.time() - request.app.state.start_time
    return {"status": "ok", "uptime_seconds": round(uptime, 2)}
