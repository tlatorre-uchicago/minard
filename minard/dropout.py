from .db import engine_nl
import json
import detector_state

def get_details(run_number, trigger_type):
    conn = engine_nl.connect()
    command = "select f.rate, f.peak_offset, f.sigma, f.separation, p.x_vals, p.y_vals, p.fit_vals from dropout_fits as f INNER JOIN dropout_plots as p on f.fit_plot=p.key where p.run=%s and p.trigger_type=%s"
    result = conn.execute(command, (run_number, trigger_type));
    keys = result.keys()
    data = result.fetchone()
    try:
        return json.dumps(dict(zip(keys, data)))
    except TypeError:
        return json.dumps(None)

def get_fits():
    """
    """
    conn = engine_nl.connect()

    result = conn.execute("SELECT fit.rate, plots.trigger_type, plots.run FROM dropout_fits AS fit "
                          "INNER JOIN dropout_plots AS plots ON "
                          "fit.fit_plot=plots.key ORDER BY plots.run DESC")

    ret = {}
    for rate, trigger, run in result.fetchall():
        if not ret.has_key(run):
            ret[run] = [None, None]
        if trigger==1:
            ret[run][0] = rate
        if trigger==2:
            ret[run][1] = rate

    return json.dumps(ret.items())

