from .db import engine_nl
from .detector_state import get_latest_run

def get_channel_flags(limit):
    """
    Returns a list of runs and 5 dictionaries using the run number as the keys.
    The dictionaries keep track of the number of sync16s, number of syn24s,
    number of out-of-sync channels, and number of missed count channels.
    """
    conn = engine_nl.connect()

    current_run = get_latest_run()

    result = conn.execute("SELECT DISTINCT ON (run) run, sync16, sync24 "
                          "FROM channel_flags WHERE run > %s "
                          "ORDER BY run DESC, timestamp DESC", (current_run - limit))

    rows = result.fetchall()

    runs = []
    nsync16 = {}
    nsync24 = {}
    count_sync16 = {}
    count_sync24 = {}
    count_missed = {}
    count_sync16_pr = {}
    count_sync24_pr = {}

    for run, sync16, sync24 in rows:
        runs.append(run)
        nsync16[run] = sync16
        nsync24[run] = sync24     

        count_sync16[run] = 0
        count_sync24[run] = 0
        count_missed[run] = 0
        count_sync16_pr[run] = 0
        count_sync24_pr[run] = 0

    result = conn.execute("SELECT DISTINCT ON (crate, slot, channel, run) run, "
                          "cmos_sync16, cgt_sync24, missed_count, cmos_sync16_pr, "
                          "cgt_sync24_pr FROM channel_flags "
                          "WHERE run > %s ORDER BY crate, slot, channel, run DESC, timestamp DESC", \
                          int(current_run - limit))

    rows = result.fetchall()

    for run, cmos_sync16, cgt_sync24, missed_count, cmos_sync16_pr, cgt_sync24_pr in rows:
        if cmos_sync16 != 0 and cmos_sync16 is not None:
            count_sync16[run] += 1
        if cgt_sync24 != 0 and cgt_sync24 is not None:
            count_sync24[run] += 1
        if missed_count != 0 and missed_count is not None:
            count_missed[run] += 1
        if cmos_sync16_pr != 0 and cmos_sync16_pr is not None:
            count_sync16_pr[run] += 1
        if cgt_sync24_pr != 0 and cgt_sync24_pr is not None:
            count_sync24_pr[run] += 1

    return runs, nsync16, nsync24, count_sync16, count_sync24, count_missed, count_sync16_pr, count_sync24_pr


def get_channel_flags_by_run(run):
    """
    Returns a list of the missed count and out-of-sync channels
    for a requested run
    """
    conn = engine_nl.connect()

    # Find all of the out-of-sync and missed-count channels for the run selected
    result = conn.execute("SELECT DISTINCT ON (crate, slot, channel) crate, slot, channel, "
                          "cmos_sync16, cgt_sync24, missed_count, cmos_sync16_pr, "
                          "cgt_sync24_pr FROM channel_flags "
                          "WHERE run = %s ORDER BY crate, slot, channel, run DESC, timestamp DESC", \
                          int(run))

    rows = result.fetchall()

    list_sync16 = []
    list_sync24 = []
    list_missed = []
    list_sync16_pr = []
    list_sync24_pr = []

    for crate, slot, channel, sync16, sync24, missed, sync16_pr, sync24_pr in rows:
        if missed != 0 and missed is not None:
            list_missed.append((crate, slot, channel, missed))
        if sync16 != 0 and sync16 is not None:
            list_sync16.append((crate, slot, channel, sync16))
        if sync24 != 0 and sync24 is not None:
            list_sync24.append((crate, slot, channel, sync24))
        if sync16_pr != 0 and sync16_pr is not None:
            list_sync16_pr.append((crate, slot, channel, sync16_pr))
        if sync24_pr != 0 and sync24_pr is not None:
            list_sync24_pr.append((crate, slot, channel, sync24_pr))

    return list_missed, list_sync16, list_sync24, list_sync16_pr, list_sync24_pr


def get_number_of_syncs(run):
    '''
    Get the number of sync16 and sync24s in a selected run
    '''

    conn = engine_nl.connect()

    result = conn.execute("SELECT run, sync16, sync24 FROM channel_flags "
                          "WHERE run = %s ORDER BY timestamp DESC limit 1", (run))

    rows = result.fetchall()

    nsync16s = -1
    nsync24s = -1
    for run, sync16, sync24 in rows:
        nsync16s = sync16
        nsync24s = sync24

    return nsync16s, nsync24s

