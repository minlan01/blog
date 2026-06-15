"""Email service for password reset and email verification."""

import logging
import smtplib
import threading
from email.mime.text import MIMEText

from app.core.config import settings
from app.core.security import create_purpose_token

logger = logging.getLogger("blog")


class _SMTPConnectionPool:
    def __init__(self, max_size: int = 3):
        self._max_size = max_size
        self._pool: list[smtplib.SMTP] = []
        self._lock = threading.Lock()

    def _create(self) -> smtplib.SMTP:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=30)
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        return server

    def acquire(self) -> smtplib.SMTP:
        with self._lock:
            if self._pool:
                return self._pool.pop()
        return self._create()

    def release(self, server: smtplib.SMTP) -> None:
        try:
            server.noop()
            with self._lock:
                if len(self._pool) < self._max_size:
                    self._pool.append(server)
                    return
        except Exception:
            pass
        try:
            server.quit()
        except Exception:
            pass

    def close_all(self) -> None:
        with self._lock:
            while self._pool:
                try:
                    self._pool.pop().quit()
                except Exception:
                    pass


_pool = _SMTPConnectionPool()


def close_email_pool() -> None:
    _pool.close_all()


def _send_email(to: str, subject: str, body: str) -> bool:
    if not settings.SMTP_HOST:
        logger.warning("SMTP not configured, skipping email to %s", to)
        return False

    server = None
    try:
        msg = MIMEText(body, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM
        msg["To"] = to

        server = _pool.acquire()
        server.send_message(msg)
        _pool.release(server)
        server = None
        logger.info("Email sent to %s: %s", to, subject)
        return True
    except Exception:
        if server:
            try:
                server.quit()
            except Exception:
                pass
        logger.exception("Failed to send email to %s", to)
        return False


def _generate_token(user_id: int, purpose: str, expire_minutes: int = 60) -> str:
    from datetime import timedelta
    return create_purpose_token(
        data={"sub": str(user_id)},
        purpose=purpose,
        expires_delta=timedelta(minutes=expire_minutes),
    )


def send_password_reset_email(user, db) -> None:
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
    token = _generate_token(user.id, "email_verify", expire_minutes=1440)
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
