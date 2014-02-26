from __future__ import division
from threading import Timer, Lock, Thread
from xml.etree.ElementTree import XML
from itertools import izip_longest
from datetime import datetime, timedelta
import sys
import socket
import struct
import atexit
import zmq
from multiprocessing import Process
import numpy as np
from redis import Redis
from functools import partial
import time

def strpiso(string):
    try:
        return datetime.strptime(string,'%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        return datetime.strptime(string,'%Y-%m-%dT%H:%M:%S')

redis = Redis()

CMOS_ID = 1310720
BASE_ID = 1048576

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
    print timestamp
    sys.stdout.flush()
    return crate, slot_mask, channel_mask, delay, error_flags, counts, timestamp

def parse_base(rec):
    crate, slot_mask = struct.unpack('II', rec[:8])
    channel_mask = np.frombuffer(rec[8:8+4*16], dtype=np.uint32)
    error_flags = struct.unpack('I',rec[72:72+4])
    counts = np.frombuffer(rec[76:76+16*32], dtype=np.uint8).reshape((16,-1))
    busy = np.frombuffer(rec[76+16*32:76+16*32+16*32], dtype=np.uint8).reshape((16,-1))
    date_string = rec[76+2*16*32:].strip('\x00')
    timestamp = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    print timestamp
    sys.stdout.flush()
    return crate, slot_mask, channel_mask, error_flags, counts, busy, timestamp

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

def orca_producer(hostname='localhost', port=44666):
    socket = Socket()
    socket.connect(hostname, port)

    cmos_context = zmq.Context()
    cmos = cmos_context.socket(zmq.PUSH)
    cmos.bind('tcp://127.0.0.1:5557')

    base_context = zmq.Context()
    base = base_context.socket(zmq.PUSH)
    base.bind('tcp://127.0.0.1:5558')

    while True:
        id, rec = socket.recv_record()
        if id == CMOS_ID:
            print 'cmos'
            sys.stdout.flush()

            cmos.send_pyobj((id,rec))

        if id == BASE_ID:
            print 'base'
            sys.stdout.flush()

            base.send_pyobj((id,rec))

def orca_consumer(port):
    pull_context = zmq.Context()
    pull = pull_context.socket(zmq.PULL)
    pull.connect('tcp://127.0.0.1:%s' % port)

    print 'connecting'

    while True:
        id, rec = pull.recv_pyobj()

        if id == CMOS_ID:
            crate, slotmask, channelmask, delay, error_flags, counts, timestamp = \
                parse_cmos(rec)

            p = redis.pipeline()
            for i, slot in enumerate(i for i in range(16) if (slotmask >> i) & 1):
                for j, value in enumerate(map(int,counts[i])):
                    if not channelmask[slot] & (1 << j) or value >> 31:
                        continue

                    index = crate << 16 | slot << 8 | j

                    prev_count = redis.get('cmos/index:%i:count' % index)

                    expire = int(time.time() + 10*60)

                    if prev_count is not None:
                        prev_timestamp = strpiso(redis.get('cmos/index:%i:time' % index))
                        prev_count = int(prev_count)
                        try:
                            rate = (value-prev_count)/total_seconds(timestamp-prev_timestamp)
                        except ZeroDivisionError as e:
                            print 'ZeroDivisonError %s' % e
                            continue
                        p.set('cmos/index:%i:value' % index, int(rate))
                        p.expireat('cmos/index:%i:value' % index,expire)

                    p.set('cmos/index:%i:count' % index, value)
                    p.expireat('cmos/index:%i:count' % index, expire)
                    p.set('cmos/index:%i:time' % index, timestamp.isoformat())
                    p.expireat('cmos/index:%i:time' % index, expire)
            p.execute()

        elif id == BASE_ID:
            crate, slotmask, channelmask, error_flags, counts, busy, timestamp = \
                parse_base(rec)

            p = redis.pipeline()
            for i, slot in enumerate(i for i in range(16) if (slotmask >> i) & 1):
                for j, value in enumerate(map(int,counts[i])):
                    if not channelmask[slot] & (1 << j) or value >> 31:
                        continue

                    index = crate << 16 | slot << 8 | j

                    expire = int(time.time() + 10*60)
                    p.set('base/index:%i:value' % index, value-127)
                    p.expireat('base/index:%i:value' % index, expire)
            p.execute()

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
