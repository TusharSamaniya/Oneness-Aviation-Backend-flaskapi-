from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Email connection config
mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)

fast_mail = FastMail(mail_config)

# Jinja2 template env
templates_dir = Path(__file__).parent.parent / "templates" / "email"
jinja_env = Environment(loader=FileSystemLoader(str(templates_dir)))


def render_template(template_name: str, context: dict) -> str:
    template = jinja_env.get_template(template_name)
    return template.render(**context)


async def send_email(to: str, subject: str, html_body: str) -> None:
    """Send a single HTML email. Silently logs errors so the API doesn't break."""
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[to],
            body=html_body,
            subtype=MessageType.html,
        )
        await fast_mail.send_message(message)
    except Exception as e:
        logger.error(f"Email send failed to {to}: {e}")


async def send_enquiry_confirmation(name: str, email: str, enquiry_type: str) -> None:
    html = render_template("enquiry_confirmation.html", {
        "name": name,
        "enquiry_type": enquiry_type,
        "company_name": settings.APP_NAME,
    })
    await send_email(email, f"We've received your enquiry — {settings.APP_NAME}", html)


async def send_admin_enquiry_notification(name: str, email: str, phone: str, enquiry_type: str, message: str = "") -> None:
    html = render_template("admin_enquiry_notification.html", {
        "name": name,
        "email": email,
        "phone": phone,
        "enquiry_type": enquiry_type,
        "message": message,
    })
    await send_email(
        settings.ADMIN_EMAIL,
        f"New enquiry: {enquiry_type} — {name}",
        html,
    )


async def send_charter_confirmation(name: str, email: str, from_city: str, to_city: str, departure_date: str) -> None:
    html = render_template("charter_confirmation.html", {
        "name": name,
        "from_city": from_city,
        "to_city": to_city,
        "departure_date": departure_date,
        "company_name": settings.APP_NAME,
    })
    await send_email(email, f"Charter request received — {settings.APP_NAME}", html)


async def send_membership_welcome(name: str, email: str, tier: str, end_date: str, flight_credit: str) -> None:
    html = render_template("membership_welcome.html", {
        "name": name,
        "tier": tier.capitalize(),
        "end_date": end_date,
        "flight_credit": flight_credit,
        "company_name": settings.APP_NAME,
    })
    await send_email(email, f"Welcome to the Oneness {tier.capitalize()} Circle!", html)


async def send_payment_receipt(name: str, email: str, amount: str, purpose: str, payment_id: str) -> None:
    html = render_template("payment_receipt.html", {
        "name": name,
        "amount": amount,
        "purpose": purpose,
        "payment_id": payment_id,
        "company_name": settings.APP_NAME,
    })
    await send_email(email, f"Payment receipt — {settings.APP_NAME}", html)


async def send_password_reset(name: str, email: str, reset_link: str) -> None:
    html = render_template("password_reset.html", {
        "name": name,
        "reset_link": reset_link,
        "company_name": settings.APP_NAME,
    })
    await send_email(email, f"Reset your password — {settings.APP_NAME}", html)
