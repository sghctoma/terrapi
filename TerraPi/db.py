# database module

import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, Float, String, \
        DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.sql import func


Base = declarative_base()

class SensorType(enum.Enum):
    temperature = 1
    humidity = 2
    distance = 3
    uvi = 4
    ph = 5
    weight = 6
    pressure = 7

class Sensor(Base):
    __tablename__ = 'sensors'
    id = Column(Integer, primary_key=True)
    type = Column(Enum(SensorType), nullable=False)
    name = Column(String(32), nullable=False)
    description = Column(String(256))
    UniqueConstraint(type, name)

class Measurement(Base):
    __tablename__ = 'measurements'
    timestamp = Column(DateTime, primary_key=True, server_default=func.now())
    sensor_id = Column(Integer, ForeignKey('sensors.id'), nullable=False, primary_key=True)
    sensor = relationship(Sensor)
    value = Column(Float, nullable=False)

def create_sessionmaker(conn_string):
    engine = create_engine(conn_string)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    return Session;
