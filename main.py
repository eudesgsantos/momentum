from flask import Flask, request, render_template, Response
#from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import datetime
import pandas as pd
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import io
from random import randint

app = Flask(__name__)
#CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/eudes/angular/flask/app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class acumulado_ibovespa(db.Model):
    data = db.Column(db.Date(), primary_key=True, nullable=False)
    retorno = db.Column(db.Float(), nullable=False)

class acumulado_cdi(db.Model):
    data = db.Column(db.Date(), primary_key=True, nullable=False)
    retorno = db.Column(db.Float(), nullable=False)

class acumulado_momentum(db.Model):
    data = db.Column(db.Date(), primary_key=True, nullable=False)
    retorno = db.Column(db.Float(), nullable=False)


@app.route("/")
def func_acumulado():
    start_date = datetime.date(2014,6,1)
    end_date = datetime.date(2022,2,1)
    query_ibovespa = acumulado_ibovespa.query.filter(acumulado_ibovespa.data.between(start_date,end_date))
    query_cdi = acumulado_cdi.query.filter(acumulado_cdi.data.between(start_date,end_date))
    query_momentum = acumulado_momentum.query.filter(acumulado_momentum.data.between(start_date,end_date))


    df_ibovespa = pd.concat([pd.DataFrame([i.retorno], columns=["ibovespa"]) for i in query_ibovespa],ignore_index=True)
    df_cdi = pd.concat([pd.DataFrame([i.retorno], columns=["cdi"]) for i in query_cdi],ignore_index=True)
    df_momentum  = pd.concat([pd.DataFrame([i.retorno], columns=["momentum"]) for i in query_momentum],ignore_index=True)

    df = pd.concat([df_ibovespa, df_cdi,df_momentum], axis=1, join="inner")

    value_cdi, value_ibovespa, value_momentum = 1.0, 1.0, 1.0
    list_cdi, list_ibovespa, list_momentum = [], [], []

    for i in df["cdi"]:
        value_cdi = value_cdi * i
        list_cdi.append(value_cdi)
    
    for i in df["ibovespa"]:
        value_ibovespa = value_ibovespa * i
        list_ibovespa.append(value_ibovespa)

    for i in df["momentum"]:
        value_momentum = value_momentum * i
        list_momentum.append(value_momentum)

    df["cdi_calc"] = list_cdi
    df["ibovespa_calc"] = list_ibovespa
    df["momentum_calc"] = list_momentum

    return render_template("front.html",  tables=[df.to_html(classes="data")], titles=df.columns.values)

    #fig = create_figure(df)
    #output = io.BytesIO()
    #FigureCanvas(fig).print_png(output)
    #return Response(output.getvalue(), mimetype="image/png")
    

def create_figure(df):
    fig = Figure()
    show = fig.plot(df["cdi"],df["ibovespa"])
    return show

if __name__=="__main__":
    app.run(debug=True)