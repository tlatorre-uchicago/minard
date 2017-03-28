from wtforms import Form, BooleanField, StringField, validators, IntegerField

class ChannelStatusForm(Form):
    crate =              IntegerField('crate', [validators.NumberRange(min=0,max=19)])
    slot =               IntegerField('slot', [validators.NumberRange(min=0,max=15)])
    channel =            IntegerField('channel', [validators.NumberRange(min=0,max=31)])
    low_occupancy =      BooleanField('Low Occupancy')
    zero_occupancy =     BooleanField('Zero Occupancy')
    screamer =           BooleanField('Screamer')
    bad_discrimintator = BooleanField('Bad Discriminator')
    no_n100 =            BooleanField('No N100')
    no_n20 =             BooleanField('No N20')
    no_esum =            BooleanField('No ESUM')
    cable_pulled =       BooleanField('Cable pulled')
    bad_cable =          BooleanField('Bad Cable')
    resistor_pulled =    BooleanField('Resistor pulled')
    other =              BooleanField('Other')
    bad_base_current =   BooleanField('Bad Base Current')
    info =               StringField('Info', [validators.Length(min=1)])
