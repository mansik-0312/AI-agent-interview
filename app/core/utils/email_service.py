import os
from dotenv import load_dotenv
import httpx
from app.models.email_model import EmailRequest
from jinja2 import Environment, FileSystemLoader

load_dotenv()

EMAIL_SERVICE_URL=os.getenv("EMAIL_SERVICE_URL")

# Setup Jinja2 for HTML templates
template_env = Environment(loader=FileSystemLoader("app/core/utils/templates"))

def render_template(template_name: str, context: dict) -> str:
    template = template_env.get_template(template_name)
    return template.render(**context)

async def notify_via_email(
    to_emails: list[str],
    subject: str,
    body: str,
    cc: list[str] = None,
    bcc: list[str] = None,
    attachments: list[str] = None,
    is_html: bool = True
):
    payload = EmailRequest(
        to=to_emails,
        subject=subject,
        body=body,
        cc=cc or [],
        bcc=bcc or [],
        attachments=attachments or [],
        is_html=is_html
    )

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(f"{EMAIL_SERVICE_URL}/email/send", json=payload.dict())
            print(f"[EMAIL SERVICE] Response: {res.status_code}, {res.text}")
            return res.status_code == 200
        except Exception as e:
            print(f"[ERROR] Failed to call Email Service: {str(e)}")
            return False

