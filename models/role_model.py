from database import db

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    @staticmethod
    def get_by_name(name):
        return Role.query.filter_by(name=name).first()
