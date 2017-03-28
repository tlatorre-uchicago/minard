from wtforms import Form, BooleanField, StringField, validators, IntegerField
from detector_state import engine

class ChannelStatusForm(Form):
    crate =              IntegerField('crate', [validators.NumberRange(min=0,max=19)])
    slot =               IntegerField('slot', [validators.NumberRange(min=0,max=15)])
    channel =            IntegerField('channel', [validators.NumberRange(min=0,max=31)])
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
    other =              BooleanField('Other')
    bad_base_current =   BooleanField('Bad Base Current')
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
        query = "SELECT * FROM channeldb WHERE %s LIMIT %i" % (" AND ".join(filter), limit)
    else:
        query = "SELECT * FROM channeldb LIMIT %i" % limit

    result = conn.execute(query)

    if result is None:
        return None

    keys = result.keys()
    rows = result.fetchall()

    return [dict(zip(keys,row)) for row in rows]

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
    result = conn.execute("INSERT INTO channeldb (crate, slot, channel, low_occupancy, zero_occupancy, screamer, bad_discriminator, no_n100, no_n20, no_esum, cable_pulled, bad_cable, resistor_pulled, other, bad_base_current, info) VALUES (%(crate)s, %(slot)s, %(channel)s, %(low_occupancy)s, %(zero_occupancy)s, %(screamer)s, %(bad_discriminator)s, %(no_n100)s, %(no_n20)s, %(no_esum)s, %(cable_pulled)s, %(bad_cable)s, %(resistor_pulled)s, %(other)s, %(bad_base_current)s, %(info)s)", **form.data)
    return result
