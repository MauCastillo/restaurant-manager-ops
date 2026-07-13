from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional


class ReportServicePort(ABC):
    """Primary inbound port for date-range billing reports and Excel exports."""

    @abstractmethod
    def get_default_date_range(self) -> Tuple[str, str]:
        """Return the typical billing period (20th of previous month to 19th of current month)."""
        pass

    @abstractmethod
    def format_report_filename(self, start_date: str, end_date: str) -> str:
        """Return formatted filename like 'Mayo 20 hasta Junio 19 2026.xlsx'."""
        pass

    @abstractmethod
    def generate_report_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Calculate client balances and report rows for the given date range."""
        pass

    @abstractmethod
    def generate_report_excel(self, start_date: str, end_date: str) -> Tuple[bytes, str]:
        """Generate Excel workbook bytes and filename for the date range."""
        pass

    @abstractmethod
    def send_report_by_email(
        self,
        start_date: str,
        end_date: str,
        to_email: str,
        subject: str,
        body_text: str,
        sender_email: Optional[str] = None,
        sender_password: Optional[str] = None
    ) -> str:
        """Generate and email the Excel report via Gmail. Returns status message."""
        pass
