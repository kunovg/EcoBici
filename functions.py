# encoding=utf-8
import json
import pandas as pd
import models as m
from sqlalchemy import and_, func, or_, extract
import datetime as dt

def weekday_name(weekday):
    days = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
    return days[weekday]

def get_stations():
    s = m.s.query(m.Station)
    df = pd.read_sql(s.statement, s.session.bind)
    return df

def analyze_departures_by_station(years, stations):
    """ Numero de salidas por estación durante un año """
    for year in years:
        # Leer todos los viajes realizados en X año
        print('Leyendo datos del año {}'.format(year))
        trips_per_year = m.s.query(m.Trip).filter(and_(
            m.Trip.departure_time >= '{}-01-01 00:00:00'.format(year),
            m.Trip.departure_time <= '{}-12-31 23:59:59'.format(year)
        ))
        df_year = pd.read_sql(trips_per_year.statement, trips_per_year.session.bind)

        # Crear una columna que represente el día de la semana en que se hizo el viaje
        # 0 es Lunes y 6 es Domingo
        df_year['weekday'] = df_year['departure_time'].apply(lambda x: x.weekday())

        dict_year = {}
        for s in stations:
            print(s, year)
            dict_year[str(s)] = {weekday_name(d): len(
                df_year[(df_year.departure_station == s) & (df_year.weekday == d)].index)
                for d in range(7)
            }

        # Guardar los datos
        with open('data/salidas_{}.json'.format(year), 'w') as file:
            json.dump(dict_year, file)

def analyze_arrivals_by_station(years, stations):
    """ Numero de llegadas por estación durante un año """
    for year in years:
        # Leer todos los viajes realizados en X año
        print('Leyendo datos del año {}'.format(year))
        trips_per_year = m.s.query(m.Trip).filter(and_(
            m.Trip.departure_time >= '{}-01-01 00:00:00'.format(year),
            m.Trip.departure_time <= '{}-12-31 23:59:59'.format(year)
        ))
        df_year = pd.read_sql(trips_per_year.statement, trips_per_year.session.bind)

        # Crear una columna que represente el día de la semana en que se hizo el viaje
        # 0 es Lunes y 6 es Domingo
        df_year['weekday'] = df_year['departure_time'].apply(lambda x: x.weekday())

        dict_year = {}
        for s in stations:
            print(s, year)
            dict_year[str(s)] = {weekday_name(d): len(
                df_year[(df_year.arrival_station == s) & (df_year.weekday == d)].index)
                for d in range(7)
            }

        # Guardar los datos
        with open('data/llegadas_{}.json'.format(year), 'w') as file:
            json.dump(dict_year, file)

def analyze_trips_by_week(years):
    """ Numero de viajes por semana """
    result = {}
    for year in years:
        # Leer todos los viajes realizados en X año
        print('Leyendo datos del año {}'.format(year))
        trips_per_year = m.s.query(m.Trip).filter(and_(
            m.Trip.departure_time >= '{}-01-01 00:00:00'.format(year),
            m.Trip.departure_time <= '{}-12-31 23:59:59'.format(year)
        ))
        df_year = pd.read_sql(trips_per_year.statement, trips_per_year.session.bind)

        # Crear una columna que represente el número de la semana en el año
        df_year['week'] = df_year['departure_time'].apply(lambda x: int(x.strftime('%W')))
        result[year] = {str(w): len(df_year[df_year.week == w].index) for w in range(54)}

    # Guardar los datos
    with open('data/viajes_por_semana.json', 'w') as file:
        json.dump(result, file)


