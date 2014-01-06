from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from dbinfo import user, passwd, host, name
from contextlib import contextmanager

engine = create_engine('mysql://%s:%s@%s/%s' % (user,passwd,host,name), pool_recycle=60)

Session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

meta = MetaData()
meta.reflect(bind=engine)

tables = meta.tables

Base = declarative_base()

class Events(Base):
    __table__ = Table('Events', meta, autoload=True)

class PMT(Base):
    __table__ = Table('PMT', meta, autoload=True)

class Nhit(Base):
    __table__ = Table('Nhit', meta, autoload=True)

class Position(Base):
    __table__ = Table('Position', meta, autoload=True)

def get_latest_key(session, table):
    return session.query(table).order_by(table.time.desc()).first().time

def get_charge_occupancy(key=None):
    with session_scope() as session:
        if key is None:
            key = get_latest_key(session, PMT)
        result = session.query(PMT.id, PMT.chargeocc).filter(PMT.time == key).all()
    return zip(*result)

def get_number_of_events(key=None):
    with session_scope() as session:
        if key is None:
            key = get_latest_key(session, Events)
        result = session.query(Events.events).filter(Events.time == key).one()[0]
    return result

def get_number_of_passed_events(key=None):
    with session_scope() as session:
        if key is None:
            key = get_latest_key(session, Events)
        result = session.query(Events.passed_events).filter(Events.time == key).one()[0]
    return result

def get_nhit(key=None):
    with session_scope() as session:
        if key is None:
            key = get_latest_key(session, Nhit)
        result = session.query(Nhit).filter(Nhit.time == key).one()
        hist = [getattr(result,'nhit%i' % i) for i in range(30)]
    bins = range(5,300,10)
    return dict(zip(bins,hist))

def get_pos_hist(key=None):
    with session_scope() as session:
        if key is None:
            key = get_latest_key(session, Position)
        result = session.query(Position).filter(Position.time == key).one()
        hist = [getattr(result,'pos%i' % i) for i in range(13)]
    bins = range(25,650,50)
    return dict(zip(bins,hist))

