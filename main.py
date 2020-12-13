from flask import Flask, render_template
from datetime import datetime, timedelta
from os import path, listdir, remove
import pandas as pd
import requests
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Response
import io
import random


def get_items():
    hoy = datetime.now()
    primer_dia = hoy.replace(day=1)
    items = ['Region']
    while primer_dia.day < hoy.day:
        items.append(primer_dia.date().strftime("%Y-%m-%d"))
        primer_dia = primer_dia + timedelta(days=1)
    items.append(hoy.date().strftime("%Y-%m-%d"))
    return items


def read_file(file):
    data = pd.DataFrame(pd.read_csv(file, delimiter=','))
    data_mask = data['Country_EN'] == 'Spain'
    filtered_data = data[data_mask]
    filtered_data.drop(columns=["Country_EN", "Country_IT", "Country_ES"])
    return filtered_data.filter(items=get_items())


def print_files():
    content = listdir('files')
    for f in content:
        print(f)


def delete_files():
    files = listdir('files/')
    for f in files:
        remove('files/'+f)
        print('File removed')


# Descarga los ficheros necesarios para trabajar
def download_files():
    delete_files()
    date_now = datetime.now()
    file_type = ['confirmed', 'recovered', 'deaths']
    url = 'https://covid19tracking.narrativa.com/csv/'
    for one_type in file_type:
        r = requests.get(url + one_type + '.csv')
        file = 'files/' + one_type + date_now.date().strftime("_%Y_%m_%d") + '.csv'
        if not path.exists(file):
            with open(file, 'wb') as f:
                f.write(r.content)
                print('Created file ' + file)


app = Flask(__name__)


@app.route('/', methods=("POST", "GET"))
def html_table():
    now = datetime.now()
    file = read_file('files/confirmed' + now.date().strftime("_%Y_%m_%d") + '.csv')
    return render_template('simple.html', tables=[file.to_html(classes='data')], titles=file.columns.values)


@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_figure():
    fig = Figure(figsize=[20, 5])
    axis = fig.add_subplot(1, 1, 1)
    now = datetime.now()
    file = read_file('files/confirmed' + now.date().strftime("_%Y_%m_%d") + '.csv')
    file = file.drop(columns='Region')
    xs = file.columns
    ys = []
    for l in list(file.columns):
        ys.append(file.iloc[0][l])
    axis.plot(xs, ys)
    return fig


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    download_files()
    print_files()
    app.run('0.0.0.0', 5002, debug=True)