def analyze_trips_by_weekday(years, weekdays):
    """ Numero de viajes por día de la semana durante un año """
    for year in years:
        # Leer todos los viajes realizados en X año
        print('Leyendo datos del año {}'.format(year))
        trips_per_year = m.s.query(m.Trip).filter(and_(
            m.Trip.departure_time >= '{}-01-01 00:00:00'.format(year),
            m.Trip.departure_time <= '{}-12-31 23:59:59'.format(year)
        ))
        df_year = pd.read_sql(trips_per_year.statement, trips_per_year.session.bind)

        # Crear una columna que represente el día de la semana en que se hizo el viaje
        # 0 es Lunes y 6 es Domingo
        df_year['weekday'] = df_year['departure_time'].apply(lambda x: x.weekday())

        dict_year = {}
        for weekday in weekdays:
            print(weekday, year)
            trips = df_year[df_year.weekday == weekday]
            dict_year[weekday_name(weekday)] = len(trips.index)

        # Guardar los datos
        with open('data/trips_weekday_{}.json'.format(year), 'w') as file:
            json.dump(dict_year, file)

def analyze_trip_distribution(weekday, years):
    """ Número de viajes en diferentes weekdays de años """
    def all_weekdays(year, weekday):
        """ Todos los weekdays de un año """
        d = dt.datetime(year, 1, 1)  # January 1st
        diff = weekday - d.weekday()
        d += dt.timedelta(days=diff if diff >= 0 else 7+diff)
        while d.year == year:
            yield d
            d += dt.timedelta(days=7)

    result = {}
    for year in years:
        # Leer todos los viajes realizados en X año
        print('Leyendo datos del año {}'.format(year))
        trips_per_year = m.s.query(m.Trip).filter(and_(
            m.Trip.departure_time >= '{}-01-01 00:00:00'.format(year),
            m.Trip.departure_time <= '{}-12-31 23:59:59'.format(year)
        ))
        df_year = pd.read_sql(trips_per_year.statement, trips_per_year.session.bind)
        # Crear una columna que represente la fecha del viaje
        df_year['day'] = df_year['departure_time'].apply(lambda x: x.strftime('%Y-%m-%d'))

        print('Analizando datos del año {}'.format(year))
        result = {**result, **{
            d.strftime('%Y-%m-%d'): len(df_year[df_year.day == d.strftime('%Y-%m-%d')].index)
            for d in all_weekdays(int(year), weekday)
        }}

    # Guardar los datos
    with open('data/trip_distribution_{}.json'.format(weekday_name(weekday)), 'w') as file:
        json.dump(result, file, sort_keys=True)

def analyze_trips_by_moments(weekday, intervalo, years):
    """ Numero de viajes en determinados lapsos del día por un año """
    def generate_time_lapse(intervalo):
        """ Regresa un array de strings en formato %H:%M """
        delta = dt.timedelta(minutes=intervalo)  # 1440 minutos en un día
        start = dt.datetime.now().replace(hour=0, minute=0)
        tiempos = [(start + i * delta).strftime('%H:%M') for i in range(int(1440 / intervalo))]
        tiempos.append('23:59:59')  # Último momento del día
        return tiempos

    tiempos, result = generate_time_lapse(intervalo), {}
    for year in years:
        # Leer todos los viajes realizados en X año
        print('Leyendo datos del año {}'.format(year))
        trips_per_year = m.s.query(m.Trip).filter(and_(
            m.Trip.departure_time >= '{}-01-01 00:00:00'.format(year),
            m.Trip.departure_time <= '{}-12-31 23:59:59'.format(year),
            func.to_char(m.Trip.departure_time, 'ID') == str(weekday+1)  # En SQL van de 1 a 7
        ))
        df_year = pd.read_sql(trips_per_year.statement, trips_per_year.session.bind)

        # Crear una columna que represente el día de la semana en que se hizo el viaje
        # 0 es Lunes y 6 es Domingo
        df_year['weekday'] = df_year['departure_time'].apply(lambda x: x.weekday())
        # Set DatetimeIndex
        df_year.set_index('departure_time', inplace=True)

        print('Analizando datos del año {}'.format(year))
        result[year] = {tiempos[t]: len(df_year[df_year.weekday == weekday].between_time(
                        tiempos[t],
                        tiempos[t+1]).index) for t in range(len(tiempos)-1)}

    with open('data/trips_during_weekday_{}.json'.format(weekday_name(weekday)), 'w') as file:
        json.dump(result, file)

