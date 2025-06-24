from database import db
from datetime import datetime

class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey("trips.id"), nullable=False, unique=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    company_name = db.Column(db.String(100))
    fecha_emision = db.Column(db.DateTime, default=datetime.utcnow)
    detalles_json = db.Column(db.JSON)
    monto_total = db.Column(db.Numeric(10, 2), nullable=False)

    trip = db.relationship("Trip", backref=db.backref("invoice", uselist=False))

