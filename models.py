import json
from sqlalchemy import Column, create_engine, Integer, String, ARRAY, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base

config = json.load(open('config.json'))
ENGINE = create_engine(config['connection_string'])
BASE = declarative_base()
SESSION = sessionmaker(bind=ENGINE)
s = SESSION()

def create():
    """ Crear la base de datos """
    engine = create_engine(config['connection_string'])
    if not database_exists(engine.url):
        create_database(engine.url)
        print('created')
    print(database_exists(engine.url))

def delete_all():
    Station.__table__.drop(ENGINE)
    Trip.__table__.drop(ENGINE)

def create_all():
    """ Crear todas las tablas """
    BASE.metadata.create_all(ENGINE)

class Station(BASE):
    __tablename__ = 'station'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    address = Column(String(255))
    addressNumber = Column(String(255))
    zipCode = Column(String(255))
    districtCode = Column(String(255))
    districtName = Column(String(255))
    nearbyStations = Column(ARRAY(Integer))
    location = Column(String(255))
    stationType = Column(String(255))
    capacity = Column(Integer)

class Trip(BASE):
    __tablename__ = 'trip'
    id = Column(Integer, primary_key=True)
    gender = Column(String(1))
    age = Column(Integer)
    bicycle_id = Column(Integer)
    departure_station = Column(Integer)
    departure_time = Column(DateTime)
    arrival_station = Column(Integer)
    arrival_time = Column(DateTime)
