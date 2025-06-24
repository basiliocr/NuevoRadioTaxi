from database import db
from sqlalchemy import Enum

class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Método {self.name}>"

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    trip_request_id = db.Column(db.Integer, db.ForeignKey('trip_requests.id', ondelete='CASCADE'), nullable=False)
    payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_methods.id'), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(
        Enum('completado', 'fallido', name='estado_pago_enum'),
        default='completado',
        nullable=False
    )

    payment_method = db.relationship("PaymentMethod", backref="payments")