from wtforms import Form, BooleanField, StringField, validators, IntegerField, PasswordField
from .db import engine
from .views import app
import psycopg2
import psycopg2.extensions

class ChannelStatusForm(Form):
    """
    A class for the form to update the channel status database.
    """
    crate =              IntegerField('crate', [validators.NumberRange(min=0,max=19)])
    slot =               IntegerField('slot', [validators.NumberRange(min=0,max=15)])
    channel =            IntegerField('channel', [validators.NumberRange(min=0,max=31)])
    pmt_removed =        BooleanField('PMT removed')
    pmt_reinstalled =    BooleanField('PMT reinstalled')
    low_occupancy =      BooleanField('Low Occupancy')
    zero_occupancy =     BooleanField('Zero Occupancy')
    screamer =           BooleanField('Screamer')
    bad_discriminator =  BooleanField('Bad Discriminator')
    no_n100 =            BooleanField('No N100')
    no_n20 =             BooleanField('No N20')
    no_esum =            BooleanField('No ESUM')
    cable_pulled =       BooleanField('Cable pulled')
    bad_cable =          BooleanField('Bad Cable')
    resistor_pulled =    BooleanField('Resistor pulled')
    disable_n100 =       BooleanField('Disable N100')
    disable_n20 =        BooleanField('Disable N20')
    high_dropout =       BooleanField('High Dropout')
    bad_base_current =   BooleanField('Bad Base Current')
    bad_data =           BooleanField('Bad Data')
    name =               StringField('Name', [validators.Length(min=1)])
    reason =             StringField('Reason')
    info =               StringField('Info', [validators.Length(min=1)])
    password =           PasswordField('Password')

@app.template_filter('pmt_type_description')
def pmt_type_description(pmt_type):
    """
    Converts a PMT type -> useful description.
    """
    active, pmt_type = pmt_type & 0x1, pmt_type & 0xfffe

    if pmt_type == 0x2:
        return "Normal"
    elif pmt_type == 0x4:
        return "Rope"
    elif pmt_type == 0x8:
        return "Neck"
    elif pmt_type == 0x10:
        return "FECD"
    elif pmt_type == 0x20:
        return "Low Gain"
    elif pmt_type == 0x40:
        return "OWL"
    elif pmt_type == 0x80:
        return "Butt"
    elif pmt_type == 0x12:
        return "Petal-less PMT"
    elif pmt_type == 0x00:
        return "No PMT"
    elif pmt_type == 0x100:
        return "HQE PMT"
    else:
        return "Unknown type 0x%04x" % pmt_type

def get_channels(kwargs, limit=100):
    """
    Returns a list of the current channel statuses for multiple channels in the
    detector. `kwargs` should be a dictionary containing fields and their
    associated values to select on. For example, to select only channels that
    have low occupancy:

        >>> get_channels({'low_occupancy': True})

    `limit` should be the maximum number of records returned.
    """
    conn = engine.connect()

    fields = [field.name for field in ChannelStatusForm()]

    # make sure all the values in kwargs are actual fields
    kwargs = dict(item for item in kwargs.items() if item[0] in fields)

    query = "SELECT * FROM current_channel_status "
    if len(kwargs):
        query += "WHERE %s " % (" AND ".join(["%s = %%(%s)s" % (item[0], item[0]) for item in kwargs.items()]))
    query += "ORDER BY crate, slot, channel LIMIT %i" % limit

    result = conn.execute(query, kwargs)

    if result is None:
        return None

    keys = result.keys()
    rows = result.fetchall()

    return [dict(zip(keys,row)) for row in rows]

def get_channel_history(crate, slot, channel, limit=None):
    """
    Returns a list of the channel statuses for a single channel in the
    detector. `limit` is the maximum number of records to return.
    """
    conn = engine.connect()

    query = "SELECT * FROM channel_status " + \
        "WHERE crate = %s AND slot = %s AND channel = %s " + \
        "ORDER BY timestamp DESC"

    if limit is not None:
        query += " LIMIT %i" % limit

    result = conn.execute(query, (crate,slot,channel))

    if result is None:
        return None

    keys = result.keys()
    rows = result.fetchall()

    return [dict(zip(keys,row)) for row in rows]

