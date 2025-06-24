from database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models.role_model import Role
from models.trip_request_model import TripRequest


class User(db.Model, UserMixin):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    telefono = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.relationship('Role', backref="users")

    trip_requests = db.relationship(
        'TripRequest',
        backref='pasajero',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    payments = db.relationship(
        'Payment',
        backref='usuario',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    reseñas_recibidas = db.relationship(
        "Review",
        foreign_keys="Review.reviewed_user_id",
        backref="conductor",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    def __init__(self, role_id, nombre, username, email, telefono, password):
        self.role_id = role_id
        self.nombre = nombre
        self.username = username
        self.email = email
        self.telefono = telefono
        self.password_hash = self.hash_password(password)

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_all():
        return User.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def eliminar_con_dependencias(self):
        """
        Elimina al usuario y todas sus dependencias de forma ordenada:
        - Viajes como pasajero (y todo lo relacionado)
        - Pagos independientes
        - Reseñas recibidas como conductor
        - Perfil de conductor
        """

        def eliminar_lista(coleccion):
            try:
                for item in coleccion.all():
                    db.session.delete(item)
            except AttributeError:
                for item in coleccion:
                    db.session.delete(item)

        for viaje in self.trip_requests:
            trip_final = getattr(viaje, "trip", None)

            # Eliminar factura asociada
            if trip_final and getattr(trip_final, "invoice", None):
                db.session.delete(trip_final.invoice)

            # Eliminar logs de ubicación
            if trip_final and getattr(trip_final, "ubicaciones", None):
                eliminar_lista(trip_final.ubicaciones)

            # Eliminar reseña asociada
            if trip_final and getattr(trip_final, "review", None):
                db.session.delete(trip_final.review)

            # Eliminar el viaje final
            if trip_final:
                db.session.delete(trip_final)

            # Eliminar pagos del viaje
            eliminar_lista(getattr(viaje, "payments", []))

            db.session.delete(viaje)

        # Eliminar pagos directos del usuario
        eliminar_lista(self.payments)

        # Eliminar reseñas recibidas como conductor
        eliminar_lista(self.reseñas_recibidas)

        # Eliminar perfil de conductor si existe
        if getattr(self, "driver_profile", None):
            db.session.delete(self.driver_profile)

        # Finalmente, eliminar el usuario
        db.session.delete(self)

    @property
    def tiene_perfil_completo(self):
        perfil = self.driver_profile
        if not perfil:
            return False
        if not perfil.licencia or not perfil.fecha_expiracion_licencia:
            return False
        if perfil.disponibilidad == "desconectado":
            return False
        if not getattr(self, "vehiculo", None):
            return False
        return True






