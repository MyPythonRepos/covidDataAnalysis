from flask import Flask, render_template, Response
from datetime import datetime, timedelta
from os import path, listdir, remove, replace
import pandas as pd
import requests
import locale
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
import json

app = Flask(__name__)
PROVINCIAS = ''
locale.setlocale(locale.LC_ALL, 'es-ES')


# def get_items():
#     hoy = datetime.now()
#     primer_dia = hoy.replace(day=1)
#     items = ['fecha', 'num_casos', 'num_casos_prueba_pcr', 'num_casos_prueba_ag']
#     while primer_dia.day < hoy.day:
#         items.append(primer_dia.date().strftime("%Y-%m-%d"))
#         primer_dia = primer_dia + timedelta(days=1)
#     items.append(hoy.date().strftime("%Y-%m-%d"))
#     return items

# Por defecto, se muestran los datos del mes en curso para la provincia solicitada
def read_file(file, provincia):
    data = pd.DataFrame(pd.read_csv(file, delimiter=','))
    fin_periodo = datetime.now()
    inicio_periodo = fin_periodo.replace(day=1)
    mes = fin_periodo.strftime("%B")
    filtered_data = data[(data['provincia_iso'] == provincia)
                         & (data['fecha'].between(inicio_periodo.date().strftime("%Y-%m-%d"),
                                                  fin_periodo.date().strftime("%Y-%m-%d")))]
    filtered_data = filtered_data[['fecha', 'num_casos', 'num_casos_prueba_pcr', 'num_casos_prueba_ag']]
    filtered_data.index = range(1, len(filtered_data.index)+1)
    return filtered_data, mes


# def print_files():
#     content = listdir('files')
#     for f in content:
#         print(f)


def delete_files():
    files = listdir('files/')
    for f in files:
        remove('files/' + f)
        print('File removed')


def save_files(file, r):
    with open(file, 'wb') as f:
        f.write(r.content)
        print('Created file ' + file)


def backup_files(file):
    now = datetime.now()
    replace(file, 'files/casos_diagnostico_provincia.' + now.strftime("%Y%m%d_%H%M%S"))


# Descarga los ficheros necesarios para trabajar
def download_files():
    url: str = 'https://cnecovid.isciii.es/covid19/resources/casos_tecnica_provincia.csv'
    r = requests.get(url)
    file = 'files/casos_diagnostico_provincia.csv'
    if not path.exists(file):
        save_files(file, r)
    else:
        # TODO crear función backup ficheros y sobreescribir ficheros
        backup_files(file)
        save_files(file, r)


def leer_provincias():
    f = open("files/provincias.json", "r", encoding="utf8")
    content = f.read()
    PROVINCIAS = json.loads(content)
    return PROVINCIAS


def get_nombre_provincia(prov):
    nombre_provincia = ''
    PROVINCIAS = leer_provincias()
    for key in PROVINCIAS:
        if key == prov:
            nombre_provincia = PROVINCIAS[key]
            break
    return nombre_provincia


@app.route('/', methods=("POST", "GET"))
def html_table():
    PROVINCIAS=leer_provincias()
    return render_template('index.html', provincias=PROVINCIAS)


@app.route('/datos/prov=<provincia>', methods=("POST", "GET"))
def mostrar_datos(provincia):
    now = datetime.now()
    file, mes = read_file('files/casos_diagnostico_provincia.csv', provincia)
    return render_template('datos_por_provincia.html', tables=[file.to_html(classes='data')], titles=get_nombre_provincia(provincia), mes=mes)


# @app.route('/plot.png')
# def plot_png():
#     fig = create_figure()
#     output = io.BytesIO()
#     FigureCanvas(fig).print_png(output)
#     return Response(output.getvalue(), mimetype='image/png')


# def create_figure():
#     fig = Figure(figsize=[20, 5])
#     axis = fig.add_subplot(1, 1, 1)
#     # now = datetime.now()
#     # file = read_file('files/confirmed' + now.date().strftime("_%Y_%m_%d") + '.csv')
#     file = confirmed_cases_by_region('Canarias')
#     file = file.drop(columns='Region')
#     xs = file.columns
#     ys = []
#     for element in list(file.columns):
#         ys.append(file.iloc[0][element])
#     axis.plot(xs, ys)
#     file = confirmed_cases_by_region('Madrid')
#     file = file.drop(columns='Region')
#     zs = []
#     for element in list(file.columns):
#         zs.append(file.iloc[0][element])
#     axis.plot(xs, zs)
#     return fig


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    download_files()
    app.run('0.0.0.0', 5002)