def get_pmt_info(crate, slot, channel):
    """
    Returns a dictionary of the pmt info for a given channel.
    """
    conn = engine.connect()

    result = conn.execute("SELECT * FROM pmt_info "
        "WHERE crate = %s AND slot = %s AND channel = %s",
        (crate, slot, channel))

    if result is None:
        return None

    keys = result.keys()
    row = result.fetchone()

    if row is None:
        return None

    return dict(zip(keys,row))

def get_pmt_types():
    """
    Returns a list of the pmt types for all channels.
    """
    conn = engine.connect()

    result = conn.execute("SELECT crate, slot, channel, type FROM pmt_info")

    if result is None:
        return None

    rows = result.fetchall()

    pmt_info = {}
    for row in rows:
        crate, slot, channel, pmt_type = row
        if crate not in pmt_info:
            pmt_info[crate] = {}
        if slot not in pmt_info[crate]:
            pmt_info[crate][slot] = {}
        pmt_info[crate][slot][channel] = pmt_type

    return pmt_info

def get_nominal_settings_for_run(run=0):
    """
    Returns a dictionary of the nominal settings for all the channels in the
    detector for a given run.
    """
    conn = engine.connect()

    if run == 0:
        # current nominal settings
        result = conn.execute("SELECT crate, slot, channel, n100, n20, "
            "sequencer FROM current_nominal_settings")
    else:
        result = conn.execute("SELECT DISTINCT ON (crate, slot, channel) "
            "crate, slot, channel, n100, n20, sequencer FROM nominal_settings "
            "WHERE timestamp < (SELECT timestamp FROM run_state WHERE run = %s) "
            "ORDER BY crate, slot, channel, timestamp DESC", (run,))

    if result is None:
        return None

    keys = result.keys()
    rows = result.fetchall()

    channels = {}
    for row in rows:
        crate, slot, channel, n100, n20, sequencer = row
        if crate not in channels:
            channels[crate] = {}
        if slot not in channels[crate]:
            channels[crate][slot] = {}
        channels[crate][slot][channel] = n100, n20, sequencer

    return channels

def get_nominal_settings(crate, slot, channel):
    """
    Returns a dictionary of the current nominal settings for a single channel
    in the detector.
    """
    conn = engine.connect()

    result = conn.execute("SELECT * FROM current_nominal_settings "
        "WHERE crate = %s AND slot = %s AND channel = %s",
        (crate,slot,channel))

    if result is None:
        return None

    keys = result.keys()
    row = result.fetchone()

    return dict(zip(keys,row))

def get_most_recent_polling_info(crate, slot, channel):
    """
    Returns a dictionary of the cmos and base currents check rates polling 
    info for a single channel in the detector, for the most recent check rates.
    """
    conn = engine.connect()

    # Get the run during which cmos check rates was run most recently
    result = conn.execute("SELECT run FROM cmos ORDER by run DESC limit 1")
    cmos_run = result.fetchone()
    for run in cmos_run:
        run_ = run

    result = conn.execute("SELECT * FROM cmos WHERE run = %s and crate = %s "
        "AND slot = %s AND channel = %s", (run_, crate, slot, channel))

    if result is None:
        return None, None

    keys = result.keys()
    row = result.fetchone()
    cmos = dict(zip(keys,row))

    # Get the run during which base check rates was run most recently
    result = conn.execute("SELECT run FROM base ORDER by run DESC limit 1")
    base_run = result.fetchone()
    for run in base_run:
        run_ = run

    result = conn.execute("SELECT * FROM base WHERE run = %s and crate = %s "
        "AND slot = %s AND channel = %s", (run_, crate, slot, channel))

    if result is None:
        return None, None

    keys = result.keys()
    row = result.fetchone()
    base = dict(zip(keys,row))

    polls = cmos.copy()
    polls.update(base)

    return polls

def get_discriminator_threshold(crate, slot, channel):
    """
    Get the current discriminator threshold for a specified 
    crate, card, and channel. Returns a disctionary of the 
    discriminator threshold and zero threshold.
    """

    conn = engine.connect()

    # Select most recent zdisc with ecalid field
    result = conn.execute("SELECT zero_disc FROM zdisc WHERE "
        "(ecalid <> '') and crate = %s and slot = %s "
        "ORDER BY timestamp DESC limit 1", (crate, slot))

    if result is None:
        return None

    keys = result.keys()
    row = result.fetchone()

    if row is None:
        return None

    zthr = dict(zip(keys,row))

    # Get the current discriminator threshold
    result = conn.execute("SELECT vthr FROM current_detector_state WHERE "
        "crate = %s and slot = %s", (crate, slot))
    if result is None:
        return None

    keys = result.keys()
    row = result.fetchone()

    if row is None:
        return None

    vthr = dict(zip(keys,row))

    threshold = zthr.copy()
    threshold.update(vthr)

    return threshold

