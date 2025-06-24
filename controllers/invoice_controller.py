from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from models.trip_model import Trip
from models.invoice_model import Invoice
from datetime import datetime
from database import db

invoice_bp = Blueprint("invoice", __name__, url_prefix="/facturas")

@invoice_bp.route("/generar/<int:trip_id>", methods=["POST"])
@login_required
def generar_factura(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    es_conductor_pasajero = trip.trip_request.passenger_user_id == current_user.id and current_user.role.name == "conductor"
    historial = "trip.historial_pasajero_conductor" if es_conductor_pasajero else "trip.historial_pasajero"

    if trip.invoice:
        flash("La factura de este viaje ya fue generada.", "info")
        return redirect(url_for("historial"))

    trip_request = trip.trip_request
    if not trip_request.tarifa_estimada:
        flash("Este viaje aún no tiene una tarifa registrada.", "warning")
        return redirect(url_for(historial))


    nuevo_invoice = Invoice(
        trip_id=trip.id,
        invoice_number=f"{datetime.utcnow().year}{str(trip.id).zfill(6)}",
        company_name="Taxi Express S.R.L.",
        detalles_json={
            "origen": trip.trip_request.pickup_address_text,
            "destino": trip.trip_request.dropoff_address_text,
            "vehículo": trip.trip_request.vehicle_type,
            "fecha": trip.datetime_ini.strftime('%d/%m/%Y %H:%M'),
            "usuario": trip.trip_request.pasajero.nombre
        },
        monto_total=trip.trip_request.tarifa_estimada
    )

    db.session.add(nuevo_invoice)
    db.session.commit()
    flash("Factura generada exitosamente.", "success")
    return redirect(url_for("trip.historial_pasajero"))

@invoice_bp.route("/ver/<int:trip_id>")
@login_required
def ver_factura(trip_id):
    trip = Trip.query.get_or_404(trip_id)

    es_conductor_pasajero = trip.trip_request.passenger_user_id == current_user.id and current_user.role.name == "conductor"
    historial = "trip.historial_pasajero_conductor" if es_conductor_pasajero else "trip.historial_pasajero"

    if not trip.invoice:
        flash("Este viaje no tiene factura generada.", "warning")
        return redirect(url_for(historial))

    return render_template("invoices/ver_factura.html", factura=trip.invoice)

