from .db import engine_nl
from .detector_state import get_latest_run

def occupancy_by_trigger_limit(limit, selected_run):
    """
    Returns a dictionary of the ESUMH occupacy status
    indexed by run
    """
    conn = engine_nl.connect()

    latest_run = get_latest_run()

    if selected_run == 0:
        result = conn.execute("SELECT DISTINCT ON (run, crate, slot) "
                              "run, status, crate, slot "
                              "FROM esumh_occupancy_fail WHERE run > %s "
                              "ORDER BY run, crate, slot", \
                              (latest_run - limit))
    else:
        result = conn.execute("SELECT DISTINCT ON (run, crate, slot) "
                              "run, status, crate, slot "
                              "FROM esumh_occupancy_fail WHERE run = %s "
                              "ORDER BY run, crate, slot", \
                              (selected_run))

    rows = result.fetchall()

    crates = {}
    slots = {}
    status = {}
    count = {}
    for run, run_status, crate, slot in rows:
        status[run] = run_status
        if run_status == 0:
            crates[run] = "None"
            slots[run] = "None"
            count[run] = 0
            continue
        try:
            if crate != crates[run][-1]:
                crates[run].append(crate)
        except Exception as e:
            crates[run] = [crate]
        try:
            slots[run].append(slot)
            count[run]+=1
        except Exception as e:
            slots[run] = [slot]
            count[run] = 1

    return status, crates, slots, count
 

def occupancy_by_trigger(trigger_type, run, find_issues):
    """
    Returns a list specifing the normalized occupancy
    for the trigger type.
    """
    conn = engine_nl.connect()

    result = conn.execute("SELECT DISTINCT ON (run, lcn, trigger_bit) "
                          "lcn, trigger_norm, occupancy "
                          "FROM trigger_occupancy WHERE trigger_bit = %s AND run = %s "
                          "ORDER BY run, lcn, trigger_bit ", \
                          (trigger_type, run))

    rows = result.fetchall()

    if not rows:
        return None

    data = [0]*9728
    trigger_norm = 0
    for lcn, norm, occupancy in rows:
        trigger_norm = norm
        data[lcn] = occupancy

    if trigger_norm == 0:
        data = [0]*9728
        return data

    data = [float(x) / trigger_norm for x in data]

    return data


def run_list(limit):
    """
    Get a list of runs where the trigger
    occupancy job ran.
    """
    conn = engine_nl.connect()

    current_run = get_latest_run()

    result = conn.execute("SELECT DISTINCT ON (run) run FROM esumh_occupancy_fail "
                          "WHERE run > %s ORDER BY run DESC", (current_run - limit))

    rows = result.fetchall()
    runs = []
    for run in rows:
        runs.append(run[0])

    return runs


