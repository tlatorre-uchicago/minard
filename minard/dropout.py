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

def get_fits(trigger_type=0):
    """
    """
    conn = engine_nl.connect()

    result = conn.execute("SELECT plots.run, fit.rate FROM dropout_fits AS fit "
                          "INNER JOIN dropout_plots AS plots ON "
                          "fit.fit_plot=plots.key where trigger_type=%s ORDER BY plots.run DESC",
                          (1 if trigger_type==0 else 2,))

    ret = result.fetchall()
    ret = [list(x) for x in ret]
    return json.dumps(ret)
