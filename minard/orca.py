from __future__ import division
from xml.etree.ElementTree import XML
from itertools import izip_longest
import socket
import struct
import zmq
from datetime import datetime, timedelta
import numpy as np
from redis import Redis
import time

CMOS_ID = 1310720
BASE_ID = 1048576

redis = Redis()

# number of seconds to keep CMOS records
EXPIRE = 60

def strpiso(string):
    """Converts an iso string -> python datetime object."""
    try:
        return datetime.strptime(string,'%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        return datetime.strptime(string,'%Y-%m-%dT%H:%M:%S')

def parse_cmos(rec):
    """Parse a CMOS record."""
    crate, slot_mask = struct.unpack('II', rec[:8])
    channel_mask = np.frombuffer(rec[8:8+4*16], dtype=np.uint32)
    delay, error_flags = struct.unpack('II',rec[72:72+2*4])
    counts = np.frombuffer(rec[80:80+8*32*4], dtype=np.uint32).reshape((8,-1))
    date_string = rec[21*4+8*32*4-4:].strip('\x00')
    timestamp = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    return crate, slot_mask, channel_mask, delay, error_flags, counts, timestamp

def parse_base(rec):
    """Parse a base current record."""
    crate, slot_mask = struct.unpack('II', rec[:8])
    channel_mask = np.frombuffer(rec[8:8+4*16], dtype=np.uint32)
    error_flags = struct.unpack('I',rec[72:72+4])
    counts = np.frombuffer(rec[76:76+16*32], dtype=np.uint8).reshape((16,-1))
    busy = np.frombuffer(rec[76+16*32:76+16*32+16*32], dtype=np.uint8).reshape((16,-1))
    date_string = rec[76+2*16*32:].strip('\x00')
    timestamp = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%fZ')
    return crate, slot_mask, channel_mask, error_flags, counts, busy, timestamp

def total_seconds(td):
    """Returns the total number of seconds contained in the duration."""
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

def orca_consumer(port):
    pull_context = zmq.Context()
    pull = pull_context.socket(zmq.PULL)
    pull.connect('tcp://127.0.0.1:%s' % port)

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

                    index = crate << 9 | slot << 5 | j

                    prev_count = redis.get('cmos:%i:count' % index)

                    if prev_count is not None:
                        prev_timestamp = strpiso(redis.get('cmos:%i:time' % index))
                        prev_count = int(prev_count)
                        try:
                            rate = (value-prev_count)/total_seconds(timestamp-prev_timestamp)
                        except ZeroDivisionError as e:
                            print 'ZeroDivisonError %s' % e
                            continue
                        p.setex('cmos:%i:value' % index, int(rate), EXPIRE)

                    p.setex('cmos:%i:count' % index, value, EXPIRE)
                    p.setex('cmos:%i:time' % index, timestamp.isoformat(), EXPIRE)
            p.execute()

        elif id == BASE_ID:
            crate, slotmask, channelmask, error_flags, counts, busy, timestamp = \
                parse_base(rec)

            p = redis.pipeline()
            for i, slot in enumerate(i for i in range(16) if (slotmask >> i) & 1):
                for j, value in enumerate(map(int,counts[i])):
                    if not channelmask[slot] & (1 << j) or value >> 31:
                        continue

                    index = crate << 9 | slot << 5 | j

                    p.setex('base:%i:value' % index, value-127, EXPIRE)
            p.execute()

def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') -> ABC DEF Gxx
    args = [iter(iterable)]*n
    return izip_longest(fillvalue=fillvalue, *args)

def parse_header(header):
    """Parse an ORCA header -> python dictionary."""
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
    """
    Socket object used to communicate with ORCA.
    See `here <http://orca.physics.unc.edu/~markhowe/Data_Format_Viewing/Data_Format.html>`_
    for more information.
    """
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
        """Returns the data id associated with `datarecord`."""
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

def orca_producer(host, port=44666):
    """
    Pushes CMOS and base current records to a ZMQ Push/Pull socket
    to be parsed by other workers. CMOS rates and base currents are
    pushed to ports 5557 and 5558 respectively.
    See `zeromq.org <http://zeromq.org>`_ for more information.
    """
    socket = Socket()
    socket.connect(host, port)

    cmos_context = zmq.Context()
    cmos = cmos_context.socket(zmq.PUSH)
    cmos.bind('tcp://127.0.0.1:5557')

    base_context = zmq.Context()
    base = base_context.socket(zmq.PUSH)
    base.bind('tcp://127.0.0.1:5558')

    while True:
        id, rec = socket.recv_record()
        if id == CMOS_ID:
            cmos.send_pyobj((id,rec))

        if id == BASE_ID:
            base.send_pyobj((id,rec))
