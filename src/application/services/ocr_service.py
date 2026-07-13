import datetime
from typing import List, Dict, Any, Optional

from src.ports.outbound.ocr_service_port import OcrServicePort
from src.ports.outbound.client_repository_port import ClientRepositoryPort


class OcrService:
    """Application use case for analyzing handwritten sales images and matching clients."""

    def __init__(self, ocr_port: OcrServicePort, client_repo: ClientRepositoryPort):
        self.ocr_port = ocr_port
        self.client_repo = client_repo

    def analyze_sales_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> List[Dict[str, Any]]:
        raw_rows = self.ocr_port.analyze_handwritten_image(image_bytes, mime_type)
        all_clients = self.client_repo.list_all()

        today_str = datetime.date.today().strftime("%Y-%m-%d")
        enriched_rows = []

        for idx, row in enumerate(raw_rows):
            cliente_texto = (row.get("cliente_texto") or "").strip()
            matched_client = None

            # 1. Exact or partial Cédula match
            for c in all_clients:
                if cliente_texto and cliente_texto in c.cedula:
                    matched_client = c
                    break

            # 2. Substring or word match in Client Name
            if not matched_client and cliente_texto:
                txt_lower = cliente_texto.lower()
                for c in all_clients:
                    name_lower = c.nombre.lower()
                    if txt_lower in name_lower or any(word in name_lower for word in txt_lower.split() if len(word) > 3):
                        matched_client = c
                        break

            fecha_val = row.get("fecha") or today_str

            enriched_rows.append({
                "index": idx + 1,
                "cliente_texto": cliente_texto,
                "client_id": matched_client.id if matched_client else "",
                "client_nombre": matched_client.nombre if matched_client else "",
                "client_cedula": matched_client.cedula if matched_client else "",
                "concepto": row.get("concepto") or "Alimentación",
                "monto": row.get("monto") or 0.0,
                "fecha_compra": fecha_val
            })

        return enriched_rows
