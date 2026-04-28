"""Email service for password reset and email verification."""

import logging
import smtplib
from email.mime.text import MIMEText

from app.core.config import settings
from app.core.security import create_access_token

logger = logging.getLogger("blog")


def _send_email(to: str, subject: str, body: str) -> bool:
    """Send an email via SMTP. Returns True on success."""
    if not settings.SMTP_HOST:
        logger.warning("SMTP not configured, skipping email to %s", to)
        return False

    try:
        msg = MIMEText(body, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Email sent to %s: %s", to, subject)
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to)
        return False


def _generate_token(user_id: int, purpose: str, expire_minutes: int = 60) -> str:
    """Generate a JWT token for email purposes."""
    from datetime import timedelta
    return create_access_token(
        data={"sub": str(user_id), "purpose": purpose},
        expires_delta=timedelta(minutes=expire_minutes),
    )


def send_password_reset_email(user, db) -> None:
    """Generate and send a password reset email."""
    token = _generate_token(user.id, "password_reset", expire_minutes=30)
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    body = f"""
    <div style="max-width:600px;margin:0 auto;font-family:sans-serif;">
      <h2>Password Reset</h2>
      <p>Click the link below to reset your password. This link expires in 30 minutes.</p>
      <a href="{reset_url}"
         style="display:inline-block;padding:12px 24px;background:#3b82f6;color:#fff;
                text-decoration:none;border-radius:6px;">
        Reset Password
      </a>
      <p>If you didn't request this, you can safely ignore this email.</p>
    </div>
    """
    _send_email(user.email, "Password Reset Request", body)


def send_verification_email(user, db) -> None:
    """Generate and send an email verification link."""
    token = _generate_token(user.id, "email_verify", expire_minutes=1440)  # 24 hours
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    body = f"""
    <div style="max-width:600px;margin:0 auto;font-family:sans-serif;">
      <h2>Verify Your Email</h2>
      <p>Click the link below to verify your email address.</p>
      <a href="{verify_url}"
         style="display:inline-block;padding:12px 24px;background:#22c55e;color:#fff;
                text-decoration:none;border-radius:6px;">
        Verify Email
      </a>
      <p>This link expires in 24 hours.</p>
    </div>
    """
    _send_email(user.email, "Verify Your Email", body)
