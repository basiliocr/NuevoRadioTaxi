from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from utils.decorators import role_required
from database import db
from models.trip_model import Trip
from models.trip_request_model import TripRequest
from models.user_model import User  # Asegurate de tener acceso a nombres
from models.role_model import Role
from models.invoice_model import Invoice
from models.review_model import Review
from sqlalchemy import func, desc
from models.vehicle_pricing_model import VehiclePricing
from sqlalchemy import func, extract
from datetime import datetime

from sqlalchemy.orm import joinedload
from sqlalchemy import or_


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/solicitudes")
@login_required
@role_required("admin")
def ver_solicitudes_admin():
    estado = request.args.get("estado")
    nombre = request.args.get("nombre", "").strip()

    query = TripRequest.query.options(joinedload(TripRequest.pasajero))

    if estado:
        query = query.filter_by(estado=estado)

    if nombre:
        query = query.join(TripRequest.pasajero).filter(
            User.nombre.ilike(f"%{nombre}%")
        )

    solicitudes = query.order_by(TripRequest.fecha_solicitud.desc()).all()

    return render_template(
        "admin/solicitudes_admin.html",
        solicitudes=solicitudes,
        estado_seleccionado=estado,
        nombre_buscado=nombre
    )

@admin_bp.route("/viajes")
@login_required
@role_required("admin")
def ver_viajes_admin():
    from models.user_model import User
    from models.payment_model import PaymentMethod
    from models.trip_request_model import TripRequest

    pasajero = request.args.get("pasajero", "").strip()
    conductor = request.args.get("conductor", "").strip()
    pago = request.args.get("pago", "").strip()
    vehiculo = request.args.get("vehiculo", "").strip()

    query = Trip.query.options(
        db.joinedload(Trip.trip_request).joinedload(TripRequest.pasajero),
        db.joinedload(Trip.driver)
    )

    if pasajero:
        query = query.join(Trip.trip_request).join(TripRequest.pasajero).filter(
            User.nombre.ilike(f"%{pasajero}%")
    )


    if conductor:
        query = query.join(Trip.driver).filter(
            User.nombre.ilike(f"%{conductor}%")
        )

    if pago:
        query = query.join(Trip.trip_request).join(TripRequest.payment_method).filter(
            PaymentMethod.name == pago
        )

    if vehiculo:
        query = query.join(Trip.trip_request).filter(
            TripRequest.vehicle_type == vehiculo
        )

    viajes = query.order_by(Trip.datetime_ini.desc()).all()

    metodos_pago = [m.name for m in PaymentMethod.query.order_by(PaymentMethod.name).all()]
    tipos_vehiculo = list({t.vehicle_type for t in TripRequest.query.distinct(TripRequest.vehicle_type).all() if t.vehicle_type})

    return render_template(
        "admin/viajes_admin.html",
        viajes=viajes,
        pasajero=pasajero,
        conductor=conductor,
        pago=pago,
        vehiculo=vehiculo,
        metodos_pago=metodos_pago,
        tipos_vehiculo=tipos_vehiculo
    )

@admin_bp.route("/viaje/eliminar/<int:trip_id>", methods=["POST"])
@login_required
@role_required("admin")
def eliminar_viaje(trip_id):
    from models.location_log_model import LocationLog
    from models.review_model import Review

    trip = Trip.query.get_or_404(trip_id)

    # 0. Eliminar reviews relacionados
    Review.query.filter_by(trip_id=trip.id).delete()

    # 1. Eliminar location logs directamente
    LocationLog.query.filter_by(trip_id=trip.id).delete()

    # 2. Eliminar factura si existe
    if trip.invoice:
        db.session.delete(trip.invoice)

    # 3. Eliminar solicitud asociada
    if trip.trip_request:
        db.session.delete(trip.trip_request)

    # 4. Eliminar el viaje
    db.session.delete(trip)
    db.session.commit()

    flash("Viaje y todos sus datos relacionados fueron eliminados.", "success")
    return redirect(url_for("admin.ver_viajes_admin"))



@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard_admin():
    return render_template("admin/dashboard.html")

@admin_bp.route("/estadisticas/solicitudes")
@login_required
@role_required("admin")
def estadisticas_solicitudes():
    estados = ["buscando", "aceptado", "finalizado", "rechazado"]
    data = {estado: TripRequest.query.filter_by(estado=estado).count() for estado in estados}
    return render_template("estadistica/solicitudes.html", data=data)

@admin_bp.route("/usuarios")
@login_required
@role_required("admin")
def ver_usuarios_admin():
    from models.role_model import Role  # asegurate de importar

    rol = request.args.get("rol", "").strip()
    query = User.query

    if rol:
        query = query.join(Role).filter(Role.name == rol)

    usuarios = query.order_by(User.nombre).all()
    roles_disponibles = ['admin', 'conductor', 'pasajero']

    return render_template(
        "admin/usuarios_admin.html",
        usuarios=usuarios,
        rol=rol,
        roles_disponibles=roles_disponibles
    )


