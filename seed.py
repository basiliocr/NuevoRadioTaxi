from flask import Flask
from database import db
from models.vehicle_pricing_model import VehiclePricing

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///taxi_express.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()  # Asegura que exista la tabla
    if not VehiclePricing.query.first():  # Evita duplicar si ya existen precios
        precios = [
            VehiclePricing(vehicle_type="auto", tarifa_base=5.00, tarifa_por_km=2.50),
            VehiclePricing(vehicle_type="moto", tarifa_base=3.00, tarifa_por_km=1.50)
        ]
        db.session.add_all(precios)
        db.session.commit()
        print("✅ Tarifas precargadas exitosamente")
    else:
        print("ℹ️ Ya existen precios, no se duplicaron")
