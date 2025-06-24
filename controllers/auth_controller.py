from flask import request, redirect, url_for, render_template, flash, Blueprint
from flask_login import LoginManager, login_user, logout_user, login_required
from models.user_model import User
from database import db
from forms.auth_forms import LoginForm, RegisterForm
from models.role_model import Role

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Debes iniciar sesión para acceder a esta página."
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.verify_password(form.password.data):
                login_user(user)
                flash("Inicio de sesión exitoso.", "success")

                # Redirección según rol
                if user.role.name == "admin":
                    return redirect(url_for("admin.dashboard_admin"))
                elif user.role.name == "conductor":
                    return redirect(url_for("driver.dashboard"))
                elif user.role.name == "pasajero":
                    return redirect(url_for("user.dashboard"))
                else:
                    return redirect(url_for("home"))

            flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("auth/login.html", form=form)

# NUEVO: Pantalla de selección de rol antes de registrar
@auth_bp.route("/register")
def register_select():
    return render_template("auth/choose_role.html")

# NUEVO: Mostrar el formulario con el rol precargado
@auth_bp.route("/register/<role>", methods=["GET", "POST"])
def register(role):
    form = RegisterForm()

    # Buscar el rol por nombre en la base de datos
    role_obj = Role.query.filter_by(name=role).first()
    if not role_obj:
        flash("Rol inválido", "danger")
        return redirect(url_for("auth.register_select"))

    if request.method == "POST" and form.validate_on_submit():
        errores = []

        if User.query.filter_by(username=form.username.data).first():
            errores.append("El nombre de usuario ya está en uso.")

        if User.query.filter_by(email=form.email.data).first():
            errores.append("El correo electrónico ya está en uso.")

        if User.query.filter_by(telefono=form.telefono.data).first():
            errores.append("El número de teléfono ya está registrado.")

        if errores:
            for error in errores:
                flash(error, "danger")
            return render_template("auth/register.html", form=form, role=role)

        user = User(
            role_id=role_obj.id,  # ✅ Asigna directamente el ID del rol desde la tabla
            nombre=form.nombre.data,
            username=form.username.data,
            email=form.email.data,
            telefono=form.telefono.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()

        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form, role=role, role_obj=role_obj)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("home"))

@auth_bp.route("/check_username")
def check_username():
    username = request.args.get("valor")
    user_exists = User.query.filter_by(username=username).first() is not None
    return {"available": not user_exists}

@auth_bp.route("/check_email")
def check_email():
    email = request.args.get("valor")
    user_exists = User.query.filter_by(email=email).first() is not None
    return {"available": not user_exists}

@auth_bp.route("/check_telefono")
def check_telefono():
    telefono = request.args.get("valor")
    user_exists = User.query.filter_by(telefono=telefono).first() is not None
    return {"available": not user_exists}





