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

def upload_channel_status(form):
    conn = engine.connect()
    result = conn.execute("INSERT INTO channeldb (crate, slot, channel, low_occupancy, zero_occupancy, screamer, bad_discriminator, no_n100, no_n20, no_esum, cable_pulled, bad_cable, resistor_pulled, other, bad_base_current, info) VALUES (%(crate)s, %(slot)s, %(channel)s, %(low_occupancy)s, %(zero_occupancy)s, %(screamer)s, %(bad_discriminator)s, %(no_n100)s, %(no_n20)s, %(no_esum)s, %(cable_pulled)s, %(bad_cable)s, %(resistor_pulled)s, %(other)s, %(bad_base_current)s, %(info)s)", **form.data)
    return result
