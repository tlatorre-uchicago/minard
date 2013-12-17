from websno.stream import OrcaJSONStream

cmos = {}

def callback(output):
    for item in output:
        if 'key' in item and item['key'] == 'cmos_rate':
            crate, card = item['crate_num'], item['slot_num']
            rate = item['v']['rate']

            if crate not in cmos:
                cmos[crate] = {}

            cmos[crate][card] = dict(zip(range(len(rate)),rate))

