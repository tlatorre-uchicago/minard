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
                          "FROM channel_flags WHERE run > %i "
                          "ORDER BY run DESC, timestamp DESC" % (current_run - limit))

    rows = result.fetchall()

    runs = []
    nsync16 = {}
    nsync24 = {}
    count_sync16 = {}
    count_sync24 = {}
    count_missed = {}

    for run, sync16, sync24 in rows:
        runs.append(run)
        nsync16[run] = sync16
        nsync24[run] = sync24     

        count_sync16[run] = 0
        count_sync24[run] = 0
        count_missed[run] = 0

    result = conn.execute("SELECT DISTINCT ON (crate, slot, channel, run) run, crate, "
                          "cmos_sync16, cgt_sync24, missed_count FROM channel_flags "
                          "WHERE run > %i ORDER BY crate, slot, channel, run DESC, timestamp DESC" \
                          % int(current_run - limit))

    rows = result.fetchall()

    for run, crate, cmos_sync16, cgt_sync24, missed_count in rows:
        if crate == -1:
            continue
        if cmos_sync16 != 0:
            count_sync16[run] += 1
        if cgt_sync24 != 0:
            count_sync24[run] += 1
        if missed_count != 0:
            count_missed[run] += 1

    return runs, nsync16, nsync24, count_sync16, count_sync24, count_missed


def get_channel_flags_by_run(run):
    """
    Returns a list of the missed count and out-of-sync channels
    for a requested run
    """
    conn = engine_nl.connect()

    # Find all of the out-of-sync and missed-count channels for the run selected
    result = conn.execute("SELECT DISTINCT ON (crate, slot, channel) crate, slot, channel, "
                          "cmos_sync16, cgt_sync24, missed_count FROM channel_flags "
                          "WHERE run = %i ORDER BY crate, slot, channel, run DESC, timestamp DESC" \
                          % int(run))

    rows = result.fetchall()

    list_sync16 = []
    list_sync24 = []
    list_missed = []

    for crate, slot, channel, sync16, sync24, missed in rows:
        if crate == -1:
            continue
        if missed != 0:
            list_missed.append((crate, slot, channel, missed))
        if sync16 != 0:
            list_sync16.append((crate, slot, channel, sync16))
        if sync24 != 0:
            list_sync24.append((crate, slot, channel, sync24))

    list_sync16_pr = []
    list_sync24_pr = []

    # Now try and find out of sync channels identified in later runs
    try:
        result = conn.execute("SELECT run FROM channel_flags WHERE run > %i and sync16 > 0 "
                              "ORDER by run ASC, timestamp DESC limit 1" % int(run))
        if result is None:
            sync16run = run + 1
        else:
            sync16run = result.fetchone()[0]

        result = conn.execute("SELECT run FROM channel_flags WHERE run > %i and sync24 > 0 "
                              "ORDER by run ASC, timestamp DESC limit 1" % int(run))
        if result is None:
            sync24run = run + 1
        else:
            sync24run = result.fetchone()[0]

        result = conn.execute("SELECT DISTINCT ON (crate, slot, channel) crate, slot, channel, "
                              "cmos_sync16_pr FROM channel_flags "
                              "WHERE run = %i and sync16 > 0 "
                              "ORDER by crate, slot, channel, run DESC, timestamp DESC" \
                              % int(sync16run))
        rows = result.fetchall()

        for crate, slot, channel, cmos_sync16_pr in rows:
            if cmos_sync16_pr != 0:
                list_sync16_pr.append((crate, slot, channel, cmos_sync16_pr))

        result = conn.execute("SELECT DISTINCT ON (crate, slot, channel) crate, slot, channel, "
                              "cgt_sync24_pr FROM channel_flags "
                              "WHERE run = %i and sync24 > 0 "
                              "ORDER by crate, slot, channel, run DESC, timestamp DESC" \
                              % int(sync24run))
        rows = result.fetchall()

        for crate, slot, channel, cgt_sync24_pr in rows:
            if cgt_sync24_pr != 0:
                list_sync24_pr.append((crate, slot, channel, cgt_sync24_pr))

    except Exception as e:
        pass

    return list_missed, list_sync16, list_sync24, list_sync16_pr, list_sync24_pr
 
