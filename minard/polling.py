import couchdb
from .db import engine 
from .db import engine2

def polling_info(data_type):

    dtype = ""
    if data_type == "cmos":
       dtype = "cmos_rate"
    if data_type == "base":
       dtype = "base_current"

    data = [0]*9728
    conn = engine2.connect()

    result = conn.execute("SELECT run from cmos order by run DESC limit 1")
    cmos_run = result.fetchone()
    for run in cmos_run:
        run_ = run
    print data_type, dtype, run

    result = conn.execute('''SELECT distinct on (run,crate,slot,channel) crate, slot, channel, %s from %s where run = %i order by run,crate,slot,channel''' % (dtype, data_type, run_))

    row = result.fetchall()
    for crate,card,channel,cmos_rate in row:
        lcn = crate*512+card*32+channel
        data[lcn] = cmos_rate
    #row = zip(*row)
    #print row

    return data

def polling_info_card(data_type, crate):

    if data_type == "cmos":
       dtype = "cmos_rate"
    if data_type == "base":
       dtype = "base_current"

    data = [0]*9728*2
    conn = engine2.connect()

    result = conn.execute("SELECT run from cmos order by run DESC limit 1")
    cmos_run = result.fetchone()
    for run in cmos_run:
        run_ = run
    #print data_type, dtype, run_, crate

    result = conn.execute('''SELECT distinct on (run,crate,slot,channel) slot, channel, %s from %s where run = %i and crate = %s order by run,slot,channel''' % (dtype, data_type, run_, crate))

    row = result.fetchall()
    for card,channel,cmos_rate in row:
        data[card*32+channel+12*512] = cmos_rate

    return data
