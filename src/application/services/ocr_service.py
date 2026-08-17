import datetime
import unicodedata
from typing import List, Dict, Any, Optional

from src.ports.outbound.ocr_service_port import OcrServicePort
from src.ports.outbound.client_repository_port import ClientRepositoryPort


def _normalize(text: str) -> str:
    """Lowercase and strip accents, e.g. for OCR text that may mangle diacritics."""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.lower().strip()


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

            # 2. Name match, tolerant of handwritten partial names
            # (e.g. "Juan Camilo Castillo" written as "Juan Castillo" or "Camilo Castillo")
            if not matched_client and cliente_texto:
                txt_words = {w for w in _normalize(cliente_texto).split() if len(w) > 2}
                if txt_words:
                    best_clients: List[Any] = []
                    best_score = 0
                    for c in all_clients:
                        name_words = set(_normalize(c.nombre).split())
                        if not txt_words.issubset(name_words):
                            continue
                        score = len(txt_words)
                        if score > best_score:
                            best_score = score
                            best_clients = [c]
                        elif score == best_score:
                            best_clients.append(c)

                    # Only auto-assign when a single client is unambiguously the best match
                    if len(best_clients) == 1:
                        matched_client = best_clients[0]

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
