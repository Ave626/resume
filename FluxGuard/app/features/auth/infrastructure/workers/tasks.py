from pathlib import Path
from string import Template
import httpx
from app.core.infrastructure.broker.taskiq import broker
from app.core.infrastructure.config.settings import settings

@broker.task
async def send_otp_email_task(email : str,code : str) -> None:
    template = Path(__file__).parent / "templates" / "otp_email.html"
    html = Template(template.read_text(encoding="utf-8")).substitute(code=code)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.EMAIL_FROM,
                "to": [email],
                "subject": "FluxGuard — Код подтверждения",
                "html": html,
            },
        )
        response.raise_for_status()
