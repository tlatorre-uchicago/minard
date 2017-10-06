from .db import engine
from detector_state import get_latest_run
from polling import overall_status
import HLDQTools
from pingcratesdb import ping_crates_list

def get_run_list(limit, selected_run):

    conn = engine.connect()

    if selected_run == 0:
        # If not selected run, list all runs since latest run - limit
        run = get_latest_run()
        result = conn.execute("SELECT run FROM run_state "
                              "WHERE run > %s AND (run_type & 4 = 4)", run - limit)
        ping_list = ping_crates_list(limit)
    else:
        # Make sure selected run is a physics run
        result = conn.execute("SELECT run FROM run_state "
                              "WHERE run = %s AND (run_type & 4 = 4)", selected_run)
        if result is None:
           return None 
        ping_list = ping_crates_list(limit)

    rows = result.fetchall()

    physics_runs = []
    for run in rows:
        physics_runs.insert(0, run[0])

    # Check rates failures
    check_rates_fail = overall_status(physics_runs)

    ping_crates_fail = ping_failures(ping_list)

    #run_info = []
    #i = 0
    #for run in physics_runs:
    #    run_info.append(HLDQTools.import_HLDQ_ratdb(int(run)))
    #    testing = HLDQTools.generateHLDQProcStatus(run_info[i])
    #    print testing
    #    i+=1

    return physics_runs, check_rates_fail, ping_crates_fail

def ping_failures(ping_list):

    ping_failure = {}
    for i in ping_list:
        if i[6] == "Fail":
            run = int(i[1])
            ping_failure[run] = 1

    return ping_failure
