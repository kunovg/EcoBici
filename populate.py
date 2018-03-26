import os
import csv
import glob
import models as m
from ecobici import EcobiciManager
# from datetime import datetime as dt
from dateutil import parser
from tqdm import tqdm


config = m.config
e = EcobiciManager(config['client_secret'], config['client_id'])

def insert_stations():
    stations = e.get_stations()
    state = e.get_available()
    for station in stations:
        dummy = next(s for s in state if s['id'] == station['id'])
        _station = station
        _station['location'] = '{},{}'.format(station['location']['lat'], station['location']['lon'])
        _station.pop('altitude', None)
        _station['capacity'] = dummy['availability']['bikes'] + dummy['availability']['slots']
        m.s.add(m.Station(**_station))
    m.s.commit()

def read_csv(filename):
    f = open(filename)
    reader = csv.reader(f)
    next(reader)  # No leer los headers
    for row in tqdm(reader):
        if row[2].isdigit():
            trip = m.Trip(gender=row[0],
                          age=row[1],
                          bicycle_id=row[2],
                          departure_station=row[3],
                          departure_time=parser.parse('{} {}'.format(row[4], row[5]), dayfirst='/' in row[4]),
                          arrival_station=row[6],
                          arrival_time=parser.parse('{} {}'.format(row[7], row[8]), dayfirst='/' in row[7])
                          )
            m.s.add(trip)
    f.close()

if __name__ == "__main__":
    # print('insertando estaciones')
    # insert_stations()
    # print('estaciones insertadas')

    files = []
    os.chdir("C:/Users/kuno/Documents/dataEcobici")
    for file in glob.glob("*.csv"):
        files.append(file)

    print('iniciando insercion de viajes')
    for file in files:
        read_csv(file)
        m.s.commit()
        print('archivo {} insertado'.format(file))
