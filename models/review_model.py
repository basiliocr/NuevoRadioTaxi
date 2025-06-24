from database import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False, unique=True)
    reviewer_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reviewed_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    calificacion = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.Text)
    fecha_review = db.Column(db.DateTime, default=datetime.utcnow)

    trip = db.relationship("Trip", backref="review")
    reviewer = db.relationship("User", foreign_keys=[reviewer_user_id])
    reviewed = db.relationship("User", foreign_keys=[reviewed_user_id])
