import pandas as pd
import requests
from datetime import datetime
from os import  path
from os import listdir


def read_file(file):
    print(file)
    data = pd.read_csv(file, delimiter=',')
    print(data)

def print_files():
    content = listdir('files')
    for f in content:
        print(f)


# Descarga los ficheros necesarios para trabajar
def download_files():
    now = datetime.now()
    file_type = ['confirmed', 'recovered', 'deaths']
    url = 'https://covid19tracking.narrativa.com/csv/'
    for type in file_type:
        r = requests.get(url + type + '.csv')
        file = 'files/' + type + now.date().strftime("_%Y_%m_%d") + '.csv'
        if not path.exists(file):
            with open(file, 'wb') as f:
                f.write(r.content)
                print('Created file ' + file)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    download_files()
    print_files()
    read_file('files/confirmed_2020_11_22.csv')
