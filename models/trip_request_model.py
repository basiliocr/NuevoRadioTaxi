from database import db
from datetime import datetime
class TripRequest(db.Model):
    __tablename__ = 'trip_requests'

    id = db.Column(db.Integer, primary_key=True)
    passenger_user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    pickup_address_text = db.Column(db.String(255))
    pickup_latitude = db.Column(db.Numeric(10, 8), nullable=True)
    pickup_longitude = db.Column(db.Numeric(11, 8), nullable=True)

    dropoff_address_text = db.Column(db.String(255))
    dropoff_latitude = db.Column(db.Numeric(10, 8), nullable=True)
    dropoff_longitude = db.Column(db.Numeric(11, 8), nullable=True)

    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow)
    tarifa_estimada = db.Column(db.Numeric(10, 2), nullable=True)
    vehicle_type = db.Column(db.String(20), nullable=False)  # ← para 'auto' o 'moto'

    estado = db.Column(db.Enum('buscando', 'aceptado', 'cancelado', 'finalizado', name='estado_viaje_enum'), default='buscando')

    trip = db.relationship("Trip", back_populates="trip_request", uselist=False)

    def __repr__(self):
         return f"<TripRequest #{self.id} - Estado: {self.estado}>"