def get_all_thresholds(run):
    """
    Get the discriminator threshold and zero threshold
    for the entire detector. Return a list of thresholds
    above zero and some information about channels with
    maxed thresholds.
    """

    conn = engine.connect()

    zero = [[0 for i in range(16)] for j in range(19)]
    thr = [[0 for i in range(16)] for j in range(19)]
    disc = [9999]*9728

    # Select most recent zdisc with ecalid field.
    result = conn.execute("SELECT crate, slot, zero_disc FROM zdisc WHERE "
        "(ecalid <> '') ORDER BY timestamp DESC limit 304")
   
    if result is None:
        return None

    rows = result.fetchall()
    for crate, slot, zero_disc in rows:
        zero[crate][slot] = zero_disc

    result = conn.execute("SELECT crate, slot, vthr FROM detector_state WHERE "
        "run = %s ORDER BY crate, slot", run)

    if result is None:
        return None

    rows = result.fetchall()
    for crate, slot, vthr in rows:
        thr[crate][slot] = vthr

    disc_average = 0
    lower_disc_average = 0
    online_channels = 0
    count_max_thresholds = 0
    maxed_thresholds = []

    for crate in range(19):
        for slot in range(16):
            # No Vthr information, slot is missing
            if thr[crate][slot] != 0:
                for channel in range(len(thr[crate][slot])):
                    threshold = thr[crate][slot][channel] - zero[crate][slot][channel]
                    lcn = crate*512+slot*32+channel
                    if thr[crate][slot][channel] != 255:
                        disc[lcn] = int(threshold)
                        disc_average += int(threshold) 
                    else: 
                        count_max_thresholds += 1
                        maxed_thresholds.append((crate,slot,channel))
                    online_channels += 1

    disc_average = round(float(disc_average) / online_channels, 3)

    return disc, disc_average, count_max_thresholds, maxed_thresholds

def get_channel_status(crate, slot, channel):
    """
    Returns a dictionary of the channel status for a single channel in the
    detector.
    """
    conn = engine.connect()

    result = conn.execute("SELECT * FROM current_channel_status "
        "WHERE crate = %s AND slot = %s AND channel = %s",
        (crate,slot,channel))

    if result is None:
        return None

    keys = result.keys()
    row = result.fetchone()

    return dict(zip(keys,row))

def get_channel_status_form(crate, slot, channel):
    """
    Returns a channel status form filled in with the current channel status for
    a single channel in the detector.
    """
    return ChannelStatusForm(**get_channel_status(crate, slot, channel))

def upload_channel_status(form):
    """
    Upload a new channel status record in the database.
    """
    conn = psycopg2.connect(dbname=app.config['DB_NAME'],
                            user=app.config['DB_EXPERT_USER'],
                            host=app.config['DB_HOST'],
                            password=form.password.data)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()
    cursor.execute("INSERT INTO channel_status "
        "(crate, slot, channel, pmt_removed, pmt_reinstalled, low_occupancy, "
        "zero_occupancy, screamer, bad_discriminator, no_n100, no_n20, "
        "no_esum, cable_pulled, bad_cable, resistor_pulled, disable_n100, "
        "disable_n20, high_dropout, bad_base_current, bad_data, name, reason, "
        "info) "
        "VALUES (%(crate)s, %(slot)s, %(channel)s, %(pmt_removed)s, "
        "%(pmt_reinstalled)s, %(low_occupancy)s, %(zero_occupancy)s, "
        "%(screamer)s, %(bad_discriminator)s, %(no_n100)s, %(no_n20)s, "
        "%(no_esum)s, %(cable_pulled)s, %(bad_cable)s, %(resistor_pulled)s, "
        "%(disable_n100)s, %(disable_n20)s, %(high_dropout)s, "
        "%(bad_base_current)s, %(bad_data)s, %(name)s, %(reason)s, %(info)s)",
         form.data)

def get_current_run():

    conn = engine.connect()

    result = conn.execute("SELECT last_value FROM run_number")

    return result.fetchone()[0]
