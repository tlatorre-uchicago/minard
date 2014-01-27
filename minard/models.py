from minard.database import engine, Base, MyBase
from sqlalchemy import MetaData, Table
import datetime

T_ZERO = datetime.datetime(1995,12,31,17,11,50,156730)

meta = MetaData()
meta.reflect(bind=engine)
tables = meta.tables

class Clock(Base):
    __table__ = Table('clock', meta, autoload=True)

class L2(Base, MyBase):
    __table__ = Table('L2', meta, autoload=True)

    def get_clock(self):
        with session_scope() as session:
            clock = session.query(Clock).filter(Clock.id == self.id).one()
            dt = datetime.timedelta(microseconds=clock.time10/10.0)
            return T_ZERO + dt

class PMT(Base):
    __table__ = Table('PMT', meta, autoload=True)

class Nhit(Base, MyBase):
    __table__ = Table('Nhit', meta, autoload=True)

class Position(Base):
    __table__ = Table('Position', meta, autoload=True)

class Alarms(Base, MyBase):
    __table__ = Table('alarms', meta, autoload=True)

def get_charge_occupancy(key=None):
    with session_scope() as session:
        if key is None:
            key = get_latest_key(session, PMT)
        result = session.query(PMT.id, PMT.chargeocc).filter(PMT.time == key).all()
    return zip(*result)

def get_number_of_events(key=None):
    with session_scope() as session:
        if key is None:
            key = session.query(L2).order_by(L2.id.desc()).first().id
        result = session.query(L2.events).filter(L2.id == key).one()[0]
    return result

def get_number_of_passed_events(key=None):
    with session_scope() as session:
        if key is None:
            key = session.query(L2).order_by(L2.id.desc()).first().id
        result = session.query(L2.passed_events).filter(L2.id == key).one()[0]
    return result
