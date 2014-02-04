from minard.database import engine, Base, MyBase, db_session
from sqlalchemy import MetaData, Table
from sqlalchemy.orm.exc import NoResultFound
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
        clock = db_session.query(Clock).filter(Clock.id == self.id).one()
        dt = datetime.timedelta(microseconds=clock.time10/10.0)
        return T_ZERO + dt

    def __iter__(self):
    	for key, value in MyBase.__iter__(self):
            yield key, value

        try:
            yield 'clock', self.get_clock().strftime('%Y-%m-%dT%H:%M:%S')
        except NoResultFound:
            yield 'clock', '???'

class PMT(Base, MyBase):
    __table__ = Table('pmt', meta, autoload=True)

class Nhit(Base, MyBase):
    __table__ = Table('nhit', meta, autoload=True)

class Position(Base, MyBase):
    __table__ = Table('position', meta, autoload=True)

class Alarms(Base, MyBase):
    __table__ = Table('alarms', meta, autoload=True)
