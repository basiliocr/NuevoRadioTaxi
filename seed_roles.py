from flask import Flask
from database import db
from models.role_model import Role

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///taxi_express.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    roles_existentes = Role.query.with_entities(Role.name).all()
    nombres_existentes = {r.name for r in roles_existentes}

    nuevos_roles = []
    for nombre in ["admin", "pasajero", "conductor"]:
        if nombre not in nombres_existentes:
            nuevos_roles.append(Role(name=nombre))

    if nuevos_roles:
        db.session.add_all(nuevos_roles)
        db.session.commit()
        print("✅ Roles cargados con éxito:", [r.name for r in nuevos_roles])
    else:
        print("ℹ️ Ya existen todos los roles requeridos.")
