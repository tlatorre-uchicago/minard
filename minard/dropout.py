from .db import engine_nl
import json
import detector_state

def get_fits(limit=100):
    """
    """
    conn = engine_nl.connect()

    result = conn.execute("SELECT fit.rate, plots.trigger_type, plots.run FROM dropout_fits AS fit "
                          "INNER JOIN dropout_plots AS plots ON "
                          "fit.fit_plot=plots.key ORDER BY plots.run DESC LIMIT %s",
                          (limit, ))

    #temp = zip(*result.fetchall())
    ret = {}
    for rate, trigger, run in result.fetchall():
        if not ret.has_key(run):
            ret[run] = [None, None]
        if trigger==1:
            ret[run][0] = rate
        if trigger==2:
            ret[run][1] = rate

    return json.dumps(ret.items())

