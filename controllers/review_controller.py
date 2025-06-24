from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db
from models.review_model import Review
from models.trip_model import Trip
from forms.review_form import ReviewForm
from models.user_model import User
from utils.decorators import role_required

review_bp = Blueprint("review", __name__, url_prefix="/reseñas")

@review_bp.route("/crear/<int:trip_id>", methods=["GET", "POST"])
@login_required
def crear_review(trip_id):
    trip = Trip.query.get_or_404(trip_id)

    if trip.trip_request.estado != "finalizado" or trip.trip_request.passenger_user_id != current_user.id:
        flash("No puedes calificar este viaje.", "danger")
        return redirect(url_for("trip.historial_pasajero"))

    if trip.review:
        flash("Ya has dejado una reseña para este viaje.", "info")
        return redirect(url_for("trip.historial_pasajero"))

    form = ReviewForm()
    if form.validate_on_submit():
        reseña = Review(
            trip_id=trip.id,
            reviewer_user_id=current_user.id,
            reviewed_user_id=trip.driver_user_id,
            calificacion=form.calificacion.data,
            comentario=form.comentario.data
        )
        db.session.add(reseña)
        db.session.commit()
        flash("Gracias por tu opinión. Reseña enviada.", "success")
        return redirect(url_for("trip.historial_pasajero"))

    return render_template("reviews/crear_review.html", form=form, viaje=trip)

@review_bp.route("/conductor/<int:user_id>")
@login_required
def ver_reseñas_conductor(user_id):
    conductor = User.query.get_or_404(user_id)
    reseñas = Review.query.filter_by(reviewed_user_id=user_id).order_by(Review.fecha_review.desc()).all()
    total = len(reseñas)
    promedio = sum(r.calificacion for r in reseñas) / total if total else None

    return render_template("reviews/ver_reseñas.html", conductor=conductor, reseñas=reseñas, promedio=promedio, total=total)

@review_bp.route("/crear/pasajeroconductor/<int:trip_id>", methods=["GET", "POST"])
@login_required
@role_required("conductor")
def crear_review_pasajeroconductor(trip_id):
    trip = Trip.query.get_or_404(trip_id)

    if trip.trip_request.estado != "finalizado" or trip.trip_request.passenger_user_id != current_user.id:
        flash("No puedes calificar este viaje.", "danger")
        return redirect(url_for("trip.historial_pasajero_conductor"))

    if trip.review:
        flash("Ya has dejado una reseña para este viaje.", "info")
        return redirect(url_for("trip.historial_pasajero_conductor"))

    form = ReviewForm()
    if form.validate_on_submit():
        reseña = Review(
            trip_id=trip.id,
            reviewer_user_id=current_user.id,
            reviewed_user_id=trip.driver_user_id,
            calificacion=form.calificacion.data,
            comentario=form.comentario.data
        )
        db.session.add(reseña)
        db.session.commit()
        flash("Gracias por tu reseña. Ha sido enviada.", "success")
        return redirect(url_for("trip.historial_pasajero_conductor"))

    return render_template("reviews/crear_review_pasajeroconductor.html", form=form, viaje=trip)
