from flask import request, redirect, url_for, flash, Blueprint, render_template
from flask_login import login_required, current_user
from models.user_model import User
from views import user_view
from utils.decorators import role_required  # Si estás usando ese decorador personalizado
from forms.trip_forms import TripRequestForm
from models.trip_request_model import TripRequest
from models.payment_model import Payment
from models.payment_model import PaymentMethod
from database import db


user_bp = Blueprint('user', __name__, url_prefix="/users")

@user_bp.route("/")
@login_required
def index():
    users = User.get_all()
    return redirect(url_for("admin.ver_usuarios_admin"))

@user_bp.route("/edit/<int:id>", methods=['GET', 'POST'])
@login_required
def edit(id):
    user = User.get_by_id(id)

    if not user or user.id != current_user.id:
        flash("No tienes permiso para editar este perfil.", "danger")
        return redirect(url_for('user.index'))

    if request.method == "POST":
        # Verificar que el nuevo email no esté en uso por otro usuario
        email_existente = User.query.filter(User.email == request.form['email'], User.id != user.id).first()
        if email_existente:
            flash("Ese correo ya está en uso por otro usuario.", "danger")
            return redirect(url_for("user.edit", id=user.id))

        # Verificar username único
        usuario_existente = User.query.filter(User.username == request.form['username'], User.id != user.id).first()
        if usuario_existente:
            flash("Ese nombre de usuario ya está registrado.", "danger")
            return redirect(url_for("user.edit", id=user.id))

        # Asignar nuevos valores
        user.nombre = request.form['nombre']
        user.username = request.form['username']
        user.email = request.form['email']
        user.telefono = request.form['telefono']

        db.session.commit()
        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for('user.perfil'))

    return user_view.edit(user)

@user_bp.route("/delete/<int:id>", methods=['POST'])
@login_required
def delete(id):
    user = User.get_by_id(id)
    if user:
        from models.trip_request_model import TripRequest
        from models.payment_model import Payment

        # Elimina pagos relacionados a los viajes del usuario
        viajes = TripRequest.query.filter_by(passenger_user_id=user.id).all()
        for viaje in viajes:
            Payment.query.filter_by(trip_request_id=viaje.id).delete()

        # Elimina los viajes
        TripRequest.query.filter_by(passenger_user_id=user.id).delete()

        # Ahora sí elimina el usuario usando su método
        user.delete()

        flash("Cuenta eliminada exitosamente.", "success")

    return redirect(url_for('home'))

@user_bp.route("/dashboard")
@login_required
@role_required("pasajero")
def dashboard():
    viaje_activo = TripRequest.query.filter_by(
        passenger_user_id=current_user.id,
        estado="buscando"
    ).order_by(TripRequest.id.desc()).first()

    return render_template("users/dashboard.html", viaje_activo=viaje_activo)

@user_bp.route("/solicitar", methods=["GET", "POST"])
@login_required
@role_required("pasajero")
def solicitar_viaje():
    from models.trip_request_model import TripRequest
    from models.vehicle_pricing_model import VehiclePricing  # ← asegurate de que esté aquí arriba
    from models.payment_model import Payment, PaymentMethod

    form = TripRequestForm()

    metodos = PaymentMethod.query.all()
    form.payment_method.choices = [(m.id, m.name) for m in metodos]

    vehiculos = VehiclePricing.query.all()
    tarifas = {v.vehicle_type: {"base": float(v.tarifa_base), "por_km": float(v.tarifa_por_km)} for v in vehiculos}

    if form.validate_on_submit():
        from models.trip_request_model import TripRequest
        from models.vehicle_pricing_model import VehiclePricing

        vehicle = VehiclePricing.query.filter_by(vehicle_type=form.vehicle_type.data).first()
        if not vehicle:
            flash("Tarifa no disponible para este vehículo.", "danger")
            return redirect(url_for("user.solicitar_viaje"))
        
        if not form.tarifa_estimada.data or not form.tarifa_estimada.data.strip():
            flash("La tarifa no fue calculada. Asegúrate de haber seleccionado origen y destino.", "danger")
            return redirect(url_for("user.solicitar_viaje"))


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
        return redirect(url_for("user.ticket_viaje", viaje_id=nuevo_viaje.id))

    return render_template("users/solicitar_viaje.html", form=form, tarifas=tarifas)


@user_bp.route("/ticket/<int:viaje_id>")
@login_required
@role_required("pasajero")
def ticket_viaje(viaje_id):
    viaje = TripRequest.query.get_or_404(viaje_id)

    if viaje.passenger_user_id != current_user.id:
        flash("No tienes permiso para ver este ticket.", "danger")
        return redirect(url_for("user.dashboard"))

    pago = Payment.query.filter_by(trip_request_id=viaje.id).first()

    return render_template("users/ticket.html", viaje=viaje, pago=pago)

@user_bp.route("/perfil")
@login_required
@role_required("pasajero")
def perfil():
    return user_view.perfil(current_user)

