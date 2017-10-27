from .db import engine
from .detector_state import get_latest_run
from .pingcratesdb import ping_crates_list
from .channelflagsdb import get_channel_flags
from .triggerclockjumpsdb import get_clock_jumps
from .nlrat import RUN_TYPES
from .occupancy import run_list, occupancy_by_trigger

def get_run_list(limit, selected_run, all_runs):
    '''
    Returns dictionaries keeping track of a list
    of failures for each nearline job
    '''
    conn = engine.connect()

    ping_list = ping_crates_list(limit)
    ping_crates_fail = {}
    ping_runs = []
    for i in ping_list:
        run = int(i[1])
        ping_runs.append(run)
        if i[6] == 1:
            ping_crates_fail[run] = 1
        elif i[6] == 0:
            ping_crates_fail[run] = 0
        elif i[6] == 2:
            ping_crates_fail[run] = 2
    for run in all_runs:
        if run in ping_runs:
            continue
        ping_crates_fail[run] = -1

    runs, nsync16, nsync24, count_sync16, count_sync24, count_missed = get_channel_flags(limit)
    channel_flags_fail = {}
    for run in all_runs:
        run = int(run)
        try:
            if((count_sync16[run] >= 32 and count_sync16[run] < 64) or \
                count_missed[run] >= 64 and count_missed[run] < 256):
                channel_flags_fail[run] = 2
            elif(count_sync16[run] >= 64 or count_missed[run] >= 256):
                channel_flags_fail[run] = 1
            else:
                channel_flags_fail[run] = 0
        except Exception as e:
            channel_flags_fail[run] = -1
            continue

    clock_jumps_fail = {}
    runs, njump10, njump50 = get_clock_jumps(limit) 
    for run in all_runs:
        try:
            if((njump10[run] + njump50[run]) >= 10 and \
               (njump10[run] + njump50[run]) < 20):
                clock_jumps_fail[run] = 2
            elif(njump10[run] + njump50[run] >= 20):
                clock_jumps_fail[run] = 1
            else:
                clock_jumps_fail[run] = 0
        except Exception as e:
            clock_jumps_fail[run] = -1
            continue

    occupancy_fail = {}
    runs = run_list(limit) 
    for run in all_runs:
        try:
            # Check ESUMH Occupancy
            issues = occupancy_by_trigger(6, run, True)
            count_slots = 0
            # If more than one slot has an issue
            for i in issues:
                for j in issues[i]:
                    count_slots+=1
            if count_slots > 1:
                occupancy_fail[run] = 1
            else:
                occupancy_fail[run] = 0
        except Exception as e:
            occupancy_fail[run] = -1
            continue

    return clock_jumps_fail, ping_crates_fail, channel_flags_fail, occupancy_fail


def get_run_types(limit):
    '''
    Return a dictionary of run types for each run in the list
    '''
    conn = engine.connect()

    latest_run = get_latest_run()

    result = conn.execute("SELECT run, run_type FROM run_state WHERE run > %s", (latest_run - limit))

    rows = result.fetchall()

    runtypes = {}
    for run, run_type in rows:
        for i in range(len(RUN_TYPES)):
            if (run_type & (1<<i)):
                runtypes[run] = RUN_TYPES[i]
                break

    return runtypes

