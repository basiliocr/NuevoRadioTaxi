from flask import abort, flash, redirect, url_for
from flask_login import current_user
from functools import wraps

def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Debes iniciar sesión.", "warning")
                return redirect(url_for("auth.login"))
            if current_user.role.name != role_name:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
