from datetime import date, datetime
from typing import List, Dict, Any, Tuple, Optional

from src.ports.inbound.report_service_port import ReportServicePort
from src.ports.outbound.client_repository_port import ClientRepositoryPort
from src.ports.outbound.purchase_repository_port import PurchaseRepositoryPort
from src.ports.outbound.report_generator_port import ReportGeneratorPort
from src.ports.outbound.email_service_port import EmailServicePort


SPANISH_MONTHS = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre"
}


class ReportService(ReportServicePort):
    """Application use case service for generating Excel date-range reports and sending via Gmail."""

    def __init__(
        self,
        client_repo: ClientRepositoryPort,
        purchase_repo: PurchaseRepositoryPort,
        report_generator: ReportGeneratorPort,
        email_sender: EmailServicePort
    ):
        self.client_repo = client_repo
        self.purchase_repo = purchase_repo
        self.report_generator = report_generator
        self.email_sender = email_sender

    def get_default_date_range(self) -> Tuple[str, str]:
        today = date.today()
        # Typically 20th of previous month to 19th of current month
        if today.day < 20:
            # We are before the 20th, so current billing end is this month's 19th
            end_date = today.replace(day=19)
            if today.month == 1:
                start_date = date(today.year - 1, 12, 20)
            else:
                start_date = today.replace(month=today.month - 1, day=20)
        else:
            # We are on or after 20th, so billing starts 20th of this month to 19th of next month
            start_date = today.replace(day=20)
            if today.month == 12:
                end_date = date(today.year + 1, 1, 19)
            else:
                end_date = today.replace(month=today.month + 1, day=19)

        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

    def format_report_filename(self, start_date: str, end_date: str) -> str:
        try:
            dt_start = datetime.strptime(start_date, "%Y-%m-%d")
            dt_end = datetime.strptime(end_date, "%Y-%m-%d")
            m_start = SPANISH_MONTHS.get(dt_start.month, "Mes")
            m_end = SPANISH_MONTHS.get(dt_end.month, "Mes")
            return f"{m_start} {dt_start.day} hasta {m_end} {dt_end.day} {dt_end.year}.xlsx"
        except Exception:
            return f"Informe_{start_date}_hasta_{end_date}.xlsx"

    def generate_report_data(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        clients = self.client_repo.list_all()
        rows = []

        for c in clients:
            # Filter purchases for this client within date range
            all_purchases = self.purchase_repo.find_by_client_id(c.id)
            period_purchases = [
                p for p in all_purchases
                if start_date <= p.fecha_compra <= end_date
            ]
            period_monto = sum(p.monto for p in period_purchases)

            # In the reference spreadsheet, 'Valor a Descontar' is the total to discount
            # If the client has base discount or purchases, we include their total
            total_descontar = c.valor_a_descontar + period_monto

            rows.append({
                "client_id": c.id,
                "nombre": c.nombre,
                "cedula": c.cedula,
                "proceso_desempeno": c.proceso_desempeno,
                "valor_a_descontar": total_descontar,
                "period_monto": period_monto,
                "base_descuento": c.valor_a_descontar
            })

        # Sort by nombre
        rows.sort(key=lambda x: x["nombre"].lower())
        return rows

    def generate_report_excel(self, start_date: str, end_date: str) -> Tuple[bytes, str]:
        rows = self.generate_report_data(start_date, end_date)
        headers = ["Nombre", "Cedula", "Porceso de Desempeno", "Valor a Descontar"]
        excel_bytes = self.report_generator.generate_excel_report(rows, headers)
        filename = self.format_report_filename(start_date, end_date)
        return excel_bytes, filename

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
        excel_bytes, filename = self.generate_report_excel(start_date, end_date)

        # Generate HTML version of body
        body_html = f"""<div style="font-family: 'Outfit', Arial, sans-serif; color: #1e293b; line-height: 1.6;">
            <p>{body_text.replace(chr(10), '<br>')}</p>
        </div>"""

        success = self.email_sender.send_email_with_attachment(
            to_email=to_email,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            attachment_bytes=excel_bytes,
            attachment_filename=filename,
            sender_email=sender_email,
            sender_password=sender_password
        )

        if success:
            return f"Correo enviado exitosamente a {to_email} con el archivo adjunto {filename}."
        return "No se pudo enviar el correo."
