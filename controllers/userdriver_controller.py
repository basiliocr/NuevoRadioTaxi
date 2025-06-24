from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from utils.decorators import role_required
from database import db
from models.trip_request_model import TripRequest
from models.vehicle_pricing_model import VehiclePricing
from models.payment_model import Payment, PaymentMethod
from forms.trip_forms import TripRequestForm
from models.trip_model import Trip

userdriver_bp = Blueprint("userdriver", __name__, url_prefix="/conductorpasajero")

@userdriver_bp.route("/dashboard")
@login_required
@role_required("conductor")
def dashboard():
    viaje_activo = Trip.query.join(TripRequest).filter(
        Trip.driver_user_id == current_user.id,
        TripRequest.estado == "aceptado"
    ).order_by(TripRequest.fecha_solicitud.desc()).first()

    return render_template("driver/dashboard.html", viaje_activo=viaje_activo)

@userdriver_bp.route("/solicitar", methods=["GET", "POST"])
@login_required
@role_required("conductor")
def solicitar_viaje():
    form = TripRequestForm()

    metodos = PaymentMethod.query.all()
    form.payment_method.choices = [(m.id, m.name) for m in metodos]

    vehiculos = VehiclePricing.query.all()
    tarifas = {
        v.vehicle_type: {
            "base": float(v.tarifa_base),
            "por_km": float(v.tarifa_por_km)
        } for v in vehiculos
    }

    if form.validate_on_submit():
        if not form.tarifa_estimada.data or not form.tarifa_estimada.data.strip():
            flash("La tarifa no fue calculada. Asegúrate de haber seleccionado origen y destino.", "danger")
            return redirect(url_for("userdriver.solicitar_viaje"))

        nuevo_viaje = TripRequest(
            passenger_user_id=current_user.id,
            pickup_address_text=form.pickup_address.data,
            pickup_latitude=form.pickup_lat.data,
            pickup_longitude=form.pickup_lon.data,
            dropoff_address_text=form.dropoff_address.data,
            dropoff_latitude=form.dropoff_lat.data,
            dropoff_longitude=form.dropoff_lon.data,
            vehicle_type=form.vehicle_type.data,
            tarifa_estimada=form.tarifa_estimada.data,
        )
        db.session.add(nuevo_viaje)
        db.session.commit()

        nuevo_pago = Payment(
            user_id=current_user.id,
            trip_request_id=nuevo_viaje.id,
            payment_method_id=form.payment_method.data,
            monto=form.tarifa_estimada.data,
            estado="completado"
        )
        db.session.add(nuevo_pago)
        db.session.commit()

        flash("¡Viaje solicitado exitosamente!", "success")
        return redirect(url_for("userdriver.ticket_viaje", viaje_id=nuevo_viaje.id))

    return render_template("driver/solicitar_conductor.html", form=form, tarifas=tarifas)

@userdriver_bp.route("/ticket/<int:viaje_id>")
@login_required
@role_required("conductor")
def ticket_viaje(viaje_id):
    viaje = TripRequest.query.get_or_404(viaje_id)

    if viaje.passenger_user_id != current_user.id:
        flash("No tienes permiso para ver este ticket.", "danger")
        return redirect(url_for("userdriver.dashboard"))

    pago = Payment.query.filter_by(trip_request_id=viaje.id).first()

    return render_template("driver/ticket_conductor.html", viaje=viaje, pago=pago)
