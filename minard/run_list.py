from .db import engine

def run_list():
    '''
    Select all gold runs
    '''

    conn = engine.connect()

    result = conn.execute("SELECT DISTINCT ON (run) run FROM evaluated_runs WHERE list = "
                          "(SELECT id FROM run_lists WHERE name = 'gold') ORDER BY run")

    rows = result.fetchall()

    gold_runs =  [] 
    for run in rows:
        gold_runs.append(run)

    return gold_runs

