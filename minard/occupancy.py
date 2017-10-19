from .db import engine_test
from .detector_state import get_latest_run

def occupancy_by_trigger(trigger_type, run, find_issues):

    conn = engine_test.connect()

    result = conn.execute("SELECT DISTINCT ON (run, crate, slot, channel, trigger_bit) "
                          "crate, slot, channel, trigger_norm, occupancy "
                          "FROM trigger_occupancy WHERE trigger_bit = %s AND run = %s "
                          "ORDER BY run, crate, slot, channel, trigger_bit ", \
                          (trigger_type, run))

    rows = result.fetchall()

    data = [0]*9728
    trigger_norm = 0
    for crate, slot, channel, norm, occupancy in rows:
        lcn = crate*512 + slot*32 + channel
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

    conn = engine_test.connect()

    current_run = get_latest_run()

    result = conn.execute("SELECT DISTINCT ON (run) run FROM trigger_occupancy "
                          "WHERE run > %s ORDER BY run DESC", (current_run - limit))

    rows = result.fetchall()
    runs = []
    for run in rows:
        runs.append(run[0])

    return runs


def check_occupancy(trigger_type, data, norm):

    # Fixme do slot average
    slot_average = [0.0]*304
    channel_count = [32.0]*304

    for i in range(len(data)):

        crate = i/512
        card = (i%512)/32
        lcn = card + 16*crate

        if data[i] < 0:
            channel_count[lcn] -= 1
            continue

        slot_average[lcn] += data[i]

    issues = []
    for i in range(304):
        crate = i/16
        slot = i%16
        if channel_count[i] != 0 and slot_average[i]/(channel_count[i]) < 4e-5:
            print i, crate, slot, slot_average[i], channel_count[i], slot_average[i]/(channel_count[i])
            issues.append((crate, slot))

    return issues

