from fastapi import APIRouter, HTTPException, Request

from app.models.contact import ContactRequest, ContactResponse
from app.services import contact_service

router = APIRouter()


@router.post("/contact", response_model=ContactResponse)
async def submit_contact(request: Request, body: ContactRequest):
    client_ip = request.client.host
    result = contact_service.process_contact(body, client_ip)

    if result["blocked"]:
        raise HTTPException(
            status_code=429,
            detail={
                "message": "Слишком много запросов. Попробуйте позже.",
                "retry_after": result["retry_after"],
            },
        )

    return ContactResponse(
        success=True,
        message="Заявка получена. Мы свяжемся с вами в ближайшее время.",
    )
