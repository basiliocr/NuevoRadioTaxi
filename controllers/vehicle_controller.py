from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from utils.decorators import role_required
from forms.vehicle_forms import VehicleForm
from models.vehicle_model import Vehicle
from database import db
from views import vehicle_view

vehicle_bp = Blueprint("vehicle", __name__, url_prefix="/vehiculo")


@vehicle_bp.route("/", methods=["GET"])
@login_required
@role_required("conductor")
def ver_vehiculo():
    vehiculo = current_user.vehiculo
    return vehicle_view.detalle(vehiculo)


@vehicle_bp.route("/registrar", methods=["GET", "POST"])
@login_required
@role_required("conductor")
def registrar():
    vehiculo = current_user.vehiculo
    form = VehicleForm(obj=vehiculo)

    if form.validate_on_submit():
        if not vehiculo:
            vehiculo = Vehicle(
                driver_user_id=current_user.id,
                matricula=form.matricula.data,
                marca=form.marca.data,
                modelo=form.modelo.data,
                anio=form.anio.data,
                color=form.color.data,
                vehicle_type=form.vehicle_type.data
            )
            db.session.add(vehiculo)
        else:
            vehiculo.matricula = form.matricula.data
            vehiculo.marca = form.marca.data
            vehiculo.modelo = form.modelo.data
            vehiculo.anio = form.anio.data
            vehiculo.color = form.color.data
            vehiculo.vehicle_type = form.vehicle_type.data

        db.session.commit()
        flash("Vehículo registrado correctamente.", "success")
        return redirect(url_for("vehicle.ver_vehiculo"))

    return vehicle_view.formulario(form, vehiculo)

@vehicle_bp.route("/editar", methods=["GET", "POST"])
@login_required
@role_required("conductor")
def editar():
    vehiculo = current_user.vehiculo
    if not vehiculo:
        flash("Primero debes registrar un vehículo.", "warning")
        return redirect(url_for("vehicle.registrar"))

    form = VehicleForm(obj=vehiculo)

    if form.validate_on_submit():
        vehiculo.matricula = form.matricula.data
        vehiculo.marca = form.marca.data
        vehiculo.modelo = form.modelo.data
        vehiculo.anio = form.anio.data
        vehiculo.color = form.color.data
        vehiculo.vehicle_type = form.vehicle_type.data

        db.session.commit()
        flash("Vehículo actualizado correctamente.", "success")
        return redirect(url_for("vehicle.ver_vehiculo"))

    return render_template("driver/vehiculoedit.html", form=form, vehiculo=vehiculo)


@vehicle_bp.route("/eliminar", methods=["POST"])
@login_required
@role_required("conductor")
def eliminar():
    vehiculo = current_user.vehiculo
    if vehiculo:
        vehiculo.delete()
        flash("Tu vehículo fue eliminado correctamente.", "warning")
    else:
        flash("No tenés un vehículo registrado para eliminar.", "danger")

    return redirect(url_for("driver.dashboard"))
