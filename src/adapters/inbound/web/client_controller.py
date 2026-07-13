import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from src.domain.exceptions import DomainException
from src.adapters.inbound.web.auth_decorators import login_required

client_bp = Blueprint("clients", __name__, url_prefix="/clients")


def get_client_service():
    return current_app.client_service


def get_purchase_service():
    return current_app.purchase_service


@client_bp.route("/", methods=["GET"])
@login_required
def list_clients():
    search_query = request.args.get("q", "").strip()
    client_service = get_client_service()
    clients = client_service.list_clients(search_query=search_query)
    return render_template("clients/list.html", clients=clients, search_query=search_query)


@client_bp.route("/create", methods=["POST"])
@login_required
def create_client():
    nombre = request.form.get("nombre", "").strip()
    cedula = request.form.get("cedula", "").strip()
    proceso_desempeno = request.form.get("proceso_desempeno", "Pool de Ambulancia").strip()
    valor_raw = request.form.get("valor_a_descontar", "0.0")

    try:
        valor = float(valor_raw or 0.0)
        client_service = get_client_service()
        client = client_service.register_client(
            nombre=nombre,
            cedula=cedula,
            proceso_desempeno=proceso_desempeno,
            valor_a_descontar=valor
        )
        flash(f"Cliente '{client.nombre}' registrado exitosamente.", "success")
    except ValueError:
        flash("El valor a descontar debe ser numérico.", "danger")
    except DomainException as e:
        flash(str(e.message), "danger")

    return redirect(url_for("clients.list_clients"))


@client_bp.route("/<int:client_id>", methods=["GET"])
@login_required
def detail_client(client_id):
    client_service = get_client_service()
    purchase_service = get_purchase_service()

    client = client_service.get_client(client_id)
    if not client:
        flash("Cliente no encontrado.", "danger")
        return redirect(url_for("clients.list_clients"))

    purchases = purchase_service.get_purchases_by_client(client_id)
    summary = purchase_service.get_client_financial_summary(client_id)

    fecha_inicio = request.args.get("fecha_inicio", "").strip()
    fecha_fin = request.args.get("fecha_fin", "").strip()

    if fecha_inicio:
        purchases = [p for p in purchases if p.fecha_compra >= fecha_inicio]
    if fecha_fin:
        purchases = [p for p in purchases if p.fecha_compra <= fecha_fin]

    filtered_total = sum(p.monto for p in purchases)

    return render_template(
        "clients/detail.html",
        client=client,
        purchases=purchases,
        summary=summary,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        filtered_total=filtered_total
    )


@client_bp.route("/<int:client_id>/update", methods=["POST"])
@login_required
def update_client(client_id):
    nombre = request.form.get("nombre", "").strip()
    cedula = request.form.get("cedula", "").strip()
    proceso_desempeno = request.form.get("proceso_desempeno", "Pool de Ambulancia").strip()
    valor_raw = request.form.get("valor_a_descontar", "0.0")

    try:
        valor = float(valor_raw or 0.0)
        client_service = get_client_service()
        client = client_service.update_client(
            client_id=client_id,
            nombre=nombre,
            cedula=cedula,
            proceso_desempeno=proceso_desempeno,
            valor_a_descontar=valor
        )
        flash(f"Datos de '{client.nombre}' actualizados correctamente.", "success")
    except ValueError:
        flash("El valor a descontar debe ser numérico.", "danger")
    except DomainException as e:
        flash(str(e.message), "danger")

    return redirect(url_for("clients.detail_client", client_id=client_id))


@client_bp.route("/<int:client_id>/delete", methods=["POST"])
@login_required
def delete_client(client_id):
    client_service = get_client_service()
    try:
        client_service.delete_client(client_id)
        flash("Cliente eliminado del sistema.", "success")
    except DomainException as e:
        flash(str(e.message), "danger")

    return redirect(url_for("clients.list_clients"))


@client_bp.route("/import_consulta", methods=["POST"])
@login_required
def import_consulta_html():
    client_service = get_client_service()
    temp_file_path = None
    import os
    import tempfile

    try:
        uploaded_file = request.files.get("json_file")
        if not uploaded_file or uploaded_file.filename == "":
            flash("Por favor selecciona un archivo .json para importar los clientes.", "warning")
            return redirect(url_for("clients.list_clients"))

        fd, temp_file_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        uploaded_file.save(temp_file_path)

        imported, skipped = client_service.import_from_json_file(temp_file_path)
        flash(f"Carga de clientes (.json) desde '{uploaded_file.filename}' completada: {imported} nuevos clientes registrados ({skipped} actualizados sin modificar montos base).", "success")
    except Exception as e:
        flash(f"Error al procesar el archivo JSON de clientes: {str(e)}", "danger")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass

    return redirect(url_for("clients.list_clients"))


@client_bp.route("/api/search", methods=["GET"])
@login_required
def api_search_clients():
    """JSON API endpoint for autocomplete client searcher."""
    q = request.args.get("q", "").strip()
    client_service = get_client_service()
    clients = client_service.list_clients(search_query=q)

    results = []
    for c in clients[:25]:
        results.append({
            "id": c.id,
            "nombre": c.nombre,
            "cedula": c.cedula,
            "proceso_desempeno": c.proceso_desempeno,
            "display": f"{c.nombre} — Cédula: {c.cedula}"
        })

    return jsonify(results)
