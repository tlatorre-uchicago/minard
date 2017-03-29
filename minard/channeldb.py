from wtforms import Form, BooleanField, StringField, validators, IntegerField
from detector_state import engine

class ChannelStatusForm(Form):
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
    bad_base_current =   BooleanField('Bad Base Current')
    name =               StringField('Name', [validators.Length(min=1)])
    info =               StringField('Info', [validators.Length(min=1)])

def get_channels(crate=None, slot=None, channel=None, limit=100):
    """
    Returns a dictionary of the channel status for multiple channels in the detector.
    """
    conn = engine.connect()

    filter = []
    if crate is not None:
        filter.append("crate = %i" % crate)
    if slot is not None:
        filter.append("slot = %i" % slot)
    if channel is not None:
        filter.append("channel = %i" % channel)

    if len(filter):
        query = "SELECT DISTINCT ON (crate, slot, channel) * FROM channeldb WHERE %s ORDER BY crate, slot, channel, timestamp DESC LIMIT %i" % (" AND ".join(filter), limit)
    else:
        query = "SELECT DISTINCT ON (crate, slot, channel) * FROM channeldb ORDER BY crate, slot, channel, timestamp DESC LIMIT %i" % limit

    result = conn.execute(query)

    if result is None:
        return None

    keys = result.keys()
    rows = result.fetchall()

    return [dict(zip(keys,row)) for row in rows]

def get_channel_history(crate, slot, channel, limit=100):
    """
    Returns a dictionary of the channel status for multiple channels in the detector.
    """
    conn = engine.connect()

    result = conn.execute("SELECT * FROM channeldb WHERE crate = %s AND slot = %s AND channel = %s ORDER BY timestamp DESC LIMIT %s", (crate,slot,channel,limit))

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

    result = conn.execute("SELECT * FROM pmt_info WHERE crate = %s AND slot = %s AND channel = %s", (crate, slot, channel))

    if result is None:
        return None

    keys = result.keys()
    row = result.fetchone()

    if row is None:
        return None

    return dict(zip(keys,row))

def get_channel_status(crate, slot, channel):
    """
    Returns a dictionary of the channel status for multiple channels in the detector.
    """
    conn = engine.connect()

    result = conn.execute("SELECT * FROM channeldb WHERE crate = %s AND slot = %s AND channel = %s ORDER BY timestamp DESC LIMIT 1", (crate,slot,channel))

    if result is None:
        return None

    keys = result.keys()
    row = result.fetchone()

    return dict(zip(keys,row))

def get_channel_status_form(crate, slot, channel):
    return ChannelStatusForm(**get_channel_status(crate, slot, channel))

def upload_channel_status(form):
    conn = engine.connect()
    result = conn.execute("INSERT INTO channeldb (crate, slot, channel, pmt_removed, pmt_reinstalled, low_occupancy, zero_occupancy, screamer, bad_discriminator, no_n100, no_n20, no_esum, cable_pulled, bad_cable, resistor_pulled, disable_n100, disable_n20, bad_base_current, name, info) VALUES (%(crate)s, %(slot)s, %(channel)s, %(pmt_removed)s, %(pmt_reinstalled)s, %(low_occupancy)s, %(zero_occupancy)s, %(screamer)s, %(bad_discriminator)s, %(no_n100)s, %(no_n20)s, %(no_esum)s, %(cable_pulled)s, %(bad_cable)s, %(resistor_pulled)s, %(disable_n100)s, %(disable_n20)s, %(bad_base_current)s, %(name)s, %(info)s)", **form.data)
    return result
