from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Saldo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wartosc = db.Column(db.Float, default=0.0)


class Produkt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(100), unique=True, nullable=False)
    ilosc = db.Column(db.Integer, default=0)


class Historia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opis = db.Column(db.String(255), nullable=False)

