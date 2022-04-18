from classes import db, acumulado_ibovespa, acumulado_cdi, acumulado_momentum
from flask import Flask, request, Response
from flask_migrate import Migrate
#from flask_cors import CORS
import datetime
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io


app = Flask(__name__)
#CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////home/eudes/angular/flask/app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route("/retorno")
def func_retorno():
    #inputs
    start_date = datetime.date(2014,6,1)
    end_date = datetime.date(2022,2,1)

    #queries
    query_ibovespa = acumulado_ibovespa.query.filter(acumulado_ibovespa.data.between(start_date,end_date))
    query_cdi = acumulado_cdi.query.filter(acumulado_cdi.data.between(start_date,end_date))
    query_momentum = acumulado_momentum.query.filter(acumulado_momentum.data.between(start_date,end_date))

    #count size
    count = query_ibovespa.count()

    list_date, list_cdi, list_ibovespa, list_momentum = [], [], [], []
    value_cdi, value_ibovespa, value_momentum = 1.0, 1.0, 1.0

    #fill list for each metric and multiply values
    for i in range(count):
        value_cdi = value_cdi * query_cdi[i].retorno
        value_ibovespa = value_ibovespa * query_ibovespa[i].retorno
        value_momentum = value_momentum * query_momentum[i].retorno
        list_date.append(query_ibovespa[i].data)
        list_cdi.append(value_cdi)
        list_ibovespa.append(value_ibovespa)
        list_momentum.append(value_momentum)
    
    #create retorno dataframe
    df = pd.DataFrame(index=list_date)

    #percentage convert
    df["cdi"] = [element * 100 for element in list_cdi]
    df["ibovespa"] = [element * 100 for element in list_ibovespa]
    df["momentum"] = [element * 100 for element in list_momentum]

    #plot retorno
    fig = Figure()
    ax = fig.add_subplot(1, 1, 1)
    plot = df.plot(ax=ax)
    plot.set_xlabel("Date")
    plot.set_ylabel("Percent")
    plot_retorno_image = io.BytesIO()
    FigureCanvas(fig).print_png(plot_retorno_image)

    return Response(plot_retorno_image.getvalue(), mimetype='image/png')

@app.route("/drawdown")
def func_drawdown():
    #inputs
    start_date = datetime.date(2014,6,1)
    end_date = datetime.date(2022,2,1)

    #queries
    query_ibovespa = acumulado_ibovespa.query.filter(acumulado_ibovespa.data.between(start_date,end_date))
    query_cdi = acumulado_cdi.query.filter(acumulado_cdi.data.between(start_date,end_date))
    query_momentum = acumulado_momentum.query.filter(acumulado_momentum.data.between(start_date,end_date))

    #count size
    count = query_ibovespa.count()

    list_date, list_cdi, list_ibovespa, list_momentum = [], [], [], []
    value_cdi, value_ibovespa, value_momentum = 1.0, 1.0, 1.0

    #fill list for each metric and multiply values
    for i in range(count):
        value_cdi = value_cdi * query_cdi[i].retorno
        value_ibovespa = value_ibovespa * query_ibovespa[i].retorno
        value_momentum = value_momentum * query_momentum[i].retorno
        list_date.append(query_ibovespa[i].data)
        list_cdi.append(value_cdi)
        list_ibovespa.append(value_ibovespa)
        list_momentum.append(value_momentum)
    
    #create retorno dataframe
    df = pd.DataFrame(index=list_date)

    #percentage convert
    df["cdi"] = [element * 100 for element in list_cdi]
    df["ibovespa"] = [element * 100 for element in list_ibovespa]
    df["momentum"] = [element * 100 for element in list_momentum]
    
    #create drawdown dataframe
    df_drawdown = pd.DataFrame(index=list_date)

    #calculate each drawdown
    previous_peaks_momentum = df["momentum"].cummax()
    drawdown_momentum =(df["momentum"]-previous_peaks_momentum)/previous_peaks_momentum

    previous_peaks_cdi = df["cdi"].cummax()
    drawdown_cdi =(df["cdi"]-previous_peaks_cdi)/previous_peaks_cdi

    previous_peaks_ibovespa = df["ibovespa"].cummax()
    drawdown_ibovespa =(df["ibovespa"]-previous_peaks_ibovespa)/previous_peaks_ibovespa

    #concat results in one dataframe
    df_drawdown = pd.concat([drawdown_momentum, drawdown_cdi,drawdown_ibovespa], axis=1, join="inner")

    #percentage convert
    df_drawdown["cdi"] = 100 * df_drawdown["cdi"] 
    df_drawdown["ibovespa"] = 100 * df_drawdown["ibovespa"] 
    df_drawdown["momentum"] = 100 * df_drawdown["momentum"] 

    #plot drawdown
    fig = Figure()
    ax = fig.add_subplot(1, 1, 1)
    plot = df_drawdown.plot(ax=ax)
    plot.set_xlabel("Date")
    plot.set_ylabel("Percent")
    plot_drawdown_image = io.BytesIO()
    FigureCanvas(fig).print_png(plot_drawdown_image)

    return Response(plot_drawdown_image.getvalue(), mimetype='image/png')


if __name__=="__main__":
    app.run(debug=True)