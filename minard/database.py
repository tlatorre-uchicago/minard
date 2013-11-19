import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dbinfo import user, passwd, host, name

Base = declarative_base()

engine = sa.create_engine('mysql://%s:%s@%s/%s' % (user,passwd,host,name))
engine.connect()

meta = sa.MetaData()
meta.reflect(bind=engine)

tables = meta.tables

class Events(Base):
    __table__ = sa.Table('Events', meta, autoload=True)

class PMT(Base):
    __table__ = sa.Table('PMT', meta, autoload=True)

class Nhit(Base):
    __table__ = sa.Table('Nhit', meta, autoload=True)

class Position(Base):
    __table__ = sa.Table('Position', meta, autoload=True)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

def get_latest_key(table):
    return session.query(table).order_by(table.time.desc()).first().time

def get_charge_occupancy(key=None):
    if key is None:
        key = get_latest_key(PMT)
    result = session.query(PMT.id, PMT.chargeocc).filter(PMT.time == key).all()
    return zip(*result)

def get_number_of_events(key=None):
    if key is None:
        key = get_latest_key(Events)
    result = session.query(Events.events).filter(Events.time == key).one()[0]
    return result

def get_number_of_passed_events(key=None):
    if key is None:
        key = get_latest_key(Events)
    result = session.query(Events.passed_events).filter(Events.time == key).one()[0]
    return result

