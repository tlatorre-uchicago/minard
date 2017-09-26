from .db import engine
from .detector_state import get_latest_run

def crates_failed(run): 

    conn = engine.connect()

    result = conn.execute("SELECT n100_crates_failed, n20_crates_failed FROM ping_crates "
                          "WHERE run = %i" % run)

    n100_failed = []
    n20_failed = []

    for n100, n20 in result.fetchall():
        for i in n100:
            if i < 20:
                n100_failed.append(i)
        for i in n20:
            if i < 20: # warnings are > 20
                n20_failed.append(i)

    return n100_failed, n20_failed

def ping_crates_list(limit):

    run = get_latest_run()

    conn = engine.connect()

    result = conn.execute("SELECT timestamp, run, n100_crates_failed, n20_crates_failed FROM ping_crates "
                          "WHERE run > %i" % int(run - limit))

    ping_info = []

    for timestamp, run, n100, n20 in result:

        n100_fail_str = ""
        n20_fail_str = ""
        n100_warn_str = ""
        n20_warn_str = ""
        status = "Pass"

        for i in range(len(n100)):

            if n100[i] < 20:
                n100_fail_str+=str(n100[i]) + ", "
                status = "Fail"
            else:
                n100_warn_str+=str(n100[i]%20) + ", "
                if status != "Fail":
                    status = "Warn"

        for i in range(len(n20)):

            if n20[i] < 20:
                n20_fail_str+=str(n20[i]) + ", " 
                status = "Fail"
            else:
                n20_warn_str+=str(n20[i]%20) + ", "
                if status != "Fail":
                    status = "Warn"

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

        ping_info.append((timestamp,int(run),n100_fail_str,n20_fail_str,n100_warn_str,n20_warn_str,status))

    ping_info = sorted(ping_info,key=lambda l:l[1], reverse=True)

    return ping_info

