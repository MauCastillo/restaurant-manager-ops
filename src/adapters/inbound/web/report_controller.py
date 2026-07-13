from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, current_app
import io

from src.adapters.inbound.web.auth_controller import login_required
from src.domain.exceptions import DomainException

report_bp = Blueprint("reports", __name__, url_prefix="/reports")


@report_bp.route("/", methods=["GET"])
@login_required
def report_dashboard():
    service = current_app.report_service
    def_start, def_end = service.get_default_date_range()

    start_date = request.args.get("start_date", def_start)
    end_date = request.args.get("end_date", def_end)

    rows = service.generate_report_data(start_date, end_date)
    filename = service.format_report_filename(start_date, end_date)

    # Default email text matching user's Cuentas de Cobro EML
    default_subject = "Cuentas de Cobro del Casino del Pool de Ambulancias"
    default_body = (
        "Hola buenos dias.\n\n"
        'Adjunto a este correo las cuentas de cobro del casino de pool de ambulancias "Restaurante Doña O". '
        "El detalle se encuentra en el archivo Excel adjunto.\n\n"
        "Cualquier duda, por favor, avísenme.\n\n"
        "Saludos,\n\n"
        "Olivia Mina Valencia\n"
        "Administradora\n"
        '"Restaurante Doña O"'
    )

    return render_template(
        "reports/index.html",
        rows=rows,
        start_date=start_date,
        end_date=end_date,
        filename=filename,
        default_subject=default_subject,
        default_body=default_body,
        total_monto=sum(r["valor_a_descontar"] for r in rows)
    )


@report_bp.route("/download", methods=["POST"])
@login_required
def download_excel():
    service = current_app.report_service
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    if not start_date or not end_date:
        flash("Debes seleccionar un rango de fechas válido.", "danger")
        return redirect(url_for("reports.report_dashboard"))

    excel_bytes, filename = service.generate_report_excel(start_date, end_date)

    return send_file(
        io.BytesIO(excel_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )


@report_bp.route("/email", methods=["POST"])
@login_required
def send_email():
    service = current_app.report_service
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    to_email = request.form.get("to_email", "").strip()
    bcc_email = request.form.get("bcc_email", "").strip() or None
    subject = request.form.get("subject", "").strip()
    body_text = request.form.get("body_text", "").strip()
    sender_email = request.form.get("sender_email", "").strip() or None
    sender_password = request.form.get("sender_password", "").strip() or None

    if not to_email or not subject:
        flash("El destinatario y el asunto son campos obligatorios.", "danger")
        return redirect(url_for("reports.report_dashboard", start_date=start_date, end_date=end_date))

    try:
        msg = service.send_report_by_email(
            start_date=start_date,
            end_date=end_date,
            to_email=to_email,
            subject=subject,
            body_text=body_text,
            sender_email=sender_email,
            sender_password=sender_password,
            bcc_email=bcc_email
        )
        flash(msg, "success")
    except DomainException as e:
        flash(str(e), "danger")
    except Exception as e:
        flash(f"Error inesperado al enviar correo: {str(e)}", "danger")

    return redirect(url_for("reports.report_dashboard", start_date=start_date, end_date=end_date))
