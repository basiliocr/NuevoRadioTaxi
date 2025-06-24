from database import db

class VehiclePricing(db.Model):
    __tablename__ = 'vehicle_pricing'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_type = db.Column(db.String(20), nullable=False, unique=True)
    tarifa_base = db.Column(db.Numeric(10, 2), nullable=False)
    tarifa_por_km = db.Column(db.Numeric(10, 2), nullable=False)

    def __repr__(self):
        return f"<{self.vehicle_type}: Bs {self.tarifa_base} base + {self.tarifa_por_km}/km>"
