from flask import Blueprint, render_template, current_app
from src.adapters.inbound.web.auth_decorators import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    client_service = current_app.client_service
    purchase_service = current_app.purchase_service

    clients = client_service.list_clients()
    purchases = purchase_service.list_all_purchases()

    total_clients = len(clients)
    total_base_descuento = sum(c.valor_a_descontar for c in clients)
    total_compras_monto = sum(p.monto for p in purchases)
    total_saldo_neto = total_base_descuento + total_compras_monto

    client_map = {c.id: c for c in clients}
    recent_purchases = purchases[:8]

    # Process summary by Proceso de Desempeño
    por_proceso = {}
    for c in clients:
        proc = c.proceso_desempeno or "Sin Asignar"
        por_proceso.setdefault(proc, {"clientes": 0, "monto": 0.0})
        por_proceso[proc]["clientes"] += 1
        por_proceso[proc]["monto"] += c.valor_a_descontar

    return render_template(
        "dashboard/index.html",
        total_clients=total_clients,
        total_base_descuento=total_base_descuento,
        total_compras_monto=total_compras_monto,
        total_saldo_neto=total_saldo_neto,
        recent_purchases=recent_purchases,
        client_map=client_map,
        por_proceso=por_proceso,
        clients=clients[:10]
    )
