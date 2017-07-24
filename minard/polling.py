from .db import engine 

def polling_runs():
    ''' 
    Returns two lists of runs, one where
    CMOS rates were polled using check rates, the other
    where base currents were polled using check rates.
    '''

    conn = engine.connect()

    result = conn.execute("SELECT distinct on (run) run from cmos order by run DESC limit 20")

    if result is not None:
        keys = result.keys()
        rows = result.fetchall()
        cmos_runs = [dict(zip(keys,row)) for row in rows]

    result = conn.execute("SELECT distinct on (run) run from base order by run DESC limit 20")

    if result is not None:
        keys = result.keys()
        rows = result.fetchall()
        base_runs = [dict(zip(keys,row)) for row in rows]

    return cmos_runs, base_runs


def polling_history(crate, slot, channel):
    '''
    Return a list of form [[run number, cmos rate]].
    for all runs with cmos data polling. Also returns
    a list which included statistics on the cmos data.
    '''

    conn = engine.connect()

    result = conn.execute("SELECT run, cmos_rate from cmos WHERE crate = %s \
                           AND slot = %s AND channel = %s ORDER by run DESC" \
                           % (crate, slot, channel))

    if result is None:
        return None, None

    keys = result.keys()
    rows = result.fetchall()

    data = []
    for run, rate in rows:
        data.append([int(run),rate])

    data_stats = []
    if data:
        z = zip(*data)
        data_max = max(z[1])
        data_min = min(z[1])
        data_average = sum(z[1])/(len(z[1]))

        data_std = 0
        for i in range(len(z[1])):
            data_std += (z[1][i] - data_average)**2
        data_std = (data_std/len(z[1]))**(0.5)

        data_stats = [int(data_max), int(data_min), int(data_average), int(data_std)]

    return data, data_stats


def polling_info(data_type, run_number):
    '''
    Returns the polling data for the detector
    '''
 
    conn = engine.connect()

    poll_type = polling_type(data_type)

    # Hold the polling information
    # for the entire detector
    data = [0]*9728

    # Default load the most recent run
    if run_number == 0:
        result = conn.execute("SELECT run FROM %s ORDER by\
                               run DESC limit 1" % data_type)
        if result is None:
            return None
        cmos_run = result.fetchone()
        for run in cmos_run:
            run_number = run

    result = conn.execute("SELECT distinct on (run,crate,slot,channel)\
                           crate, slot, channel, %s FROM %s WHERE run = %i\
                           order by run,crate,slot,channel"\
                           % (poll_type, data_type, run_number))

    if result is None:
        return None

    row = result.fetchall()
    for crate, card, channel, cmos_rate in row:
        lcn = crate*512+card*32+channel
        data[lcn] = cmos_rate

    return data


def polling_info_card(data_type, run_number, crate):
    '''
    Returns the polling data for a crate
    '''

    conn = engine.connect()

    poll_type = polling_type(data_type)

    # Hold the polling information
    # for a single crate
    data = [0]*512

    # Default load the most recent run
    if run_number == 0:
        result = conn.execute("SELECT run FROM %s ORDER by\
                               run DESC limit 1" % data_type)
        if result is None:
            return None
        cmos_run = result.fetchone()
        for run in cmos_run:
            run_number = run

    result = conn.execute("SELECT distinct on (run,crate,slot,channel)\
                           slot, channel, %s FROM %s WHERE run = %i\
                           and crate = %s ORDER by run,slot,channel"\
                           % (poll_type, data_type, run_number, crate))

    if result is None:
        return None

    row = result.fetchall()
    for card, channel, cmos_rate in row:
        data[card*32+channel] = cmos_rate

    return data


def polling_type(data_type):

    if data_type == "cmos":
        return "cmos_rate"
    elif data_type == "base":
        return "base_current"
    else:
        return None

