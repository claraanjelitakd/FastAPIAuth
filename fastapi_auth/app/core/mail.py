from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from app.core.config import settings
from pathlib import Path

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=settings.SMTP_TLS,
    MAIL_SSL_TLS=settings.SMTP_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_FROM_NAME=settings.EMAILS_FROM_NAME,
)

fastmail = FastMail(conf)

async def send_verification_email(email: EmailStr, token: str):
    verification_url = f"{settings.FRONTEND_HOST}/verify/{token}"
    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=f"Click the link to verify your email: {verification_url}",
        subtype=MessageType.html
    )
    try:
        await fastmail.send_message(message)
        print(f"Email sent successfully to {email}")
    except Exception as e:
        print("\n" + "="*50)
        print(f"SMTP ERROR: {str(e)}")
        print(f"🔗 SIMULATION LINK: {verification_url}")
        print("="*50 + "\n")

async def send_reset_password_email(email: EmailStr, token: str):
    reset_url = f"{settings.FRONTEND_HOST}/reset-password?token={token}"
    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[email],
        body=f"Click the link to reset your password: {reset_url}. This link expires in 15 minutes.",
        subtype=MessageType.html
    )
    await fastmail.send_message(message)
