from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from minard import app
import datetime

# see http://flask.pocoo.org/docs/patterns/sqlalchemy/

user = app.config['DBUSER']
host = app.config['DBHOST']
passwd = app.config['DBPASS']
name = app.config['DBNAME']

engine = create_engine('mysql://%s:%s@%s/%s' % (user,passwd,host,name), pool_recycle=60)
db_session = scoped_session(sessionmaker(autocommit=False,autoflush=False,bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

class MyBase(object):
    @classmethod
    def latest(cls):
        return db_session.query(cls).order_by(cls.id.desc()).first()

    def __iter__(self):
        """
        Used so that you can call dict(object) and get a dictionary
        of the column name and value.
        """
        for column in self.__table__.columns:
            value = getattr(self,column.name)

            if isinstance(value,datetime.datetime):
                # strftime datetime objects otherwise flask
                # jsonify will assume they are in Greenwich Mean Time
                value = value.strftime('%Y-%m-%dT%H:%M:%S')

            yield column.name, value

def init_db():
    from minard import models
    Base.metadata.create_all(bind=engine)

