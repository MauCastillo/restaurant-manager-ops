import base64
import json
import os
import urllib.request
import urllib.error
import ssl
from typing import List, Dict, Any, Optional

from src.ports.outbound.ocr_service_port import OcrServicePort
from src.domain.exceptions import DomainException


class GeminiOcrAdapter(OcrServicePort):
    """Outbound adapter for analyzing handwritten sales notes using Google Gemini REST API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")

    def _get_ssl_context(self):
        try:
            import certifi
            return ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            return ssl._create_unverified_context()

    def analyze_handwritten_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> List[Dict[str, Any]]:
        if not self.api_key:
            raise DomainException("Clave de API de Google Gemini no configurada.")

        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = """
Analiza cuidadosamente esta fotografía que contiene escritura a mano (notas manuscritas, recibos o listas de consumo/ventas).
Identifica cada renglón o transacción registrada y extrae un arreglo JSON donde cada elemento tenga exactamente estas claves:
- "cliente_texto": El nombre, apellido o número de cédula escrito en la línea (ej. "Carlos Hurtado", "16848254", "Luis").
- "concepto": El concepto o descripción del consumo o venta (ej. "Alimentación", "Almuerzo", "Desayuno", "Uniforme"). Si en el papel solo aparece el nombre y el valor sin concepto explícito, asigna "Alimentación".
- "monto": El monto o valor monetario en número flotante positivo (ej. 15000.0, 20500.0). Elimina símbolos de peso o comas.
- "fecha": La fecha si aparece escrita en el papel en formato "YYYY-MM-DD" (o "2026-MM-DD" si se deduce el mes/día). Si no hay fecha visible, pon null.

Devuelve EXCLUSIVAMENTE una lista JSON válida [] sin texto adicional ni bloques markdown extra.
"""

        models_to_try = [
            self.model,
            "gemini-3.1-flash-lite-preview",
            "gemini-3.1-flash-lite",
            "gemini-flash-lite-latest",
            "gemini-flash-latest"
        ]
        # Remove duplicates preserving order
        models_to_try = list(dict.fromkeys(models_to_try))

        last_error = None

        for mdl in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={self.api_key}"
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": img_b64
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "response_mime_type": "application/json"
                }
            }

            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            try:
                with urllib.request.urlopen(req, context=self._get_ssl_context(), timeout=30) as response:
                    res_json = json.loads(response.read().decode("utf-8"))
                    text_res = res_json["candidates"][0]["content"]["parts"][0]["text"]
                    cleaned_text = text_res.strip()
                    if cleaned_text.startswith("```json"):
                        cleaned_text = cleaned_text[7:]
                    if cleaned_text.endswith("```"):
                        cleaned_text = cleaned_text[:-3]
                    cleaned_text = cleaned_text.strip()

                    parsed = json.loads(cleaned_text)
                    if not isinstance(parsed, list):
                        raise ValueError("La respuesta de Gemini no es una lista JSON.")

                    results = []
                    for item in parsed:
                        if not isinstance(item, dict):
                            continue
                        monto_raw = item.get("monto", 0.0)
                        try:
                            monto_val = float(monto_raw)
                        except (ValueError, TypeError):
                            monto_val = 0.0

                        results.append({
                            "cliente_texto": str(item.get("cliente_texto") or "").strip(),
                            "concepto": str(item.get("concepto") or "Alimentación").strip(),
                            "monto": monto_val,
                            "fecha": item.get("fecha")
                        })
                    return results
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8")
                last_error = f"HTTP {e.code}: {err_body}"
                if e.code in (404, 429):
                    continue
                break
            except Exception as e:
                last_error = str(e)
                continue

        raise DomainException(f"Error procesando imagen manuscrita con IA Gemini OCR: {last_error}")
