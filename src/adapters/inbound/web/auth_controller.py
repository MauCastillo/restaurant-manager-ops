from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from src.domain.exceptions import DomainException
from src.adapters.inbound.web.auth_decorators import login_required, admin_required

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def get_auth_service():
    from flask import current_app
    return current_app.auth_service


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        auth_service = get_auth_service()
        try:
            user = auth_service.authenticate(username, password)
            session["user_id"] = user.id
            session["username"] = user.username
            session["user_role"] = user.role
            flash(f"¡Bienvenido de nuevo, {user.username}!", "success")
            return redirect(url_for("dashboard.index"))
        except DomainException as e:
            flash(str(e.message), "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión exitosamente.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/users", methods=["GET"])
@login_required
def users_list():
    auth_service = get_auth_service()
    users = auth_service.list_users()
    return render_template("auth/users_list.html", users=users)


@auth_bp.route("/register", methods=["GET", "POST"])
@login_required
def register_user():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        role = request.form.get("role", "operator")

        auth_service = get_auth_service()
        try:
            auth_service.register_user(username, email, password, role)
            flash(f"Usuario '{username}' registrado exitosamente en el sistema de seguridad.", "success")
            return redirect(url_for("auth.users_list"))
        except DomainException as e:
            flash(str(e.message), "danger")

    return render_template("auth/register_user.html")


@auth_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@admin_required
def delete_user(user_id):
    if session.get("user_id") == user_id:
        flash("No puedes eliminar tu propia cuenta mientras estás conectado.", "warning")
        return redirect(url_for("auth.users_list"))

    auth_service = get_auth_service()
    try:
        auth_service.delete_user(user_id)
        flash("Usuario eliminado correctamente.", "success")
    except DomainException as e:
        flash(str(e.message), "danger")

    return redirect(url_for("auth.users_list"))
