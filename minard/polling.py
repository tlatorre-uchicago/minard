import couchdb
from .db import engine 
from .db import engine2

#def polling_info(data_type):
def polling_info(crate, slot, channel):

    #if data_type == "cmos":
    #   dtype = "cmos_rate"
    #if data_type == "base":
    #   dtype = "base_current"

    #data = [0]*9728
    conn = engine2.connect()

    result = conn.execute("SELECT run from cmos order by run DESC limit 1")
    cmos_run = result.fetchone()
    for run in cmos_run:
        run_ = run

    #result = conn.execute('''select run from run_state order by timestamp DESC limit 1''') 
    #result = result.fetchone()
    #for run_ in result:
    #   run = int(run_)

    #command = '''SELECT distinct on (run,crate,slot,channel) crate, slot, channel, %s from %s where run = %i order by run,crate,slot,channel''' % (dtype, data_type, run) 
    result = conn.execute("SELECT * "
               "FROM cmos where run = %s and crate = %s and slot = %s and channel = %s" \
               % (run_, crate, slot, channel))

    keys = result.keys()
    row = result.fetchone()

    cmos = dict(zip(keys,row))

    result = conn.execute("SELECT run from base order by run DESC limit 1")
    base_run = result.fetchone() 
    for run in base_run:
        run_ = run

    result = conn.execute("SELECT * "
               "FROM base where run = %s and crate = %s and slot = %s and channel = %s" \
               % (run_, crate, slot, channel))

    keys = result.keys()
    row = result.fetchone()

    base = dict(zip(keys,row))
 
    return cmos, base

def threshold(crate, slot, channel):

    DB_HOST = 'http://couch.snopl.us'
    DB_NAME = 'debugdb'
    DB_CREDENTIALS = ('snoplus', 'dontestopmenow')

    couch = couchdb.Server(DB_HOST)
    couch.resource.credentials = DB_CREDENTIALS
    db = couch[DB_NAME]

    vthr_zero = []
    for row in db.view('penn_daq_views/get_fec_by_generated'):

        crate_doc = row.value['crate']
        slot_doc = row.value['card']

        if crate_doc == crate and slot_doc == slot:
            try:
               timestamp_ecal = row.value['timestamp_ecal']
               ecal_id = row.value['ecal_id']
            except KeyError:
               continue
            try:
               hw = row.value['hw']
               vthr_zero = hw['vthr_zero']
            except KeyError:
               continue

    conn = engine.connect()
    result= conn.execute("select vthr from current_detector_state where "
                         "crate = %s and slot = %s" % \
                         (crate, slot))

    keys = result.keys()
    row = result.fetchone()

    vthr = []
    for threshold in row:
        for i in range(len(threshold)):
            threshold[i] = (threshold[i] - vthr_zero[i])

    detector_state = dict(zip(keys, row))
 
    return detector_state

