from .db import engine
from detector_state import get_latest_run
from polling import overall_status
import HLDQTools
from pingcratesdb import ping_crates_list
from channelflagsdb import get_channel_flags
from triggerclockjumpsdb import get_clock_jumps

def get_run_list(limit, selected_run):

    conn = engine.connect()

    if selected_run == 0:
        # If not selected run, list all runs since latest run - limit
        run = get_latest_run()
        result = conn.execute("SELECT run FROM run_state "
                              "WHERE run > %s AND (run_type & 4 = 4)", run - limit)

    else:
        # Make sure selected run is a physics run
        result = conn.execute("SELECT run FROM run_state "
                              "WHERE run = %s AND (run_type & 4 = 4)", selected_run)
        if result is None:
           return None

    rows = result.fetchall()

    # Grab the recent physics runs or the selected runs
    physics_runs = []
    for run in rows:
        physics_runs.insert(0, run[0])

    # FIXME how does this work for selected run??
    ping_list = ping_crates_list(limit)
    runs, nsync16, nsync24, count_sync16, count_sync24, count_missed = get_channel_flags(limit)

    check_rates_fail = []

    ping_crates_fail = ping_failures(ping_list)

    # FIXME make a function
    channel_flags_fail = {}
    for run in physics_runs:
       run = int(run)
       try:
           if((count_sync16[run] > 25 and count_sync16[run] <= 100) or count_missed[run] > 100):
               channel_flags_fail[run] = 2
           elif(count_sync16[run] > 100):
               channel_flags_fail[run] = 1
           else:
               channel_flags_fail[run] = 0
       except Exception as e:
           channel_flags_fail[run] = -1
           continue

    # THIS IS SO SLOW, because it requires so many PSQL queries
    # check_rates_fail = overall_status(physics_runs)

    return physics_runs, check_rates_fail, ping_crates_fail, channel_flags_fail


def ping_failures(ping_list):

    ping_failure = {}
    for i in ping_list:
        if i[6] == "Fail":
            run = int(i[1])
            ping_failure[run] = 1

    return ping_failure
