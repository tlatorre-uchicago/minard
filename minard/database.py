from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from dbinfo import user, passwd, host, name
from contextlib import contextmanager
import datetime

engine = create_engine('mysql://%s:%s@%s/%s' % (user,passwd,host,name), pool_recycle=60)

Session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))

T_ZERO = datetime.datetime(1995,12,31,17,11,50,156730)

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

class Clock(Base):
    __table__ = Table('clock', meta, autoload=True)

class L2(Base):
    __table__ = Table('L2', meta, autoload=True)

    def get_clock(self):
        with session_scope() as session:
            clock = session.query(Clock).filter(Clock.id == self.id).one()
            dt = datetime.timedelta(microseconds=clock.time10/10.0)
            return T_ZERO + dt

class PMT(Base):
    __table__ = Table('PMT', meta, autoload=True)

class Nhit(Base):
    __table__ = Table('Nhit', meta, autoload=True)

class Position(Base):
    __table__ = Table('Position', meta, autoload=True)

class Alarms(Base):
    __table__ = Table('alarms', meta, autoload=True)

def get_latest_key(session, table):
    return session.query(table).order_by(table.time.desc()).first().time

def row_to_dict(row):
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}

def get_alarms():
    with session_scope() as session:
        result = map(row_to_dict,session.query(Alarms).all())
    return result

def get_l2_info(id=None):
    with session_scope() as session:
        if id is None:
            id = session.query(L2).order_by(L2.id.desc()).first().id
        l2_info = session.query(L2).filter(L2.id == id).one()
        result = row_to_dict(l2_info)
        result['clock'] = l2_info.get_clock().strftime('%Y-%m-%dT%H-%M-%S')

    if result['entry_time'] is None:
        result['entry_time'] = '???'
    else:
        result['entry_time'] = result['entry_time'].strftime('%Y-%m-%dT%H-%M-%S')

    return result

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

def get_nhit(id=None):
    with session_scope() as session:
        if id is None:
            id = get_latest_key(session, Nhit)
        result = session.query(Nhit).filter(Nhit.time == id).one()
        hist = [getattr(result,'nhit%i' % i) for i in range(30)]
    bins = range(5,300,10)
    return dict(zip(bins,hist))

def get_pos_hist(id=None):
    with session_scope() as session:
        if id is None:
            id = get_latest_key(session, Position)
        result = session.query(Position).filter(Position.time == id).one()
        hist = [getattr(result,'pos%i' % i) for i in range(13)]
    bins = range(25,650,50)
    return dict(zip(bins,hist))

