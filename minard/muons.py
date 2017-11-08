from .db import engine_nl
from .detector_state import get_latest_run

def get_muons(limit, selected_run):
    """
    Returns a list of muon gtids for either
    a run list or a selected run
    """
    conn = engine_nl.connect()

    current_run = get_latest_run()

    if selected_run == 0:
        result = conn.execute("SELECT run, gtids FROM muons where run > %s", \
                              (current_run - limit))
    else:
        result = conn.execute("SELECT run, gtids FROM muons where run = %s", \
                              (selected_run))

    rows = result.fetchall()

    muon_runs = []
    muon_gtids = {}
    for run, gtids in rows:
        muon_runs.append(run)
        muon_gtids[run] = str(gtids)[1:-1]

    return muon_runs, muon_gtids

