from abc import ABC, abstractmethod
from typing import Optional


class EmailServicePort(ABC):
    """Outbound port interface for sending email notifications and reports."""

    @abstractmethod
    def send_email_with_attachment(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: str,
        attachment_bytes: bytes,
        attachment_filename: str,
        sender_email: Optional[str] = None,
        sender_password: Optional[str] = None
    ) -> bool:
        """Send an email with an attachment via SMTP. Returns True if successful."""
        pass
