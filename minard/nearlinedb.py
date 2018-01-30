from .db import engine_nl

def get_nearline_status(run):
    """
    Get all the nearline jobs and their
    statuses for a given run
    """
    conn = engine_nl.connect()

    result = conn.execute("SELECT name, status FROM nearline WHERE run = %s "
                          "ORDER BY timestamp ASC", run)

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

def job_types():
    """
    Get all of the nearline job types
    """
    conn = engine_nl.connect()

    result = conn.execute("SELECT DISTINCT ON (name) name FROM nearline "
                          "ORDER BY name DESC")
    rows = result.fetchall()

    names = []
    names.append("All")
    names.append("Critical")
    for name in rows:
        names.append(str(name[0]))

    return names

def get_failed_runs(run, run_range_low=0, run_range_high=0):
    """
    Get all failed runs after a given runnumber or over a run range
    """
    conn = engine_nl.connect()

    if run_range_high:
        result = conn.execute("SELECT run, name, status FROM nearline WHERE "
                              "run >= %s AND run <= %s ORDER BY run DESC, timestamp ASC ",
                              (run_range_low, run_range_high,))
    else:
        result = conn.execute("SELECT run, name, status FROM nearline WHERE "
                              "run >= %s ORDER BY run DESC, timestamp ASC ",
                              (run,))
    rows = result.fetchall()

    # First create a map of most recent statuses
    job_status = {}
    for run, name, status in rows:
        job_status[(run, name)] = status

    # Keep track of runs that returned a failure code
    failed = [-1, 1, 2, 3, 97, 98]
    failed_map = {}
    for run, name, status in rows:
        if job_status[(run, name)] in failed and status in failed:
            try:
                failed_map[run].append((str(name), int(status)))
            except KeyError:
                failed_map[run] = [(str(name), int(status))]

    failed_runs = failed_map.keys()
    failed_runs = sorted(failed_runs, reverse=True)

    return failed_runs, failed_map
