from app.handlers import email_handler, logging_handler, rate_limit_handler
from app.models.contact import ContactRequest
from app.services import ai_service, metrics_service


async def process_contact(data: ContactRequest, client_ip: str) -> dict:
    allowed, retry_after = rate_limit_handler.check_rate_limit(client_ip)

    if not allowed:
        logging_handler.log_request(client_ip, data.email, "rate_limited")
        metrics_service.record("rate_limited")
        return {"blocked": True, "retry_after": retry_after}

    ai_analysis = await ai_service.analyze_comment(data.comment)

    email_sent = email_handler.send_contact_emails(
        name=data.name,
        phone=data.phone,
        email=data.email,
        comment=data.comment,
        ai_analysis=ai_analysis,
    )

    status = "success" if email_sent else "email_queued"
    logging_handler.log_request(client_ip, data.email, status)
    metrics_service.record("success")

    return {"blocked": False, "email_sent": email_sent}