@admin_bp.route("/usuario/<int:id>")
@login_required
@role_required("admin")
def ver_usuario(id):
    user = User.query.get_or_404(id)
    return render_template("admin/usuario_detalle.html", user=user)

@admin_bp.route("/usuario/editar/<int:id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def editar_usuario(id):
    user = User.query.get_or_404(id)

    if request.method == "POST":
        # Validar que el correo no esté en uso por otro usuario
        email_existente = User.query.filter(User.email == request.form['email'], User.id != user.id).first()
        if email_existente:
            flash("Ese correo ya está registrado por otro usuario.", "danger")
            return redirect(url_for("admin.editar_usuario", id=user.id))

        # Validar que el username no esté repetido
        username_existente = User.query.filter(User.username == request.form['username'], User.id != user.id).first()
        if username_existente:
            flash("Ese nombre de usuario ya está en uso.", "danger")
            return redirect(url_for("admin.editar_usuario", id=user.id))

        # Guardar los cambios
        user.nombre = request.form['nombre']
        user.username = request.form['username']
        user.email = request.form['email']
        user.telefono = request.form['telefono']

        db.session.commit()
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for("admin.ver_usuarios_admin"))

    return render_template("admin/usuario_editar.html", user=user)


@admin_bp.route("/usuario/toggle/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def toggle_estado_usuario(id):
    user = User.query.get_or_404(id)
    user.activo = not user.activo
    db.session.commit()
    flash(f"El usuario fue {'activado' if user.activo else 'bloqueado'} correctamente.", "info")
    return redirect(url_for("admin.ver_usuarios_admin"))

@admin_bp.route("/usuario/eliminar/<int:id>", methods=["POST"])
@login_required
@role_required("admin")
def eliminar_usuario(id):
    user = User.query.get_or_404(id)
    try:
        user.eliminar_con_dependencias()
        db.session.commit()
        flash("Usuario eliminado correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"No se pudo eliminar el usuario: {str(e)}", "danger")
    return redirect(url_for("admin.ver_usuarios_admin"))

@admin_bp.route("/usuarios/crear", methods=["GET", "POST"])
@login_required
@role_required("admin")
def crear_usuario():
    roles = Role.query.all()

    if request.method == "POST":
        nombre = request.form["nombre"]
        username = request.form["username"]
        email = request.form["email"]
        telefono = request.form["telefono"]
        rol_id = request.form["rol_id"]
        password = request.form["password"]  # O podés generar una por defecto

        nuevo = User(
            role_id=rol_id,
            nombre=nombre,
            username=username,
            email=email,
            telefono=telefono,
            password=password
        )
        # Verificar duplicados
        if User.query.filter_by(email=email).first():
            flash("Ya existe un usuario con este correo electrónico.", "danger")
            return redirect(url_for("admin.crear_usuario"))

        if User.query.filter_by(username=username).first():
            flash("El nombre de usuario ya está en uso.", "danger")
            return redirect(url_for("admin.crear_usuario"))

        if User.query.filter_by(telefono=telefono).first():
            flash("Ese número de teléfono ya está registrado.", "danger")
            return redirect(url_for("admin.crear_usuario"))

        db.session.add(nuevo)
        db.session.commit()
        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("admin.ver_usuarios_admin"))

    return render_template("admin/crear_usuario.html", roles=roles)

@admin_bp.route("/conductores/<int:user_id>")
@login_required
@role_required("admin")
def ver_conductor(user_id):
    user = User.query.get_or_404(user_id)
    perfil = user.driver_profile
    vehiculo = None

    if perfil and hasattr(user, "vehiculo"):
        vehiculo = user.vehiculo

    # Reseñas recientes
    reseñas = Review.query.filter_by(reviewed_user_id=user.id).order_by(Review.fecha_review.desc()).all()

    # Promedio de calificación
    promedio = db.session.query(func.avg(Review.calificacion))\
        .filter_by(reviewed_user_id=user.id).scalar() or 0
    promedio = round(promedio, 2)

    # Conteo por estrellas
    conteo_estrellas = dict(
        db.session.query(Review.calificacion, func.count(Review.id))
        .filter_by(reviewed_user_id=user.id)
        .group_by(Review.calificacion)
        .all()
    )
    # Asegurar todos los niveles de estrella están presentes (1 a 5)
    for i in range(1, 6):
        conteo_estrellas.setdefault(i, 0)

    return render_template(
        "admin/ficha_conductor.html",
        user=user,
        perfil=perfil,
        vehiculo=vehiculo,
        promedio=promedio,
        conteo_estrellas=conteo_estrellas,
        reseñas=reseñas
    )



@admin_bp.route("/facturas")
@login_required
@role_required("admin")
def ver_facturas_admin():
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")
    monto_min = request.args.get("monto_min")

    facturas_query = Invoice.query

    if fecha_inicio:
        facturas_query = facturas_query.filter(Invoice.fecha_emision >= fecha_inicio)
    if fecha_fin:
        facturas_query = facturas_query.filter(Invoice.fecha_emision <= fecha_fin)
    if monto_min:
        facturas_query = facturas_query.filter(Invoice.monto_total >= float(monto_min))

    facturas = facturas_query.order_by(Invoice.fecha_emision.desc()).all()
    return render_template("admin/ver_facturas.html", facturas=facturas)

@admin_bp.route("/tarifas", methods=["GET", "POST"])
@login_required
@role_required("admin")
def configurar_tarifas():
    tarifas = {p.vehicle_type: p for p in VehiclePricing.query.all()}

    if request.method == "POST":
        for tipo in tarifas:
            base = request.form.get(f"{tipo}_base")
            por_km = request.form.get(f"{tipo}_por_km")
            if base and por_km:
                tarifas[tipo].tarifa_base = float(base)
                tarifas[tipo].tarifa_por_km = float(por_km)
        db.session.commit()
        flash("Tarifas actualizadas correctamente", "success")
        return redirect(url_for("admin.configurar_tarifas"))

    return render_template("admin/tarifas_config.html", tarifas=tarifas)



@admin_bp.route("/estadisticas", methods=["GET"])
@login_required
@role_required("admin")
def estadisticas_financieras():
    from collections import defaultdict

    # Parámetros por URL
    año = int(request.args.get("anio", datetime.now().year))
    mes = int(request.args.get("mes", datetime.now().month))

    PORCENTAJE_EMPRESA = 0.40
    PORCENTAJE_CONDUCTOR = 0.60

    # Viajes del mes
    viajes = Trip.query.filter(
        extract("year", Trip.datetime_ini) == año,
        extract("month", Trip.datetime_ini) == mes
    ).all()

    # Total bruto del mes (convertido a float)
    total_monto = sum([
        float(v.trip_request.tarifa_estimada)
        for v in viajes
        if v.trip_request and v.trip_request.tarifa_estimada
    ])
    total_viajes = len(viajes)

    ganancia_empresa = round(total_monto * PORCENTAJE_EMPRESA, 2)
    ganancia_conductores = round(total_monto * PORCENTAJE_CONDUCTOR, 2)

    # Desglose por conductor
    desglose = defaultdict(lambda: {"nombre": "", "viajes": 0, "total": 0.0})

    for v in viajes:
        if v.driver and v.trip_request and v.trip_request.tarifa_estimada:
            monto = float(v.trip_request.tarifa_estimada)
            cid = v.driver.id
            desglose[cid]["nombre"] = v.driver.nombre
            desglose[cid]["viajes"] += 1
            desglose[cid]["total"] += monto

    # Cálculo de reparto por conductor
    for d in desglose.values():
        d["empresa"] = round(d["total"] * PORCENTAJE_EMPRESA, 2)
        d["conductor"] = round(d["total"] * PORCENTAJE_CONDUCTOR, 2)

    return render_template("admin/estadisticas_financieras.html",
        mes=mes,
        anio=año,
        total_viajes=total_viajes,
        total_monto=round(total_monto, 2),
        ganancia_empresa=ganancia_empresa,
        ganancia_conductores=ganancia_conductores,
        desglose=desglose.values()
    )


from flask import render_template, make_response, request
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime
from sqlalchemy import extract
from collections import defaultdict


@admin_bp.route('/estadisticas/pdf')
@login_required
@role_required("admin")
def exportar_pdf():
    año = int(request.args.get("anio", datetime.now().year))
    mes = int(request.args.get("mes", datetime.now().month))

    PORCENTAJE_EMPRESA = 0.40
    PORCENTAJE_CONDUCTOR = 0.60

    viajes = Trip.query.filter(
        extract("year", Trip.datetime_ini) == año,
        extract("month", Trip.datetime_ini) == mes
    ).all()

    desglose = defaultdict(lambda: {
        "nombre": "",
        "viajes": 0,
        "total": 0.0,
        "empresa": 0.0,
        "conductor": 0.0
    })

    total_monto = 0.0
    for v in viajes:
        if v.driver and v.trip_request and v.trip_request.tarifa_estimada:
            monto = float(v.trip_request.tarifa_estimada)
            cid = v.driver.id
            desglose[cid]["nombre"] = v.driver.nombre
            desglose[cid]["viajes"] += 1
            desglose[cid]["total"] += monto
            total_monto += monto

    for d in desglose.values():
        d["empresa"] = round(d["total"] * PORCENTAJE_EMPRESA, 2)
        d["conductor"] = round(d["total"] * PORCENTAJE_CONDUCTOR, 2)

    rendered = render_template("admin/estadisticas_pdf.html",
        mes=mes,
        anio=año,
        total_viajes=len(viajes),
        total_monto=round(total_monto, 2),
        ganancia_empresa=round(total_monto * PORCENTAJE_EMPRESA, 2),
        ganancia_conductores=round(total_monto * PORCENTAJE_CONDUCTOR, 2),
        desglose=desglose.values()
    )

    pdf_stream = BytesIO()
    pisa.CreatePDF(src=rendered, dest=pdf_stream)
    pdf_stream.seek(0)

    response = make_response(pdf_stream.read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=estadisticas_{mes}_{año}.pdf"
    return response