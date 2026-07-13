from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ReportGeneratorPort(ABC):
    """Outbound port interface for generating spreadsheet reports."""

    @abstractmethod
    def generate_excel_report(self, rows: List[Dict[str, Any]], headers: List[str]) -> bytes:
        """Generate an Excel .xlsx file in memory and return bytes."""
        pass
