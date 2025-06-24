from flask import Blueprint, render_template
from flask_login import login_required, current_user
from utils.decorators import role_required
from views import driver_view

driver_bp = Blueprint("driver", __name__, url_prefix="/conductor")

@driver_bp.route("/dashboard")
@login_required
@role_required("conductor")
def dashboard():
    return driver_view.dashboard(current_user)