def analyze_trips_by_moments_for_day(days, intervalo):
    """ Numero de viajes en determinados lapsos para un dia en especifico(datetime) """
    def generate_time_lapse(intervalo):
        """ Regresa un array de strings en formato %H:%M """
        delta = dt.timedelta(minutes=intervalo)  # 1440 minutos en un día
        start = dt.datetime.now().replace(hour=0, minute=0)
        tiempos = [(start + i * delta).strftime('%H:%M') for i in range(int(1440 / intervalo))]
        tiempos.append('23:59:59')  # Último momento del día
        return tiempos

    tiempos, result = generate_time_lapse(intervalo), {}
    for day in days:
        start, end = day.replace(hour=0, minute=0, second=0), day.replace(hour=23, minute=59, second=59)
        # Leer todos los viajes realizados en X día
        print('Leyendo datos del día {}'.format(day))
        trips_per_year = m.s.query(m.Trip).filter(and_(
            m.Trip.departure_time >= start,
            m.Trip.departure_time <= end
        ))
        df_year = pd.read_sql(trips_per_year.statement, trips_per_year.session.bind)
        # Set DatetimeIndex
        df_year.set_index('departure_time', inplace=True)

        print('Analizando datos del día {}'.format(day))
        result[day.strftime('%Y-%m-%d')] = {tiempos[t]: len(df_year.between_time(tiempos[t], tiempos[t+1]).index)
                                            for t in range(len(tiempos)-1)}

    with open('data/trips_during_days.json', 'w') as file:
        json.dump(result, file)

def analyze_trips_by_moments_day_station(day, station, intervalo):
    """ Numero de viajes en determinados lapsos del día para cierta estación"""
    def generate_time_lapse(intervalo):
        """ Regresa un array de strings en formato %H:%M """
        delta = dt.timedelta(minutes=intervalo)  # 1440 minutos en un día
        start = dt.datetime.now().replace(hour=0, minute=0)
        tiempos = [(start + i * delta).strftime('%H:%M') for i in range(int(1440 / intervalo))]
        tiempos.append('23:59:59')  # Para que no exista un overlapping con el primer intervalo
        return tiempos

    tiempos, result = generate_time_lapse(intervalo), {}
    start, end = day.replace(hour=0, minute=0, second=0), day.replace(hour=23, minute=59, second=59)

    # Leer todos los viajes de X estación durante Y día
    print('Leyendo datos del día {} estación {}'.format(day, station))
    trips_per_year = m.s.query(m.Trip).filter(and_(
        m.Trip.departure_time >= start,
        m.Trip.departure_time <= end)).filter(or_(
            m.Trip.departure_station == station,
            m.Trip.arrival_station == station
        ))
    df_year = pd.read_sql(trips_per_year.statement, trips_per_year.session.bind)

    # Set DatetimeIndex
    df_year.set_index('departure_time', inplace=True)

    for t in range(len(tiempos)-1):
        salidas = df_year[df_year.departure_station == station].between_time(tiempos[t], tiempos[t+1]).index
        llegadas = df_year[df_year.arrival_station == station].between_time(tiempos[t], tiempos[t+1]).index
        result[tiempos[t]] = {'salidas': len(salidas), 'llegadas': len(llegadas)}
    with open('data/trips_{}_station_{}.json'.format(day.strftime('%Y-%m-%d'), station), 'w') as file:
        json.dump(result, file)

