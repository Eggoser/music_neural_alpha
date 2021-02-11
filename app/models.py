from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(100))
