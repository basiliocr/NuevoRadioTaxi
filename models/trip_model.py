from database import db
from sqlalchemy.orm import relationship
from datetime import datetime

class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    trip_request_id = db.Column(db.Integer, db.ForeignKey('trip_requests.id'), unique=True, nullable=False)
    driver_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)

    datetime_ini = db.Column(db.DateTime, default=None)
    datetime_fin = db.Column(db.DateTime, default=None)
    distancia_km = db.Column(db.Numeric(10, 2))
    duracion_min = db.Column(db.Integer)

    trip_request = relationship("TripRequest", back_populates="trip")
    driver = relationship("User", backref="viajes_como_conductor")
    vehicle = relationship("Vehicle", backref="viajes_usados")

    def iniciar(self):
        self.datetime_ini = datetime.utcnow()

    def finalizar(self, distancia_km, duracion_min):
        self.datetime_fin = datetime.utcnow()
        self.distancia_km = distancia_km
        self.duracion_min = duracion_min
