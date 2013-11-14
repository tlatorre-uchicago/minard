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

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
