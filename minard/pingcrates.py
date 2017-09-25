from .db import nearline_engine

def pingcrates(run): 

    conn = nearline_engine.connect()

    result = conn.execute("SELECT n100_crates_failed, n20_crates_failed from ping_crates where run = %s" % run)

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
