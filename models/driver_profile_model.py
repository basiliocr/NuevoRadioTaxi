from database import db

class DriverProfile(db.Model):
    __tablename__ = "driver_profiles"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    licencia = db.Column(db.String(50), unique=True, nullable=False)
    fecha_expiracion_licencia = db.Column(db.Date, nullable=False)
    ci = db.Column(db.String(20), nullable=False)

    foto_perfil = db.Column(db.String(255))
    documento_seguro = db.Column(db.String(255))

    disponibilidad = db.Column(
        db.Enum("conectado", "en_viaje", "desconectado", name="estado_disponibilidad"),
        default="desconectado",
        nullable=False
    )

    current_latitude = db.Column(db.Numeric(10, 8))
    current_longitude = db.Column(db.Numeric(11, 8))

    usuario = db.relationship(
        "User",
        backref=db.backref("driver_profile", uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    )

    def __init__(self, user_id, licencia, fecha_expiracion_licencia, ci,
                 foto_perfil=None, documento_seguro=None,
                 current_latitude=None, current_longitude=None,
                 disponibilidad="desconectado"):
        self.user_id = user_id
        self.licencia = licencia
        self.fecha_expiracion_licencia = fecha_expiracion_licencia
        self.ci = ci
        self.foto_perfil = foto_perfil
        self.documento_seguro = documento_seguro
        self.current_latitude = current_latitude
        self.current_longitude = current_longitude
        self.disponibilidad = disponibilidad

    @staticmethod
    def get_by_id(user_id):
        return DriverProfile.query.get(user_id)
    
    @staticmethod
    def get_all():
        return DriverProfile.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
