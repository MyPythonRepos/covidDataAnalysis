from flask import Flask, request, render_template, session, redirect
import pandas as pd
import requests
from datetime import datetime
from os import path
from os import listdir
from os import remove


def read_file(file):
    data = pd.DataFrame(pd.read_csv(file, delimiter=','))
    data_mask = data['Country_EN'] == 'Spain'
    filtered_data = data[data_mask]
    print(filtered_data.loc[:, '2020-11-01':'2020-11-30'])
    return filtered_data.agg .filter(items=['Region', '2020-11-01', '2020-11-30'])


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
    file = read_file('files/confirmed' + now.date().strftime("_%Y_%m_%d") + '.csv')
    return render_template('simple.html',  tables=[file.to_html(classes='data')], titles=file.columns.values)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    download_files()
    print_files()
    now = datetime.now()
    read_file('files/confirmed' + now.date().strftime("_%Y_%m_%d") + '.csv')
    app.run('0.0.0.0', 5000, debug=True)
