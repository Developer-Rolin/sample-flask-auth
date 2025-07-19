from database import db
from flask_login import UserMixin

# classe UserMixin ja tem varios métodos prontos, esta ativo, esta anonimo...


class User(db.Model, UserMixin):
    # id(int),username(text),password(text), role(text)
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False, default="user")
