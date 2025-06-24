from flask import Flask, render_template, flash
from flask_login import LoginManager, login_required
from database import db
from models.role_model import Role
from controllers.auth_controller import auth_bp, login_manager
from controllers.user_controller import user_bp
from models.trip_request_model import TripRequest
from models.vehicle_pricing_model import VehiclePricing
from models.payment_model import Payment, PaymentMethod
from models.user_model import User
from models.role_model import Role
from controllers.driver_controller import driver_bp
from controllers.driver_profile_controller import driver_profile_bp
from controllers.vehicle_controller import vehicle_bp
from controllers.userdriver_controller import userdriver_bp
from controllers.trip_controller import trip_bp
from controllers.review_controller import review_bp
from controllers.invoice_controller import invoice_bp
from controllers.admin_controller import admin_bp


from utils.decorators import role_required

from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

@event.listens_for(Engine, "connect")
def habilitar_foreign_keys(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///taxi_express.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "clave_secreta"

db.init_app(app)
login_manager.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(driver_bp)
app.register_blueprint(driver_profile_bp)
app.register_blueprint(vehicle_bp)
app.register_blueprint(userdriver_bp)
app.register_blueprint(trip_bp)
app.register_blueprint(review_bp)
app.register_blueprint(invoice_bp)
app.register_blueprint(admin_bp)


@app.route('/')
def home():
    return render_template('baseindex.html')


@app.route("/baseuser")
@role_required("pasajero")  # ✅ Esto sí funcionará dentro de contexto HTTP
def dashboard():
    return render_template("baseuser.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)


