from .db import engine_nl
from .detector_state import get_latest_run
import time

TZERO = 14610*24*3600

def get_muons(limit, selected_run, run_range_low, run_range_high, gold):
    """
    Returns a list of muon gtids for either
    a run list or a selected run
    """
    conn = engine_nl.connect()

    if not selected_run and not run_range_high:
        current_run = get_latest_run()
        result_muons = conn.execute("SELECT DISTINCT ON (run) run, array_length(gtids, 1), "
                                    "gtids, days, secs, nsecs "
                                    "FROM muons where run > %s ORDER BY run DESC, "
                                    "timestamp DESC", (current_run - limit))
        result_missed = conn.execute("SELECT DISTINCT ON (run) run, array_length(gtids, 1) "
                                     "FROM missed_muons where run > %s ORDER BY run DESC, "
                                     "timestamp DESC", (current_run - limit))
    elif run_range_high:
        result_muons = conn.execute("SELECT DISTINCT ON (run) run, array_length(gtids, 1), "
                                    "gtids, days, secs, nsecs "
                                    "FROM muons where run >= %s AND run <= %s ORDER BY run DESC, "
                                    "timestamp DESC", (run_range_low, run_range_high))
        result_missed = conn.execute("SELECT DISTINCT ON (run) run, array_length(gtids, 1) "
                                     "FROM missed_muons where run >= %s AND run <= %s ORDER BY run DESC, "
                                     "timestamp DESC", (run_range_low, run_range_high))
    else:
        result_muons = conn.execute("SELECT run, array_length(gtids, 1), gtids, days, secs, nsecs "
                                    "FROM muons where run = %s", (selected_run))
        result_missed = conn.execute("SELECT run, array_length(gtids, 1) "
                                     "FROM missed_muons where run = %s", (selected_run))

    rows_muons = result_muons.fetchall()
    rows_missed = result_missed.fetchall()

    muon_runs = []
    muon_count = {}
    muon_fake = {}
    livetime_lost = {}
    for run, count, gtids, days, secs, nsecs in rows_muons:
        if gold !=0 and run not in gold:
            continue
        muon_runs.append(run)
        muon_count[run] = count
        if gtids and gtids[0] == -1:
            muon_fake[run] = 1
        livetime = []
        # Count the livetime lost to muons by run, accounting for overlap
        for t in range(len(days)):
            time = days[t]*24*3600 + secs[t] + float(nsecs[t])/1e9
            livetime.append(time)
            if t == 0:
                livetime_lost[run] = 20
            elif(livetime[t] > livetime[t-1] + 20):
                livetime_lost[run] += 20
            else:
                livetime_lost[run] += int((livetime[t] - livetime[t-1]))

    missed_muon_runs = []
    missed_muon_count = {}
    for run, count in rows_missed:
        if gold !=0 and run not in gold:
            continue
        missed_muon_runs.append(run)
        missed_muon_count[run] = count

    return muon_runs, muon_count, muon_fake, missed_muon_runs, missed_muon_count, livetime_lost


def get_muon_info_by_run(selected_run):
    '''
    Get the GTID and time for each identified muon in the run
    '''
    conn = engine_nl.connect()

    result_muons = conn.execute("SELECT run, gtids, days, secs, nsecs "
                                "FROM muons where run = %s", (selected_run))
    result_missed = conn.execute("SELECT run, gtids, days, secs, nsecs "
                                 "FROM missed_muons where run = %s", (selected_run))

    rows_muons = result_muons.fetchall()
    rows_missed = result_missed.fetchall()

    muon_runs = []
    muon = {}
    for run, gtids, days, secs, nsecs in rows_muons:
        t_array = []
        muon_runs.append(run)
        for t in range(len(days)):
            total_secs = TZERO + days[t]*24*3600 + secs[t] + float(nsecs[t])/1e9
            stime = time.strftime("%a, %d %b %Y %H:%M:%S ", time.gmtime(total_secs))
            t_array.append(stime)
        muon[run] = [gtids, t_array]

    missed_muon_runs = []
    missed_muon = {}
    for run, gtids, days, secs, nsecs in rows_missed:
        t_array = []
        for t in range(len(days)):
            total_secs = TZERO + days[t]*24*3600 + secs[t] + float(nsecs[t])/1e9
            stime = time.strftime("%a, %d %b %Y %H:%M:%S ", time.gmtime(total_secs))
            t_array.append(stime)
        missed_muon_runs.append(run)
        missed_muon[run] = [gtids, t_array]

    return muon_runs, muon, missed_muon_runs, missed_muon
