from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from database import db
from models.trip_request_model import TripRequest
from models.trip_model import Trip
from models.vehicle_model import Vehicle
from utils.decorators import role_required
from datetime import datetime
from models.location_log_model import LocationLog 

trip_bp = Blueprint("trip", __name__, url_prefix="/viajes")

# Mostrar solicitudes disponibles para el conductor
@trip_bp.route("/solicitudes")
@login_required
@role_required("conductor")
def ver_solicitudes_disponibles():
    vehiculo = Vehicle.query.filter_by(driver_user_id=current_user.id).first()
    if not vehiculo:
        flash("No tienes un vehículo registrado.", "warning")
        return redirect(url_for("driver_profile.ver_perfil"))

    solicitudes = TripRequest.query.filter(
        TripRequest.estado == "buscando",
        TripRequest.vehicle_type == vehiculo.vehicle_type,
        TripRequest.passenger_user_id != current_user.id
    ).order_by(TripRequest.fecha_solicitud.desc()).all()

    return render_template("trips/solicitudes_disponibles.html", solicitudes=solicitudes)

# Aceptar solicitud de viaje
@trip_bp.route("/aceptar/<int:solicitud_id>", methods=["POST"])
@login_required
@role_required("conductor")
def aceptar_solicitud(solicitud_id):
    solicitud = TripRequest.query.get_or_404(solicitud_id)
    
    if solicitud.passenger_user_id == current_user.id:
        flash("No puedes aceptar tu propia solicitud.", "danger")
        return redirect(url_for("trip.ver_solicitudes_disponibles"))

    vehiculo = Vehicle.query.filter_by(driver_user_id=current_user.id).first()
    if not vehiculo or vehiculo.vehicle_type != solicitud.vehicle_type:
        flash("Tu vehículo no es compatible con esta solicitud.", "warning")
        return redirect(url_for("trip.ver_solicitudes_disponibles"))

    solicitud.estado = "aceptado"
    nuevo_viaje = Trip(
        trip_request_id=solicitud.id,
        driver_user_id=current_user.id,
        vehicle_id=vehiculo.id,
        datetime_ini=datetime.utcnow()
    )
    db.session.add(nuevo_viaje)
    db.session.commit()

    # Registramos punto de inicio (recogida)
    inicio_log = LocationLog(
        trip_id=nuevo_viaje.id,
        user_id=current_user.id,
        latitude=solicitud.pickup_latitude,
        longitude=solicitud.pickup_longitude
    )
    db.session.add(inicio_log)
    db.session.commit()


    flash("Solicitud aceptada. Viaje asignado correctamente.", "success")
    return redirect(url_for("trip.dashboard_conductor"))

# Dashboard del conductor — muestra el viaje en curso si existe
@trip_bp.route("/dashboard/conductor")
@login_required
@role_required("conductor")
def dashboard_conductor():
    viaje_activo = Trip.query.join(TripRequest).filter(
        Trip.driver_user_id == current_user.id,
        TripRequest.estado == "aceptado"
    ).order_by(TripRequest.fecha_solicitud.desc()).first()

    return render_template("driver/dashboard.html", viaje_activo=viaje_activo)

# Finalizar viaje
@trip_bp.route("/finalizar/<int:trip_id>", methods=["POST"])
@login_required
@role_required("conductor")
def finalizar_viaje(trip_id):
    viaje = Trip.query.get_or_404(trip_id)


    if viaje.driver_user_id != current_user.id:
        flash("Solo el conductor puede finalizar este viaje.", "danger")
        return redirect(url_for("trip.dashboard_conductor"))
    
    
    # Registramos punto de destino (llegada)
    fin_log = LocationLog(
        trip_id=viaje.id,
        user_id=current_user.id,
        latitude=viaje.trip_request.dropoff_latitude,
        longitude=viaje.trip_request.dropoff_longitude
    )
    db.session.add(fin_log)

    viaje.datetime_fin = datetime.utcnow()
    viaje.distancia_km = 10.0  # Simulado por ahora
    viaje.duracion_min = 15
    viaje.trip_request.estado = "finalizado"
    db.session.commit()

    flash("Viaje finalizado correctamente.", "success")
    return redirect(url_for("trip.historial_conductor"))

# Historial como pasajero
@trip_bp.route("/historial/pasajero")
@login_required
def historial_pasajero():
    viajes = Trip.query.join(TripRequest).filter(
        TripRequest.passenger_user_id == current_user.id,
        TripRequest.estado.in_(["finalizado", "cancelado"])
    ).order_by(TripRequest.fecha_solicitud.desc()).all()

    return render_template("trips/historial_pasajero.html", viajes=viajes)

# Historial como conductor
@trip_bp.route("/historial/conductor")
@login_required
@role_required("conductor")
def historial_conductor():
    viajes = Trip.query.join(TripRequest).filter(
        Trip.driver_user_id == current_user.id,
        TripRequest.estado.in_(["finalizado", "cancelado"])
    ).order_by(TripRequest.fecha_solicitud.desc()).all()

    return render_template("trips/historial_conductor.html", viajes=viajes)

# Eliminar viaje
@trip_bp.route("/eliminar/<int:trip_id>", methods=["POST"])
@login_required
def eliminar_viaje(trip_id):
    viaje = Trip.query.get_or_404(trip_id)

    es_dueño = (
        viaje.driver_user_id == current_user.id or
        viaje.trip_request.passenger_user_id == current_user.id
    )

    if not es_dueño:
        flash("No tienes permiso para eliminar este viaje.", "danger")
        return redirect(url_for("trip.historial_pasajero"))

    if viaje.trip_request.estado not in ["finalizado", "cancelado"]:
        flash("Solo puedes eliminar viajes finalizados o cancelados.", "warning")
        return redirect(url_for("trip.historial_pasajero"))

    db.session.delete(viaje)
    db.session.commit()
    flash("Viaje eliminado correctamente.", "info")
    return redirect(url_for("trip.historial_pasajero"))

# Historial cuando el conductor viaja como pasajero
@trip_bp.route("/historial/conductor-como-pasajero")
@login_required
@role_required("conductor")
def historial_pasajero_conductor():
    viajes = Trip.query.join(TripRequest).filter(
        TripRequest.passenger_user_id == current_user.id,
        TripRequest.estado == "finalizado"
    ).order_by(TripRequest.fecha_solicitud.desc()).all()

    return render_template("trips/historial_pasajeroconductor.html", viajes=viajes)


# Cancelar solicitud antes de ser aceptada (estado: buscando)
@trip_bp.route("/solicitudes/cancelar/<int:solicitud_id>", methods=["POST"])
@login_required
def cancelar_solicitud(solicitud_id):
    solicitud = TripRequest.query.get_or_404(solicitud_id)

    if solicitud.passenger_user_id != current_user.id:
        flash("No tienes permiso para cancelar esta solicitud.", "danger")
        return redirect(url_for("user.dashboard"))

    if solicitud.estado != "buscando":
        flash("Solo puedes cancelar solicitudes en estado 'buscando'.", "warning")
        return redirect(url_for("user.dashboard"))

    solicitud.estado = "cancelado"
    db.session.commit()

    flash("Solicitud cancelada exitosamente.", "info")
    return redirect(url_for("user.dashboard"))
