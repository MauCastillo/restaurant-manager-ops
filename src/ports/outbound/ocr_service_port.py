from abc import ABC, abstractmethod
from typing import List, Dict, Any


class OcrServicePort(ABC):
    """Outbound port for analyzing handwritten images and extracting structured sales/purchases."""

    @abstractmethod
    def analyze_handwritten_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> List[Dict[str, Any]]:
        """Analyze an image of handwritten notes and extract a list of records.

        Returns:
            List[Dict[str, Any]]: List of extracted raw objects with keys:
                - 'cliente_texto': str
                - 'concepto': str
                - 'monto': float
                - 'fecha': Optional[str]
        """
        pass
