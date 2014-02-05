from __future__ import division
from threading import Timer, Lock, Thread
import time
from collections import defaultdict
import socket
from xml.etree.ElementTree import XML
from itertools import izip_longest
import struct
import numpy as np
from datetime import datetime

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') -> ABC DEF Gxx
    args = [iter(iterable)]*n
    return izip_longest(fillvalue=fillvalue, *args)

def parse_cmos(rec):
    crate, slot_mask = struct.unpack('II', rec[:8])
    channel_mask = np.frombuffer(rec[8:8+4*16], dtype=np.uint32)
    delay, error_flags = struct.unpack('II',rec[72:72+2*4])
    counts = np.frombuffer(rec[80:80+8*32*4], dtype=np.uint32).reshape((8,-1))
    date_string = rec[21*4+8*32*4-4:].strip('\x00')
    timestamp = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    return crate, slot_mask, channel_mask, delay, error_flags, counts, timestamp

def parse_base(rec):
    crate, slot_mask = struct.unpack('II', rec[:8])
    channel_mask = np.frombuffer(rec[8:8+4*16], dtype=np.uint32)
    error_flags = struct.unpack('I',rec[72:72+4])
    counts = np.frombuffer(rec[76:76+8*32*4], dtype=np.uint32).reshape((8,-1))
    date_string = rec[20*4+8*32*4-4:].strip('\x00')
    timestamp = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    return crate, slot_mask, channel_mask, error_flags, counts, timestamp

def parse_header(header):
    root = XML(header)
    assert root.tag == 'plist'

    def parse_item(item):
        if item.tag == 'integer':
            return int(item.text)
        elif item.tag == 'string':
            return item.text
        elif item.tag == 'dict':
            d = {}
            for key, value in grouper(item,2):
                d[key.text] = parse_item(value)
            return d
        elif item.tag == 'array':
            return [parse_item(x) for x in item]
        elif item.tag == 'false':
            return False
        elif item.tag == 'true':
            return True
        elif item.tag == 'real':
            return float(item.text)
        else:
            raise Exception("can't parse %s" % item.tag)

    return [parse_item(x) for x in root]

def total_seconds(td):
    """Returns the total number of seconds contained in the duration."""
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

class CMOSThread(Thread):
    def __init__(self, callback, hostname='snoplusdaq1', port=44666):
        Thread.__init__(self)
        self.callback = callback
        self.socket = Socket()
        self.hostname = hostname
        self.port = port

        self.cmos = {}
        self.tzero = datetime.now()

    def run(self):
        self.socket.connect(self.hostname, self.port)

        # receive header
        id, rec = self.socket.recv_record()

        assert id == 0
        header = parse_header(rec[4:-1])

        datadesc = header[0]['dataDescription']

        cmos_id = datadesc['ORXL3Model']['Xl3CmosRate']['dataId']
        base_id = datadesc['ORXL3Model']['Xl3PmtBaseCurrent']['dataId']

        while True:
            id, rec = self.socket.recv_record()

            if id == base_id:
                continue
                crate, slotmask, channelmask, error_flags, counts, timestamp = \
                    parse_base(rec)

                adc = {}

                for i, slot in enumerate(i for i in range(16) if (slotmask >> i) & 1):
                    adc[i] = {}
                    for j, count in enumerate(counts[i]):
                        if not channelmask[slot] & (1 << j) or count >> 31:
                            continue

                        adc[slot][j] = count

                self.callback({'key': 'base', 'crate': crate, 'adc': adc})

            if id == cmos_id:
                crate, slotmask, channelmask, delay, error_flags, counts, timestamp = \
                    parse_cmos(rec)

                rate = {}

                if crate not in self.cmos:
                    self.cmos[crate] = {}

                for i, slot in enumerate(i for i in range(16) if (slotmask >> i) & 1):
                    if slot not in self.cmos[crate]:
                        self.cmos[crate][slot] = {}

                    rate[slot] = {}

                    for j, count in enumerate(counts[i]):
                        if not channelmask[slot] & (1 << j) or count >> 31:
                            continue

                        if j in self.cmos[crate][slot]:
                            prev_count, prev_time = self.cmos[crate][slot][j]
                            dt = total_seconds(timestamp-prev_time)
                            if dt < 10.0:
                                rate[slot][j] = (count-prev_count)/dt

                        self.cmos[crate][slot][j] = count, timestamp

                self.callback({'key': 'cmos', 'crate': crate, 'rate': rate})

class Socket(object):
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host,port))

    def is_short(self, datarecord):
        return (datarecord & 0x80000000) == 0x80000000

    def get_dataid(self, datarecord):
        if self.is_short(datarecord):
            return datarecord & 0xfc000000
        else:
            return datarecord & 0xfffc0000

    def get_length(self, datarecord):
        if self.is_short(datarecord):
            return 1
        else:
            return datarecord & 0x3ffff

    def send(self, msg):
        totalsent = 0
        while totalsent < len(msg):
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError('socket connection broken')

            totalsent += sent

    def recv(self, size):
        msg = ''
        while len(msg) < size:
            chunk = self.sock.recv(size-len(msg))
            if chunk == '':
                raise RuntimeError('socket connection broken')
            msg += chunk
        return msg

    def recv_record(self):
        rec, = struct.unpack('I',self.recv(4))

        if self.is_short(rec):
            return self.get_dataid(rec), rec & 0x3ffffff
        else:
            # -1 because data record counts
            size = self.get_length(rec)*4 - 4

            return self.get_dataid(rec), self.recv(size)

expire = 60

cmos = lambda: None # just a mock object
cmos.lock = Lock()
cmos.items = []

base = lambda: None # just a mock object
base.lock = Lock()
base.items = []

def update(obj):
    with obj.lock:
        now = time.time()
        obj.items = filter(lambda x: x[2] > now - expire, obj.items)

    group = defaultdict(list)

    for k, v, t in obj.items:
        group[k].append(v)

    obj.max = dict((k, max(v)) for k, v in group.iteritems())
    obj.avg = dict((k, sum(v)/len(v)) for k, v in group.iteritems())
    obj.now = dict((k, v[-1]) for k, v in group.iteritems())

def callback(item):
    key = item['key']
    crate = item['crate']

    if key == 'cmos':
        with cmos.lock:
            for j, card in item['rate'].iteritems():
                for k, rate in card.iteritems():
                    index = (crate << 16) | (j << 8) | k
                    cmos.items.append((index,rate,time.time()))
        update(cmos)
    elif key == 'base':
        with base.lock:
            for j, card in item['adc'].iteritems():
                for k, adc in card.iteritems():
                    index = (crate << 16) | (j << 8) | k
                    base.items.append((j,adc,time.time()))
        update(base)

c = CMOSThread(callback)
c.start()
