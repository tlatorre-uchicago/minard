from .db import engine_nl
from .detector_state import get_latest_run

def occupancy_by_trigger(trigger_type, run, find_issues):
    """
    Returns a list specifing the normalized occupancy
    for the trigger type. Pass the find_issues flag
    to look for issues with the occupancy
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

    if find_issues:
        issues = check_occupancy(trigger_type, data, norm)
        return issues

    return data


def run_list(limit):
    """
    Get a list of runs where the trigger
    occupancy job ran.
    """
    conn = engine_nl.connect()

    current_run = get_latest_run()

    result = conn.execute("SELECT DISTINCT ON (run) run FROM trigger_occupancy "
                          "WHERE run > %s ORDER BY run DESC", (current_run - limit))

    rows = result.fetchall()
    runs = []
    for run in rows:
        runs.append(run[0])

    return runs


def check_occupancy(trigger_type, data, norm):
    """
    Check the occupancy of each slot against a 
    hard-coded value that was determined by 
    looking at runs where slots had tripped off
    and runs where the crate was missing its
    ESUMH trigger. Returns a dictionary of issues
    with the crate as keys and slots as values.
    """
    BAD_OCC = 3e-5

    slot_average = [0.0]*304
    channel_count = [32.0]*304

    for i in range(len(data)):
        crate = i/512
        card = (i%512)/32
        lcn = card + 16*crate
        # These are offline channels, flagged
        # by PMTCal selector
        if data[i] < 0:
            channel_count[lcn] -= 1
            continue
        slot_average[lcn] += data[i]

    issues = {}
    for i in range(304):
        crate = i/16
        slot = i%16
        if channel_count[i] != 0 and slot_average[i]/(channel_count[i]) < BAD_OCC:
            try:
                issues[crate].append(slot)
            except Exception:
                issues[crate] = [slot]

    return issues

