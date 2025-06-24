from database import db

class Vehicle(db.Model):
    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    driver_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    matricula = db.Column(db.String(20), unique=True, nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(30), nullable=False)

    vehicle_type = db.Column(
        db.Enum("auto", "moto", name="tipo_vehiculo"),
        nullable=False
    )

    conductor = db.relationship(
        "User",
        backref=db.backref("vehiculo", uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    )

    def __init__(self, driver_user_id, matricula, marca, modelo, anio, color, vehicle_type):
        self.driver_user_id = driver_user_id
        self.matricula = matricula
        self.marca = marca
        self.modelo = modelo
        self.anio = anio
        self.color = color
        self.vehicle_type = vehicle_type

    @staticmethod
    def get_by_id(vehicle_id):
        return Vehicle.query.get(vehicle_id)
    
    @staticmethod
    def get_all():
        return Vehicle.query.all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()