def most_common_trips(weekday, year):
    """ Los viajes más comunes en cierto weekday """
    def stations(s1, s2):
        return '{}-{}'.format(s1, s2) if s1 < s2 else '{}-{}'.format(s2, s1)

    print('Leyendo datos weekday: {}\taño: {}'.format(weekday, year))
    trips = m.s.query(m.Trip).filter(and_(
        m.Trip.departure_time >= '{}-01-01 00:00:00'.format(year),
        m.Trip.departure_time <= '{}-12-31 23:59:59'.format(year),
        func.to_char(m.Trip.departure_time, 'ID') == str(weekday+1)  # En SQL van de 1 a 7
    ))
    df = pd.read_sql(trips.statement, trips.session.bind)
    df['stations'] = df.apply(lambda row: stations(row['departure_station'], row['arrival_station']), axis=1)
    return df['stations'].value_counts()

def bicycle_data(bicycle_id):
    print('Leyendo viajes de la bicicleta {}'.format(bicycle_id))
    trips = m.s.query(m.Trip).filter_by(bicycle_id=bicycle_id)
    df = pd.read_sql(trips.statement, trips.session.bind).sort_values(by='departure_time')
    if len(df) == 0:
        return {}
    df['trip_length'] = df.apply(lambda row: (row['arrival_time'] - row['departure_time']).total_seconds(), axis=1)
    return {
        'first_trip': df['departure_time'].iloc[0],
        'last_trip': df['departure_time'].iloc[-1],
        'total_time': df['trip_length'].sum(),
        'total_trips': len(df),
    }

def analyze_trips_by_moments_week_station(day, station, intervalo):
    """ Numero de viajes por lapsos durante toda una semana para cierta estación"""
    def generate_time_lapse(intervalo):
        """ Regresa un array de strings en formato %H:%M """
        delta = dt.timedelta(minutes=intervalo)  # 1440 minutos en un día
        start = dt.datetime.now().replace(hour=0, minute=0)
        tiempos = [(start + i * delta).strftime('%H:%M') for i in range(int(1440 / intervalo))]
        tiempos.append('23:59:59')  # Para que no exista un overlapping con el primer intervalo
        return tiempos

    tiempos, result = generate_time_lapse(intervalo), {}
    start, end = day.replace(hour=0, minute=0, second=0), day.replace(hour=23, minute=59, second=59) + dt.timedelta(days=7)

    # Leer todos los viajes de X estación durante Y día
    print('Leyendo datos de la semana {} estación {}'.format(day, station))
    trips_per_year = m.s.query(m.Trip).filter(and_(
        m.Trip.departure_time >= start,
        m.Trip.departure_time <= end)).filter(or_(
            m.Trip.departure_station == station,
            m.Trip.arrival_station == station
        ))
    df = pd.read_sql(trips_per_year.statement, trips_per_year.session.bind)

    # Set DatetimeIndex
    df.set_index('departure_time', inplace=True)

    for dia in range(7):
        result[str(dia)] = {}
        df2 = df.ix[(day + dt.timedelta(days=dia)).strftime('%Y-%m-%d'):(day + dt.timedelta(days=dia)).strftime('%Y-%m-%d')]
        for t in range(len(tiempos)-1):
            salidas = df2[df2.departure_station == station].between_time(tiempos[t], tiempos[t+1]).index
            llegadas = df2[df2.arrival_station == station].between_time(tiempos[t], tiempos[t+1]).index
            result[str(dia)][tiempos[t]] = {'salidas': len(salidas), 'llegadas': len(llegadas)}
    with open('data/trips_week_{}_station_{}.json'.format(day.strftime('%Y-%m-%d'), station), 'w') as file:
        json.dump(result, file)

def trips_by_hour(hour, year, exclude_days=['6', '7']):
    trips = m.s.query(m.Trip).filter(and_(
        hour == extract('hour', m.Trip.departure_time),
        m.Trip.departure_time >= '{}-01-01 00:00:00'.format(year),
        m.Trip.departure_time <= '{}-12-31 23:59:59'.format(year),
        ~func.to_char(m.Trip.departure_time, 'ID').in_(exclude_days)
    ))
    return pd.read_sql(trips.statement, trips.session.bind)
