from __future__ import division
from websno.stream import OrcaJSONStream
from threading import Timer, Lock
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
    counts = np.frombuffer(rec[80:80+8*32*4], dtype=np.uint32)
    date_string = rec[21*4+8*32*4-4:].strip('\x00')
    timestamp = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    return crate, slot_mask, channel_mask, delay, error_flags, counts, timestamp

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

    Timer(5,update,args=(obj,)).start()

def callback(output):
    for item in output:
        if 'key' in item and item['key'] == 'cmos_rate':
            crate, card = item['crate_num'], item['slot_num']
            rate = item['v']['rate']

            with cmos.lock:
                for i in range(len(rate)):
                    j = (crate << 16) | (card << 8) | i
                    cmos.items.append((j,rate[i],time.time()))

        if 'key' in item and item['key'] == 'pmt_base_current':
            crate, card = item['crate_num'], item['slot_num']
            rate = item['v']['adc']

            with base.lock:
                for i in range(len(rate)):
                    j = (crate << 16) | (card << 8) | i
                    base.items.append((j,rate[i],time.time()))

orca_stream = OrcaJSONStream('tcp://localhost:5028',callback)
orca_stream.start()

update(cmos)
update(base)
