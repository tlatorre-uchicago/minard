import couchdb
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


def polling_check(high_rate, low_rate):

    #PMT Type defines
    LOWG     = 0x21
    NONE     = 0x0
    NECK     = 0x9
    FECD     = 0x10
    BUTT     = 0x81

    conn = engine.connect()

    result = conn.execute("SELECT run from cmos ORDER by timestamp DESC limit 1")

    run_number = [0]*2
    row = result.fetchone()
    for run in row:
        run_number[0] = run 

    result = conn.execute("SELECT run from cmos WHERE run != %s ORDER by\
                           timestamp DESC limit 1", run_number[0])

    row = result.fetchone()
    for run in row:
        run_number[1] = run

    data_run1 = [0]*9728
    data_run2 = [0]*9728

    result = conn.execute("SELECT crate, slot, channel, cmos_rate, run from cmos WHERE \
                           run = %s or run = %s", (run_number[0], run_number[1]))

    rows = result.fetchall()
    for crate, slot, channel, cmos_rate, run in rows:
        lcn = crate*512+slot*32+channel
        if run == run_number[0]:
            data_run1[lcn] = cmos_rate
        elif run == run_number[1]:
            data_run2[lcn] = cmos_rate

    relays = relay_status(conn)
    types = pmt_type(conn)
    pulled_resistor = channel_information(conn, "resistor_pulled")
    low_occ = channel_information(conn, "low_occupancy")
    zero_occ = channel_information(conn, "zero_occupancy")
    bad_disc = channel_information(conn, "bad_discriminator")

    cmos_changes = []
    cmos_high_rates = []
    cmos_low_rates = []

    for crate in range(19):
        for slot in range(16):
            for channel in range(32):
                lcn = crate*512+slot*32+channel
                hv_relay_mask = relays[crate][1] << 32 | relays[crate][0]
                if not(hv_relay_mask & (1 << (slot*4 + (3-channel//8)))):
                    continue
                if types[lcn] == LOWG or \
                   types[lcn] == NECK or \
                   types[lcn] == FECD or \
                   types[lcn] == BUTT or \
                   types[lcn] == NONE:
                    continue
                if pulled_resistor[lcn] == 1:
                    continue
                if(data_run1[lcn] > 50 and data_run2[lcn] > 50):
                    change1 = 100*((data_run2[lcn] - data_run1[lcn])/data_run1[lcn])
                    change2 = 100*((data_run1[lcn] - data_run2[lcn])/data_run2[lcn])
                    if change1 > 100 or change2 > 100:
                        cmos_changes.append("%i/%i/%i: %i Hz to %i Hz" %\
                            (crate, slot, channel, data_run1[lcn], data_run2[lcn]))
                if(data_run1[lcn] > high_rate):
                    cmos_high_rates.append("%i/%i/%i: %i Hz" %\
                            (crate, slot, channel, data_run1[lcn]))
                elif(data_run2[lcn] > high_rate):
                    cmos_high_rates.append("%i/%i/%i: %i Hz" %\
                            (crate, slot, channel, data_run2[lcn]))
                if not (low_occ[lcn] or zero_occ[lcn] or bad_disc[lcn]):
                    if(data_run1[lcn] < low_rate):
                        cmos_low_rates.append("%i/%i/%i: %i Hz" %\
                                (crate, slot, channel, data_run1[lcn]))
                    elif(data_run2[lcn] < low_rate):
                        cmos_low_rates.append("%i/%i/%i: %i Hz" %\
                                (crate, slot, channel, data_run2[lcn]))

    return cmos_changes, cmos_high_rates, cmos_low_rates, run_number


def pmt_type(conn):
    """ Get the PMT types """

    types = [0]*9728
    sql_result = conn.execute('''SELECT crate, slot, channel, type from pmt_info \
                                 order by crate, slot, channel''')

    sql_result = sql_result.fetchall()
    for crate, slot, channel, pmttype in sql_result:
        lcn = crate*512 + slot*32 + channel
        types[lcn] = pmttype

    return types


def channel_information(conn, status):
    """ Get the channel status for a status string (ie, "pulled resistor") """

    channel_info = [0]*9728
    sql_result = conn.execute('''select crate,slot,channel,%s from channel_status group by \
                                 (crate,slot,channel,%s) order by crate,slot,channel,MAX(timestamp)''' \
                                 % (status,status))

    sql_result = sql_result.fetchall()
    for crate,slot,channel,info in sql_result:
        lcn = crate*512+slot*32+channel
        channel_info[lcn] = int(info)

    return channel_info


def relay_status(conn):

    relays = []
    result = conn.execute("select hv_relay_mask1, hv_relay_mask2 from\
                               current_crate_state order by crate")

    rows = result.fetchall()

    for hv_relay_mask1, hv_relay_mask2 in rows:
        relays.append([hv_relay_mask1, hv_relay_mask2])

    return relays

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

