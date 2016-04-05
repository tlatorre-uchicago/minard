#from sqlalchemy import engine, create_engine
import sqlalchemy
from minard import app
PSQL_DB_NAME = 'test'

def fetch_from_table_with_key(table_name,key,key_name='key'):
    pw = app.config['DB_PASS']
    uname = app.config['DB_UNAME']
    engine = sqlalchemy.create_engine('postgresql://'+str(uname)+':'+str(pw)+'@minard/'+PSQL_DB_NAME)
    try:
        conn = engine.connect()
    except Exception as e:
        #Do somethign here?
        raise e;
    command = "SELECT * FROM "+str(table_name)+" WHERE "+str(key_name)+" = "+str(key)
    res =  conn.execute(command)
    try:
        values = zip(res.keys(),res.fetchone())
    except TypeError:
        #Chances are this failed b/c the SELECT command didn't find anything
        raise ValueError(str(key_name)+" "+str(run)+" is not valid...probably")
    conn.close()
    return dict(values)

def get_detector_control_state(key):
    return fetch_from_table_with_key('detector_control',key)
    
def get_caen_state(key):
    return fetch_from_table_with_key('caen',key)

def get_mtc_state(key):
    return fetch_from_table_with_key('mtc',key)

def get_crate_state(key):
    return fetch_from_table_with_key('crate',key)

def get_fec_state(key):
    return fetch_from_table_with_key('fec',key)

def get_run_state(run):
    return fetch_from_table_with_key('run_state',run,key_name='run')
