from .db import engine
from .detector_state import get_latest_run

def golden_run_list(limit, run_range_low, run_range_high):
    '''
    Return a list of run numbers for all gold runs
    '''
    conn = engine.connect()

    # Get the gold list for the over a set of runs
    if not run_range_high:
        latest_run = get_latest_run()
        result = conn.execute("SELECT DISTINCT ON (run) run FROM evaluated_runs WHERE list = "
                              "(SELECT id FROM run_lists WHERE name = 'gold') AND run > %s ORDER BY run", \
                              (latest_run - limit))
    else:
        result = conn.execute("SELECT DISTINCT ON (run) run FROM evaluated_runs WHERE list = "
                              "(SELECT id FROM run_lists WHERE name = 'gold') AND run >= %s AND run <= %s "
                              " ORDER BY run", (run_range_low, run_range_high))

    rows = result.fetchall()

    gold_runs =  [] 
    for run in rows:
        gold_runs.append(int(run[0]))

    return gold_runs

