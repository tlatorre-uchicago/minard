from .db import engine

def golden_run_list(run_limit, run_range_low, run_range_high):
    '''
    Return a list of run numbers for all gold runs
    '''

    conn = engine.connect()

    # Get the gold list for the over the last (limit) runs, or over a run range
    if not run_range_high:
        result = conn.execute("SELECT DISTINCT ON (run) run FROM evaluated_runs WHERE list = "
                              "(SELECT id FROM run_lists WHERE name = 'gold') AND run > %s ORDER BY run", \
                              (run_limit))
    else:
        result = conn.execute("SELECT DISTINCT ON (run) run FROM evaluated_runs WHERE list = "
                              "(SELECT id FROM run_lists WHERE name = 'gold') AND run >= %s AND run <= %s "
                              " ORDER BY run", (run_range_low, run_range_high))

    rows = result.fetchall()

    gold_runs =  [] 
    for run in rows:
        gold_runs.append(int(run[0]))

    return gold_runs

