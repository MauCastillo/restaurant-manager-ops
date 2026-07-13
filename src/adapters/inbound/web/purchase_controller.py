from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from src.domain.exceptions import DomainException
from src.adapters.inbound.web.auth_decorators import login_required

purchase_bp = Blueprint("purchases", __name__, url_prefix="/purchases")


def get_purchase_service():
    return current_app.purchase_service


def get_client_service():
    return current_app.client_service


@purchase_bp.route("/", methods=["GET"])
@login_required
def list_purchases():
    purchase_service = get_purchase_service()
    client_service = get_client_service()

    purchases = purchase_service.list_all_purchases()
    clients = client_service.list_clients()
    client_map = {c.id: c for c in clients}

    client_id_filter = request.args.get("client_id", type=int)
    fecha_inicio = request.args.get("fecha_inicio", "").strip()
    fecha_fin = request.args.get("fecha_fin", "").strip()
    selected_client = None

    if client_id_filter:
        selected_client = client_map.get(client_id_filter)
        purchases = [p for p in purchases if p.client_id == client_id_filter]

    if fecha_inicio:
        purchases = [p for p in purchases if p.fecha_compra >= fecha_inicio]
    if fecha_fin:
        purchases = [p for p in purchases if p.fecha_compra <= fecha_fin]

    total_filtered_monto = sum(p.monto for p in purchases)

    return render_template(
        "purchases/list.html",
        purchases=purchases,
        clients=clients,
        client_map=client_map,
        selected_client=selected_client,
        client_id_filter=client_id_filter,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        total_filtered_monto=total_filtered_monto
    )


@purchase_bp.route("/create", methods=["POST"])
@login_required
def create_purchase():
    client_id_raw = request.form.get("client_id")
    concepto = request.form.get("concepto", "").strip()
    monto_raw = request.form.get("monto", "0.0")
    fecha_compra = request.form.get("fecha_compra", datetime.utcnow().strftime("%Y-%m-%d"))
    notas = request.form.get("notas", "").strip()

    redirect_to_client = request.form.get("redirect_client_id")

    try:
        client_id = int(client_id_raw)
        monto = float(monto_raw)
        purchase_service = get_purchase_service()
        purchase_service.register_purchase(
            client_id=client_id,
            concepto=concepto,
            monto=monto,
            fecha_compra=fecha_compra,
            notas=notas
        )
        flash("Registro de compra guardado exitosamente.", "success")
    except (ValueError, TypeError):
        flash("Datos de compra inválidos. Por favor verifica el monto y el cliente seleccionado.", "danger")
    except DomainException as e:
        flash(str(e.message), "danger")

    if redirect_to_client:
        return redirect(url_for("clients.detail_client", client_id=int(redirect_to_client)))
    return redirect(url_for("purchases.list_purchases"))


@purchase_bp.route("/<int:purchase_id>/delete", methods=["POST"])
@login_required
def delete_purchase(purchase_id):
    redirect_to_client = request.form.get("redirect_client_id")
    purchase_service = get_purchase_service()

    try:
        purchase_service.delete_purchase(purchase_id)
        flash("Compra eliminada correctamente.", "success")
    except DomainException as e:
        flash(str(e.message), "danger")

    if redirect_to_client:
        return redirect(url_for("clients.detail_client", client_id=int(redirect_to_client)))
    return redirect(url_for("purchases.list_purchases"))


@purchase_bp.route("/api/check_duplicate", methods=["GET"])
@login_required
def check_duplicate():
    """API endpoint to detect if a purchase on the same date with exact same amount already exists."""
    client_id_raw = request.args.get("client_id")
    fecha_compra = request.args.get("fecha_compra", "").strip()
    monto_raw = request.args.get("monto", "0")

    try:
        client_id = int(client_id_raw)
        monto = float(monto_raw)
        purchase_service = get_purchase_service()
        is_dup = purchase_service.check_duplicate_purchase(client_id, fecha_compra, monto)
        return jsonify({"is_duplicate": is_dup})
    except Exception as e:
        return jsonify({"is_duplicate": False, "error": str(e)})


@purchase_bp.route("/ocr/analyze", methods=["POST"])
@login_required
def analyze_ocr_image():
    """Receive uploaded handwritten image, analyze via Gemini AI OCR, and render preview screen."""
    import base64
    image_file = request.files.get("image")
    if not image_file or image_file.filename == "":
        flash("Por favor selecciona o toma una fotografía antes de analizar.", "danger")
        return redirect(url_for("purchases.list_purchases"))

    try:
        image_bytes = image_file.read()
        mime_type = image_file.content_type or "image/jpeg"
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        image_data_uri = f"data:{mime_type};base64,{image_b64}"

        ocr_service = current_app.ocr_service
        extracted_rows = ocr_service.analyze_sales_image(image_bytes, mime_type)

        client_service = current_app.client_service
        all_clients = client_service.list_clients()

        return render_template(
            "purchases/ocr_preview.html",
            extracted_rows=extracted_rows,
            image_data_uri=image_data_uri,
            all_clients=all_clients,
            image_filename=image_file.filename
        )
    except Exception as e:
        flash(f"Error al analizar la imagen con Inteligencia Artificial: {str(e)}", "danger")
        return redirect(url_for("purchases.list_purchases"))


@purchase_bp.route("/ocr/confirm", methods=["POST"])
@login_required
def confirm_ocr_purchases():
    """Save user-verified purchases extracted from OCR preview form."""
    client_ids = request.form.getlist("client_id")
    conceptos = request.form.getlist("concepto")
    montos = request.form.getlist("monto")
    fechas = request.form.getlist("fecha_compra")

    saved_count = 0
    errors_count = 0
    purchase_service = get_purchase_service()

    for cid_raw, conc, m_raw, f_raw in zip(client_ids, conceptos, montos, fechas):
        try:
            if not cid_raw or not str(cid_raw).strip():
                continue
            cid = int(cid_raw)
            monto_val = float(m_raw or 0.0)
            if monto_val <= 0:
                continue

            purchase_service.register_purchase(
                client_id=cid,
                concepto=(conc or "Alimentación").strip(),
                monto=monto_val,
                fecha_compra=(f_raw or datetime.now().strftime("%Y-%m-%d")).strip(),
                notas="Registrado vía IA Gemini OCR (Escaneo Manuscrito)"
            )
            saved_count += 1
        except Exception:
            errors_count += 1

    if saved_count > 0:
        flash(f"✅ Se guardaron exitosamente {saved_count} consumos/ventas verificados desde la fotografía manuscrita.", "success")
    elif errors_count > 0:
        flash("No se guardaron registros debido a errores en la selección de cliente o montos.", "warning")
    else:
        flash("No se seleccionó ningún registro válido para guardar.", "info")

    return redirect(url_for("purchases.list_purchases"))
