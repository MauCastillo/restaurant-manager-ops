import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Optional

from src.ports.outbound.email_service_port import EmailServicePort
from src.domain.exceptions import DomainException


class GmailSmtpSender(EmailServicePort):
    """Outbound adapter for sending Gmail SMTP emails with attachments matching Cuentas de Cobro .eml format."""

    def __init__(
        self,
        default_sender: Optional[str] = None,
        default_password: Optional[str] = None,
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587
    ):
        self.default_sender = default_sender or os.environ.get("SMTP_USER")
        self.default_password = default_password or os.environ.get("SMTP_PASSWORD")
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send_email_with_attachment(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: str,
        attachment_bytes: bytes,
        attachment_filename: str,
        sender_email: Optional[str] = None,
        sender_password: Optional[str] = None,
        bcc_email: Optional[str] = None
    ) -> bool:
        sender = sender_email or self.default_sender
        password = sender_password or self.default_password

        if not sender or not password:
            raise DomainException(
                "Credenciales de GMAIL incompletas. Por favor ingresa el correo de remitente y la contraseña de aplicación (App Password) de Google."
            )

        # Build outer multipart/mixed MIME message
        msg = MIMEMultipart("mixed")
        msg["From"] = sender
        msg["To"] = to_email
        msg["Subject"] = subject

        # Inner multipart/alternative container for plain text and HTML
        alt_part = MIMEMultipart("alternative")
        alt_part.attach(MIMEText(body_text, "plain", "utf-8"))
        alt_part.attach(MIMEText(body_html, "html", "utf-8"))
        msg.attach(alt_part)

        # Excel attachment
        att = MIMEApplication(attachment_bytes, _subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        att.add_header("Content-Disposition", "attachment", filename=attachment_filename)
        msg.attach(att)

        recipients = [em.strip() for em in to_email.split(",") if em.strip()]
        bcc_recipients = [em.strip() for em in bcc_email.split(",") if em.strip()] if bcc_email else []
        all_recipients = recipients + bcc_recipients

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=20) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(sender, password)
                server.sendmail(sender, all_recipients, msg.as_string())
            return True
        except Exception as e:
            raise DomainException(f"Error al enviar correo vía Gmail SMTP: {str(e)}")
