from database import db
from datetime import datetime

class LocationLog(db.Model):
    __tablename__ = "location_logs"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    latitude = db.Column(db.Numeric(10, 8), nullable=False)
    longitude = db.Column(db.Numeric(11, 8), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    trip = db.relationship("Trip", backref="ubicaciones")
    user = db.relationship("User", backref="ubicaciones")
