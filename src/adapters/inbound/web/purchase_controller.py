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
    selected_client = None
    total_filtered_monto = 0.0

    if client_id_filter:
        selected_client = client_map.get(client_id_filter)
        purchases = [p for p in purchases if p.client_id == client_id_filter]

    total_filtered_monto = sum(p.monto for p in purchases)

    return render_template(
        "purchases/list.html",
        purchases=purchases,
        clients=clients,
        client_map=client_map,
        selected_client=selected_client,
        client_id_filter=client_id_filter,
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
