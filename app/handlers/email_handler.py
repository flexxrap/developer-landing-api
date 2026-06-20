import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings

_logger = logging.getLogger("email")


def _owner_html(name: str, phone: str, email: str, comment: str, ai_analysis: dict | None) -> str:
    if ai_analysis:
        ai_block = f"""<h3>AI-анализ</h3>
<table>
  <tr><td><b>Тональность:</b></td><td>{ai_analysis.get('sentiment', '—')}</td></tr>
  <tr><td><b>Тип запроса:</b></td><td>{ai_analysis.get('type', '—')}</td></tr>
  <tr><td><b>Приоритет:</b></td><td>{ai_analysis.get('priority', '—')}</td></tr>
</table>"""
    else:
        ai_block = "<p><i>AI analysis unavailable</i></p>"

    return f"""<html><body>
<h2>Новая заявка с лендинга</h2>
<table>
  <tr><td><b>Имя:</b></td><td>{name}</td></tr>
  <tr><td><b>Телефон:</b></td><td>{phone}</td></tr>
  <tr><td><b>Email:</b></td><td>{email}</td></tr>
</table>
<h3>Комментарий</h3>
<p>{comment}</p>
{ai_block}
</body></html>"""


def _user_html(name: str) -> str:
    return f"""<html><body>
<h2>Спасибо, {name}!</h2>
<p>Ваша заявка получена. Я свяжусь с вами в ближайшее время.</p>
</body></html>"""


def _build(subject: str, from_: str, to: str, html: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_
    msg["To"] = to
    msg.attach(MIMEText(html, "html", "utf-8"))
    return msg


def send_contact_emails(
    name: str,
    phone: str,
    email: str,
    comment: str,
    ai_analysis: dict | None = None,
) -> bool:
    if not settings.smtp_user or not settings.smtp_password:
        _logger.warning("SMTP credentials not configured, email queued")
        return False

    try:
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
            server.login(settings.smtp_user, settings.smtp_password)

            owner_msg = _build(
                subject=f"Новая заявка от {name}",
                from_=settings.smtp_user,
                to=settings.owner_email,
                html=_owner_html(name, phone, email, comment, ai_analysis),
            )
            server.sendmail(settings.smtp_user, settings.owner_email, owner_msg.as_string())

            user_msg = _build(
                subject="Ваша заявка получена",
                from_=settings.smtp_user,
                to=email,
                html=_user_html(name),
            )
            server.sendmail(settings.smtp_user, email, user_msg.as_string())

        return True
    except Exception as exc:
        _logger.error("SMTP error: %s", exc)
        return False
