from datetime import datetime as dt, timedelta as td
import models as m
from sqlalchemy import and_, func, or_, extract
from tqdm import tqdm

start = dt(2015, 1, 1)
end = dt(2017, 1, 1)
minutes_delta = 15

with open('trips_train_3.csv', 'w') as file:
    while start < end:
        if start.isoweekday() not in range(1,6):
            start += td(days=1)
            continue
        if (start.hour == 0 and start.minute > 30) or start.hour < 5:
            start += td(minutes=minutes_delta)
            continue
        print(start.isoformat())
        file.write("%s\n" % m.s.query(m.Trip).filter(and_(
            m.Trip.departure_time >= start.isoformat(),
            m.Trip.departure_time <= (start + td(minutes=minutes_delta)).isoformat(),
            )).count())
        start += td(minutes=minutes_delta)

start = dt(2017, 1, 1)
end = dt(2018, 1, 1)
minutes_delta = 15

with open('trips_test_2.csv', 'w') as file:
    while start < end:
        if start.isoweekday() not in range(1,6):
            start += td(days=1)
            continue
        if (start.hour == 0 and start.minute > 30) or start.hour < 5:
            start += td(minutes=minutes_delta)
            continue
        print(start.isoformat())
        file.write("%s\n" % m.s.query(m.Trip).filter(and_(
            m.Trip.departure_time >= start.isoformat(),
            m.Trip.departure_time <= (start + td(minutes=minutes_delta)).isoformat(),
            )).count())
        start += td(minutes=minutes_delta)

# Train para los clusters
import json

cluster_list = json.load(open("clusters_list.json"))

for cluster, ids in cluster_list.items():
    start = dt(2015, 1, 1)
    end = dt(2017, 1, 1)
    minutes_delta = 15
    with open('cluster_data/trips_train_cluster%s.csv' % cluster, 'w') as file:
        pbar = tqdm(total=39673)
        while start < end:
            if start.isoweekday() not in range(1,6):
                start += td(days=1)
                continue
            if (start.hour == 0 and start.minute > 30) or start.hour < 5:
                start += td(minutes=minutes_delta)
                continue
            file.write("%s\n" % m.s.query(m.Trip).filter(and_(
                or_(m.Trip.departure_station.in_(ids), m.Trip.arrival_station.in_(ids)),
                m.Trip.departure_time >= start.isoformat(),
                m.Trip.departure_time <= (start + td(minutes=minutes_delta)).isoformat(),
                )).count())
            pbar.update()
            start += td(minutes=minutes_delta)
        pbar.close()

for cluster, ids in cluster_list.items():
    start = dt(2017, 1, 1)
    end = dt(2018, 1, 1)
    minutes_delta = 15
    with open('cluster_data/trips_test_cluster%s.csv' % cluster, 'w') as file:
        while start < end:
            if start.isoweekday() not in range(1,6):
                start += td(days=1)
                continue
            if (start.hour == 0 and start.minute > 30) or start.hour < 5:
                start += td(minutes=minutes_delta)
                continue
            print(start.isoformat())
            file.write("%s\n" % m.s.query(m.Trip).filter(and_(
                or_(m.Trip.departure_station.in_(ids), m.Trip.arrival_station.in_(ids)),
                m.Trip.departure_time >= start.isoformat(),
                m.Trip.departure_time <= (start + td(minutes=minutes_delta)).isoformat(),
                )).count())
            start += td(minutes=minutes_delta)
