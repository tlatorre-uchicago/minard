import couchdb
from .db import engine 
from .db import engine2

def polling_runs():

    conn = engine2.connect()
    result = conn.execute("SELECT distinct on (run) run from cmos order by run DESC limit 20")

    keys = result.keys()
    rows = result.fetchall()
    cmos_runs = [dict(zip(keys,row)) for row in rows]

    result = conn.execute("SELECT distinct on (run) run from base order by run DESC limit 20")

    keys = result.keys()
    rows = result.fetchall()
    base_runs = [dict(zip(keys,row)) for row in rows]

    return cmos_runs, base_runs

def polling_info(data_type, run_number):

    dtype = ""
    if data_type == "cmos":
       dtype = "cmos_rate"
    if data_type == "base":
       dtype = "base_current"

    data = [0]*9728
    conn = engine2.connect()

    if run_number == 0:
        result = conn.execute("SELECT run from %s order by run DESC limit 1" % data_type)
        cmos_run = result.fetchone()
        for run in cmos_run:
            run_number = run

    result = conn.execute('''SELECT distinct on (run,crate,slot,channel) crate, slot, channel, %s from %s where run = %i order by run,crate,slot,channel''' % (dtype, data_type, run_number))

    row = result.fetchall()
    for crate,card,channel,cmos_rate in row:
        lcn = crate*512+card*32+channel
        data[lcn] = cmos_rate

    return data

def polling_info_card(data_type, run_number, crate):

    if data_type == "cmos":
       dtype = "cmos_rate"
    if data_type == "base":
       dtype = "base_current"

    data = [0]*6656
    conn = engine2.connect()

    if run_number == 0:
        result = conn.execute("SELECT run from %s order by run DESC limit 1" % data_type)
        cmos_run = result.fetchone()
        for run in cmos_run:
            run_number = run

    result = conn.execute('''SELECT distinct on (run,crate,slot,channel) slot, channel, %s from %s where run = %i and crate = %s order by run,slot,channel''' % (dtype, data_type, run_number, crate))

    row = result.fetchall()
    for card,channel,cmos_rate in row:
        data[card*32+channel+12*512] = cmos_rate

    return data
