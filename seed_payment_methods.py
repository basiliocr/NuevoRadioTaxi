from flask import Flask
from database import db
from models.payment_model import PaymentMethod

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///taxi_express.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    if not PaymentMethod.query.first():
        db.session.add_all([
            PaymentMethod(name="Efectivo"),
            PaymentMethod(name="QR")
        ])
        db.session.commit()
        print("✅ Métodos de pago cargados")
    else:
        print("ℹ️ Ya existen métodos de pago")
