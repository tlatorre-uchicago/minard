from .db import engine
from polling import relay_status, channel_information, pmt_type, check_hv_status
import json

def occupancy_by_trigger(trigger_type, run):

    datafile = open("/home/tannerbk/minard/fake_data/OccupancyByTrigger.ratdb")

    data = json.load(datafile)

    norm_str = 'trigger_norm_' + str(trigger_type)
    type_str = 'trigger_' + str(trigger_type)

    norm_by_trigger = data[norm_str]
    data_by_trigger = data[type_str]

    if norm_by_trigger == 0:
        data_by_trigger = [0.0]*9728
        return data_by_trigger

    data_by_trigger = [float(x) / norm_by_trigger for x in data_by_trigger]

    return data_by_trigger

def check_occupancy(trigger_type, run):

    conn = engine.connect()

    datafile = open("/home/tannerbk/minard/fake_data/OccupancyByTrigger.ratdb")

    data1 = json.load(datafile)

    type_str = 'trigger_' + str(trigger_type)
    norm_str = 'trigger_norm_' + str(trigger_type)

    norm_by_trigger = data1[norm_str]
    data = data1[type_str]

    # Fixme do slot average
    slot_average = [0.0]*304
    channel_count = [32.0]*304

    for i in range(len(data)):

        crate = i/512
        card = (i%512)/32
        channel = (i%512)%32

        lcn = card + 16*crate

        if data[i] == -1:
            channel_count[lcn] -= 1
            continue

        slot_average[lcn] += data[i]

    for i in range(304):
        crate = i/16
        slot = i%16
        if channel_count[i] != 0 and slot_average[i]/(channel_count[i]*norm_by_trigger) < 2e-5:
                print i, crate, slot, slot_average[i], channel_count[i], slot_average[i]/(channel_count[i]*norm_by_trigger)

