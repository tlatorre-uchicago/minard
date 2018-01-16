from .db import engine_nl

def get_nearline_status(run):
    """
    Get all the nearline jobs and their
    statuses for a given run
    """
    conn = engine_nl.connect()

    result = conn.execute("SELECT name, status FROM nearline WHERE run = %s ORDER BY timestamp ASC", run)

    rows = result.fetchall()

    programs = {}
    for name, status in rows:
        programs[name] = status

    return programs

def current_run():
    """
    Get the current run from the PSQL database
    """
    conn = engine_nl.connect()

    result = conn.execute("SELECT run from current_nearline_run")
    run = result.fetchone()[0]

    return run

