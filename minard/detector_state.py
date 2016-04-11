import sqlalchemy
from minard import app

def fetch_from_table_with_key(table_name,key,key_name='key'):
    user = app.config['DB_USER']
    password = app.config['DB_PASS']
    host = app.config['DB_HOST']
    database = app.config['DB_NAME']
    if key is None: key = "(SELECT max("+key_name+") FROM "+table_name+")"
    engine = sqlalchemy.create_engine('postgresql://%s:%s@%s/%s' % (user, password, host, database))

    try:
        conn = engine.connect()
    except Exception as e:
        #Do somethign here?
        raise e;
    command = "SELECT * FROM "+str(table_name)+" WHERE "+str(key_name)+" = "+str(key)
    res =  conn.execute(command)
    try:
        values = zip(res.keys(),res.fetchone())
    except TypeError:
        #Chances are this failed b/c the SELECT command didn't find anything
        raise ValueError(str(key_name)+" "+str(run)+" is not valid...probably")
    conn.close()
    return dict(values)

def get_detector_control_state(key):
    return fetch_from_table_with_key('detector_control',key)
    
def get_caen_state(key):
    return fetch_from_table_with_key('caen',key)

def get_mtc_state(key):
    return fetch_from_table_with_key('mtc',key)

def get_crate_state(key):
    cards = fetch_from_table_with_key('crate',key)
    ret={}
    for card_num in range(16):
        card_key = "mb%i"%card_num
        ret[card_key] = fetch_from_table_with_key('fec',cards[card_key])
#    for card_name,table_key  in filter(lambda x: 'mb' in x[0],cards.iteritems()):
#        ret[card_name] = fetch_from_table_with_key('fec',table_key)
    return ret
def get_fec_state(key):
    return fetch_from_table_with_key('fec',key)

def get_run_state(run):
    return fetch_from_table_with_key('run_state',run,key_name='run')
def translate_trigger_mask(maskVal):
    trigger_bit_to_string = [
                                (0 ,"NHIT100LO"),
                                (1 ,"NHIT100MED"),
                                (2 ,"NHIT100HI"),
                                (3 ,"NHIT20"),
                                (4 ,"NHIT20LB"),
                                (5 ,"ESUMLO"),
                                (6 ,"ESUMHI"),
                                (7 ,"OWLN"),
                                (8 ,"OWLELO"),
                                (9 ,"OWLEHI"),
                                (10,"PULSE_GT"),
                                (11,"PRESCALE"),
                                (12,"PEDESTAL"),
                                (13,"PONG"),
                                (14,"SYNC"),
                                (15,"EXT_ASYNC"),
                                (16,"EXT2"),
                                (17,"EXT3"),
                                (18,"EXT4"),
                                (19,"EXT5"),
                                (20,"EXT6"),
                                (21,"EXT7"),
                                (22,"EXT8_PULSE_ASYNC"),
                                (23,"SPECIAL_RAW"),
                                (24,"NCD"),
                                (25,"SOFT_GT")
                            ]
    triggers =  filter(lambda x: ((maskVal & 1<<x[0]) > 0),trigger_bit_to_string)
    return map(lambda x: x[1],triggers)
def translate_ped_delay(coarseDelay_mask,fineDelay_mask):
    MIN_GT_DELAY = 18.35; #Taken from daq/src/mtc.c
    AddelSlope = 0.1; #Taken from daq/src/mtc.c
    coarseDelay = ((~coarseDelay_mask & 0xFF))*10;
    fine_delay = (fineDelay_mask & 0xFF) * AddelSlope;
    return coarseDelay + fine_delay;
def translate_lockout_width(lockout_mask):
    lockout = (~lockout_mask) & 0xFF;
    return lockout*20
def translate_control_reg(control_reg):
    bit_to_string = [
        (0, "PED_EN"),
        (1, "PULSE_EN"),
        (2, "LOAD_ENPR"),
        (3, "LOAD_ENPS"),
        (4, "LOAD_ENPW"),
        (5, "LOAD_ENLK"),
        (6, "ASYNC_EN"),
        (7, "RESYNC_EN"),
        (8, "TESTGT"),
        (9, "TEST50"),
        (10, "kTEST10"),
        (11, "kLOAD_ENGT"),
        (12, "kLOAD_EN50"),
        (13, "kLOAD_EN10"),
        (14, "kTESTMEM1"),
        (15, "kTESTMEM2"),
        (16, "FIFO_RESET")
        ]
    word_list = filter(lambda x:((control_reg & 1<<x[0]) >0), bit_to_string)
    return map(lambda x:x[1], word_list)
def translate_crate_mask(mask):
    return filter(lambda x: (mask & 1<<x) > 0,range(0,20))
def translate_prescale(prescale):
    return (~prescale & 0xFFFF)+1
@app.template_filter('mtc_human_readable')
def mtc_human_readable_filter(mtc):
    ret = {}
    try:
        ret['gt_words'] = translate_trigger_mask(mtc['gt_mask'])
        ret['ped_delay'] = translate_ped_delay(mtc['coarse_delay'],mtc['fine_delay'])
        ret['lockout_width'] = translate_lockout_width(mtc['lockout_width'])
        ret['control_reg'] = translate_control_reg(mtc['control_register'])
        ret['ped_crates'] = translate_crate_mask(mtc['pedestal_mask'])
        ret['gt_crates'] = translate_crate_mask(mtc['gt_crate_mask'])
        ret['prescale'] = translate_prescale(mtc['prescale'])
        ret['N100_crates'] = translate_crate_mask(mtc['mtca_relays'][0])
    except Exception:
        return False
    return ret
@app.template_filter('caen_human_readable')
def caen_human_readable_filter(caen):
    ret = {}
    ret['post_trigger'] = caen['post_trigger']

