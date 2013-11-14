import sqlalchemy as sa
from dbinfo import user, passwd, host, name

engine = sa.create_engine('mysql://%s:%s@%s/%s' % (user,passwd,host,name))
engine.connect()

meta = sa.MetaData()
meta.reflect(bind=engine)

tables = meta.tables

print tables
