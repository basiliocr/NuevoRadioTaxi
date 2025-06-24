from flask import Flask
from werkzeug.security import generate_password_hash
from database import db
from models.role_model import Role
from models.user_model import User
from models import User, Role

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///taxi_express.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    # Verificar rol
    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin")
        db.session.add(admin_role)
        db.session.commit()
        print("✅ Rol admin creado.")

    # Crear admin si no existe
    admin_existente = User.query.filter_by(username="admin").first()
    if not admin_existente:
        admin = User(
        nombre="Administrador",
        username="admin",
        email="admin@taxiexpress.com",
        telefono="000000000",
        password="admin123",  # <-- texto plano aquí
        role_id=admin_role.id
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuario admin creado.")
    else:
        print("ℹ️ El usuario admin ya existe.")
