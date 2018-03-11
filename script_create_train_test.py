from datetime import datetime as dt, timedelta as td
import models as m
from sqlalchemy import and_, func, or_, extract

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
