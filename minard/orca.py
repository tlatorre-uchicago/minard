from __future__ import division
from xml.etree.ElementTree import XML
from itertools import izip_longest, repeat
import socket
import struct
import zmq
from datetime import datetime, timedelta
import numpy as np
from redis import Redis
import time
from minard.redistools import hmincrby, hmincrbyfloat, hdivh, hmincr, setavgmax
from minard.timeseries import HASH_INTERVALS, HASH_EXPIRE
from minard.tools import parseiso

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
    counts = np.frombuffer(rec[80:80+8*32*4], dtype=np.uint32)
    date_string = rec[21*4+8*32*4-4:].strip('\x00')
    timestamp = parseiso(date_string)
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

def unpack_index(index):
    """Returns (crate, card, channel) for a channel index."""
    return index >> 9, index >> 5 & 0xf, index & 0x1f

def orca_consumer(port):
    pull_context = zmq.Context()
    pull = pull_context.socket(zmq.PULL)
    pull.connect('tcp://127.0.0.1:%s' % port)

    while True:
        id, rec = pull.recv_pyobj()

        now = int(time.time())

        if id == CMOS_ID:
            crate, slotmask, channelmask, delay, error_flags, counts, timestamp = \
                parse_cmos(rec)

            cmos_rates = {}

            cards = np.array([i for i in range(16) if (slotmask >> i) & 1])
            indices = (crate << 9 | cards[:,np.newaxis] << 5 | np.arange(32)).flatten()

            last_counts = redis.hmget('cmos:count', indices)
            last_timestamps = redis.hmget('cmos:timestamp', indices)

            # set new times/counts
            p = redis.pipeline()
            p.hmset('cmos:count', dict(zip(indices, counts)))
            p.hmset('cmos:timestamp', dict(zip(indices, repeat(timestamp))))
            p.execute()

            for index, count, last_count, last_timestamp in \
                    zip(indices, counts, last_counts, last_timestamps):
                _, card, channel = unpack_index(index)

                if (not channelmask[card] & (1 << channel)
                    or count >> 31
                    or last_count is None):
                    continue

                # time delta between cmos counts (seconds)
                dt = timestamp - float(last_timestamp)

                if 0 < dt < 10 and count > int(last_count):
                    rate = (count-int(last_count))/dt
                    # time series
                    cmos_rates[index] = rate

            p = redis.pipeline()
            for interval in HASH_INTERVALS:
                key = 'ts:%i:%i:cmos' % (interval, now//interval)
                hmincrbyfloat(key + ':sum', cmos_rates, client=p)
                hmincr(key + ':count', cmos_rates.keys(), client=p)
                p.expire(key + ':sum', interval*2)
                p.expire(key + ':count', interval*2)
                prev = now//interval - 1
                prev_key = 'ts:%i:%i:cmos' % (interval,prev)
                if redis.incr(prev_key + ':lock') == 1:
                    hdivh(prev_key, prev_key + ':sum', prev_key + ':count', range(10240), client=p)
                    keys = setavgmax(prev_key, client=p)
                    for k in keys:
                        p.expire(k, HASH_EXPIRE*interval)
                    p.expire(prev_key, HASH_EXPIRE*interval)
                    p.expire(prev_key + ':lock', interval*2)
            p.execute()

        elif id == BASE_ID:
            crate, slotmask, channelmask, error_flags, counts, busy, timestamp = \
                parse_base(rec)

            base_currents = {}

            for i, slot in enumerate(i for i in range(16) if (slotmask >> i) & 1):
                for j, value in enumerate(map(int,counts[i])):
                    if not channelmask[slot] & (1 << j) or value >> 31:
                        continue

                    index = crate << 9 | slot << 5 | j

                    base_currents[index] = value-127

            p = redis.pipeline()
            for interval in HASH_INTERVALS:
                key = 'ts:%i:%i:base' % (interval, now//interval)
                hmincrby(key + ':sum', base_currents, client=p)
                hmincr(key + ':count', base_currents.keys(), client=p)
                p.expire(key + ':sum', interval)
                p.expire(key + ':count', interval)
                prev_key = 'ts:%i:%i:base' % (interval,now//interval-1)
                if redis.incr(prev_key + ':lock') == 1:
                    hdivh(prev_key, prev_key + ':sum', prev_key + ':count', range(10240), client=p)
                    keys = setavgmax(prev_key, client=p)
                    for k in keys:
                        p.expire(k, HASH_EXPIRE*interval)
                    p.expire(prev_key, HASH_EXPIRE*interval)
                    p.expire(prev_key + ':lock', interval)
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
