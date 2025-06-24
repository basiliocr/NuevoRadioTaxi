from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from utils.decorators import role_required
from models.driver_profile_model import DriverProfile
from views import driver_profile_view
from forms.driver_forms import DriverProfileForm
from forms.edit_driver_forms import EditDriverProfileForm
from database import db
import os
from werkzeug.utils import secure_filename

driver_profile_bp = Blueprint("driver_profile", __name__, url_prefix="/conductor/perfil")

UPLOAD_FOLDER = "static/uploads/"

@driver_profile_bp.route("/", methods=["GET"])
@login_required
@role_required("conductor")
def ver_perfil():
    perfil = current_user.driver_profile
    return driver_profile_view.detalle(perfil)

@driver_profile_bp.route("/editar", methods=["GET", "POST"])
@login_required
@role_required("conductor")
def editar_perfil():
    perfil = current_user.driver_profile

    if perfil:
        form = EditDriverProfileForm(obj=perfil)

        if request.method == "GET":
            form.username.data = current_user.username
            form.nombre.data = current_user.nombre
            form.email.data = current_user.email
            form.telefono.data = current_user.telefono
    else:
        form = DriverProfileForm()

    if form.validate_on_submit():
        # Validar licencia duplicada solo si es un perfil nuevo
        if not perfil:
            existente = DriverProfile.query.filter_by(licencia=form.licencia.data).first()
            if existente:
                flash("Ya existe un perfil con esa licencia. Verifica los datos ingresados.", "warning")
                return redirect(url_for("driver_profile.editar_perfil"))

        # Actualizar usuario si es edición
        if isinstance(form, EditDriverProfileForm):
            current_user.username = form.username.data
            current_user.nombre = form.nombre.data
            current_user.email = form.email.data
            current_user.telefono = form.telefono.data

        # Guardar archivos
        foto_filename = None
        seguro_filename = None

        if form.foto_perfil.data and hasattr(form.foto_perfil.data, "filename"):
            foto_filename = secure_filename(form.foto_perfil.data.filename)
            form.foto_perfil.data.save(os.path.join(UPLOAD_FOLDER, foto_filename))

        if form.documento_seguro.data and hasattr(form.documento_seguro.data, "filename"):
            seguro_filename = secure_filename(form.documento_seguro.data.filename)
            form.documento_seguro.data.save(os.path.join(UPLOAD_FOLDER, seguro_filename))

        if not perfil:
            perfil = DriverProfile(
                user_id=current_user.id,
                licencia=form.licencia.data,
                fecha_expiracion_licencia=form.fecha_expiracion_licencia.data,
                ci=form.ci.data,
                foto_perfil=foto_filename,
                documento_seguro=seguro_filename,
                disponibilidad="desconectado"
            )
            db.session.add(perfil)
        else:
            perfil.licencia = form.licencia.data
            perfil.fecha_expiracion_licencia = form.fecha_expiracion_licencia.data
            perfil.ci = form.ci.data
            if foto_filename:
                perfil.foto_perfil = foto_filename
            if seguro_filename:
                perfil.documento_seguro = seguro_filename

        db.session.commit()
        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for("driver_profile.ver_perfil"))

    template = "driver/perfil_form_edit.html" if isinstance(form, EditDriverProfileForm) else "driver/perfil_form.html"
    return render_template(template, form=form, perfil=perfil)

@driver_profile_bp.route("/eliminar", methods=["POST"])
@login_required
@role_required("conductor")
def eliminar_perfil():
    perfil = current_user.driver_profile
    if perfil:
        perfil.delete()
        flash("Tu perfil de conductor fue eliminado.", "warning")
    else:
        flash("No tenés un perfil para eliminar.", "danger")
    return redirect(url_for("driver.dashboard"))
