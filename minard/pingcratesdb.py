from .db import engine
from .detector_state import get_latest_run, get_mtc_state_for_run

def crates_failed(run): 
    '''
    Check the ping crates information for failures and potential
    MTCA/+ relay mapping information. Returns four strings for
    display on the monitoring website
    '''

    mtc = get_mtc_state_for_run(run)

    # MTCA/+ relays for the run
    mtca_relays = mtc['mtca_relays']
    n100_relay = mtca_relays[0]
    n20_relay = mtca_relays[1]

    conn = engine.connect()

    # Get ping crates information from detector state
    result = conn.execute("SELECT DISTINCT ON (run) n100_crates_failed, n20_crates_failed " 
                          "FROM ping_crates "
                          "WHERE run = %s", run)

    n100_failed = []
    n20_failed = []
    n100_str = ""
    n20_str = ""

    # Find any failures (not warnings)
    for n100, n20 in result.fetchall():
        for i in n100:
            if i < 20:
                n100_failed.append(i)
                n100_str+=str(i)+", "
        for i in n20:
            if i < 20: # warnings are > 20
                n20_failed.append(i)
                n20_str+=str(i)+", "

    mismapped_n100 = ""
    mismapped_n20 = ""
    removed_crate_n100 = []
    removed_crate_n20 = []

    # List of crates out of the MTCA/+ relay mask
    for crate in range(20):
        if not ((1<<crate) & n100_relay):
            removed_crate_n100.append(crate)
        if not ((1<<crate) & n20_relay):
            removed_crate_n20.append(crate)

    # If the crate is out of the MTCA/+ N100 relay mask
    for crate in removed_crate_n100:
        # If the crate did not fail Ping crates
        if crate not in n100_failed:
            # Then its probably a mismapping
            mismapped_n100+=str(crate)+", "

    # Similiarly for N20
    for crate in removed_crate_n20:
        if crate not in n20_failed:
            mismapped_n20+=str(crate)+", "

    # Formatting
    n100_str = n100_str[0:-2]
    n20_str = n20_str[0:-2]
    mismapped_n100 = mismapped_n100[0:-2]
    mismapped_n20 = mismapped_n20[0:-2]

    return n100_str, n20_str, mismapped_n100, mismapped_n20


def crates_failed_messages(run):
    '''
    Returns messages related to ping crates failing 
    as well as potential MTCA/+ relay mis-mappings
    '''

    messages = []

    # Warn about ping crates failures, messages print to detector state check
    try:
        n100, n20, mn100, mn20 = crates_failed(run)
        if n100:
            if len(n100) > 2:
                messages.append("crates %s failed N100 checks in ping crates" % n100)
            else:
                messages.append("crate %s failed N100 checks in ping crates" % n100)
        if n20:
            if len(n20) > 2:
                messages.append("crates %s failed N20 checks in ping crates" % n20)
            else:
                messages.append("crate %s failed N20 checks in ping crates" % n20)
        if mn100:
            if len(mn100) > 2:
                messages.append("Warning: crates %s N100 is mismapped !" % mn100)
            else:
                messages.append("Warning: crate %s N100 is mismapped !" % mn100)
        if mn20:
            if len(mn20) > 2:
                messages.append("Warning: crates %s N20 is mismapped !" % mn20)
            else:
                messages.append("Warning: crate %s N20 is mismapped !" % mn20)
    except Exception as e:
        # No avaiable ping crates data, no need to warn
        pass

    return messages


def ping_crates_list(limit):
    '''
    Returns a list of ping crates information for runs larger
    than the current run - limit
    '''

    run = get_latest_run()

    conn = engine.connect()

    result = conn.execute("SELECT DISTINCT ON (run) timestamp, "
                          "run, n100_crates_failed, n20_crates_failed FROM ping_crates "
                          "WHERE run > %s", (run - limit))

    ping_info = []

    for timestamp, run, n100, n20 in result:

        n100_fail_str = ""
        n20_fail_str = ""
        n100_warn_str = ""
        n20_warn_str = ""
        status = "Pass"

        # N100 ping crates status
        for i in range(len(n100)):
            if n100[i] < 20:
                n100_fail_str+=str(n100[i]) + ", "
                status = "Fail"
            else:
                n100_warn_str+=str(n100[i]%20) + ", "
                if status != "Fail":
                    status = "Warn"

        # N20 ping crates status
        for i in range(len(n20)):
            if n20[i] < 20:
                n20_fail_str+=str(n20[i]) + ", " 
                status = "Fail"
            else:
                n20_warn_str+=str(n20[i]%20) + ", "
                if status != "Fail":
                    status = "Warn"

        # Reformatting of the messages
        if n100_fail_str == "":
            n100_fail_str = "None"
        else:
            n100_fail_str = n100_fail_str[0:-2]
        if n20_fail_str == "":
            n20_fail_str = "None"
        else:
            n20_fail_str = n20_fail_str[0:-2]
        if n100_warn_str == "":
            n100_warn_str = "None"
        else:
            n100_warn_str = n100_warn_str[0:-2]
        if n20_warn_str == "":
            n20_warn_str = "None"
        else:
            n20_warn_str = n20_warn_str[0:-2]

        # parse timestamp format a little
        timestamp = str(timestamp)
        timestamp = timestamp[0:19]

        # A list of all the ping crates information
        ping_info.append((timestamp,int(run),n100_fail_str,n20_fail_str,n100_warn_str,n20_warn_str,status))

    # Sort by run-number, for display purposes
    ping_info = sorted(ping_info,key=lambda l:l[1], reverse=True)

    return ping_info

