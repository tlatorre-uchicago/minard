from .db import engine_nl
from .detector_state import get_latest_run

def get_muons(limit, selected_run, run_range_low, run_range_high, gold):
    """
    Returns a list of muon gtids for either
    a run list or a selected run
    """
    conn = engine_nl.connect()

    current_run = get_latest_run()

    if not selected_run and not run_range_high:
        result_muons = conn.execute("SELECT DISTINCT ON (run) run, gtids, days, secs, nsecs "
                                    "FROM muons where run > %s ORDER BY run DESC, "
                                    "timestamp DESC", (current_run - limit))
        result_missed = conn.execute("SELECT DISTINCT ON (run) run, gtids, days, secs, nsecs "
                                     "FROM missed_muons where run > %s ORDER BY run DESC, "
                                     "timestamp DESC", (current_run - limit))
    elif run_range_high:
        result_muons = conn.execute("SELECT DISTINCT ON (run) run, gtids, days, secs, nsecs "
                                    "FROM muons where run >= %s AND run <= %s ORDER BY run DESC, "
                                    "timestamp DESC", (run_range_low, run_range_high))
        result_missed = conn.execute("SELECT DISTINCT ON (run) run, gtids, days, secs, nsecs "
                                     "FROM missed_muons where run >= %s AND run <= %s ORDER BY run DESC, "
                                     "timestamp DESC", (run_range_low, run_range_high))
    else:
        result_muons = conn.execute("SELECT run, gtids, days, secs, nsecs "
                                    "FROM muons where run = %s", (selected_run))
        result_missed = conn.execute("SELECT run, gtids, days, secs, nsecs "
                                     "FROM missed_muons where run = %s", (selected_run))

    rows_muons = result_muons.fetchall()
    rows_missed = result_missed.fetchall()

    muon_runs = []
    muon = {}
    for run, gtids, days, secs, nsecs in rows_muons:
        if gold !=0 and run not in gold:
            continue
        muon_runs.append(run)
        muon[run] = [gtids, days, secs, nsecs]

    missed_muon_runs = []
    missed_muon = {}
    for run, gtids, days, secs, nsecs in rows_missed:
        if gold !=0 and run not in gold:
            continue
        missed_muon_runs.append(run)
        missed_muon[run] = [gtids, days, secs, nsecs]

    return muon_runs, muon, missed_muon_runs, missed_muon

