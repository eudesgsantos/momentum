from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class acumulado_ibovespa(db.Model):
    data = db.Column(db.Date(), primary_key=True, nullable=False)
    retorno = db.Column(db.Float(), nullable=False)

class acumulado_cdi(db.Model):
    data = db.Column(db.Date(), primary_key=True, nullable=False)
    retorno = db.Column(db.Float(), nullable=False)

class acumulado_momentum(db.Model):
    data = db.Column(db.Date(), primary_key=True, nullable=False)
    retorno = db.Column(db.Float(), nullable=False)
