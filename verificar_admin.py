from run import app
from models.user_model import User

with app.app_context():
    user = User.query.filter_by(username="admin").first()

    if user:
        print("🧑‍💼 Usuario encontrado: admin")
        print("🔒 Contraseña coincide:", user.verify_password("admin123"))
        print("🔑 Contraseña guardada (hash):", user.password_hash)
    else:
        print("❌ Usuario admin no encontrado en la base de datos.")
