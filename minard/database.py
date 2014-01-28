from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from dbinfo import user, passwd, host, name
import datetime

engine = create_engine('mysql://%s:%s@%s/%s' % (user,passwd,host,name), pool_recycle=60)
db_session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class MyBase(object):
    @classmethod
    def latest(cls):
        return db_session.query(cls).order_by(cls.id.desc()).first()

    def __iter__(self):
        for column in self.__table__.columns:
            value = getattr(self,column.name)

            if isinstance(value,datetime.datetime):
                value = value.strftime('%Y-%m-%dT%H-%M-%S')

            yield column.name, value

def init_db():
    from minard import models
    Base.metadata.create_all(bind=engine)

