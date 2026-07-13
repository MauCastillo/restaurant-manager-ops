from functools import wraps
from flask import session, redirect, url_for, flash, current_app


def login_required(f):
    """Decorator to require an active user session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor, inicia sesión para acceder a esta página.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor, inicia sesión para acceder a esta página.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("user_role") != "admin":
            flash("Acceso denegado: se requieren permisos de administrador.", "danger")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return decorated_function
