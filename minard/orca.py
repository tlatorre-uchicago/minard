from __future__ import division
from threading import Timer, Lock, Thread
from xml.etree.ElementTree import XML
from itertools import izip_longest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import select
from sqlalchemy import event
import sys
import socket
import struct
import atexit
import zmq
from multiprocessing import Process
import numpy as np
from dbinfo import user, passwd, host, name

CMOS_ID = 1310720
BASE_ID = 1048576

def _fk_pragma_on_connect(dbapi_con, con_record):
    pass
    #dbapi_con.execute('PRAGMA journal_mode = MEMORY')
    #dbapi_con.execute('PRAGMA synchronous = OFF')

Base = declarative_base()
engine = create_engine('mysql://snoplus:%s@%s/test2' % (passwd,host), echo=False)

event.listen(engine,'connect',_fk_pragma_on_connect)

class BaseCurrent(Base):
    __tablename__ = 'base_current'

    id = Column(Integer, primary_key=True)
    index = Column(Integer, nullable=False)
    value = Column(SmallInteger, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    def __init__(self, index, value, timestamp):
        self.index = index
        self.value = value
        self.timestamp = timestamp

    def __getitem__(self, i):
        return [self.id, self.index, self.value, self.timestamp][i]

    def __repr__(self):
        return "<BaseCurrent(index=%i,value=%i)>" % (self.index, self.value) 

class CMOSRate(Base):
    __tablename__ = 'cmos_rate'

    id = Column(Integer, primary_key=True)
    index = Column(Integer, nullable=False)
    value = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    def __init__(self, index, value, timestamp):
        self.index = index
        self.value = value
        self.timestamp = timestamp

    def __iter__(self):
        yield self.index
        yield self.value
        yield self.timestamp

    def __getitem__(self, i):
        return [self.id, self.index, self.value, self.timestamp][i]

    def __repr__(self):
        return "<CMOSRate(index=%i,value=%i)>" % (self.index, self.value) 

Base.metadata.create_all(engine)

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

def orca_producer(hostname='snoplusdaq1', port=44666):
    socket = Socket()
    socket.connect(hostname, port)

    push_context = zmq.Context()
    push = push_context.socket(zmq.PUSH)
    push.bind('tcp://127.0.0.1:5557')

    while True:
        id, rec = socket.recv_record()
        if id == CMOS_ID or id == BASE_ID:
            print 'sent'
            sys.stdout.flush()

            push.send_pyobj((id,rec))

def orca_consumer():
    pull_context = zmq.Context()
    pull = pull_context.socket(zmq.PULL)
    pull.connect('tcp://127.0.0.1:5557')

    engine = create_engine('mysql://snoplus:%s@%s/test2' % (passwd,host), echo=False)
    Session = scoped_session(sessionmaker(bind=engine,autoflush=False,autocommit=False))

    cmos = {}

    while True:
        id, rec = pull.recv_pyobj()

        session = Session()
        if id == CMOS_ID:
            crate, slotmask, channelmask, delay, error_flags, counts, timestamp = \
                parse_cmos(rec)

            for i, slot in enumerate(i for i in range(16) if (slotmask >> i) & 1):
                for j, value in enumerate(map(int,counts[i])):
                    if not channelmask[slot] & (1 << j) or value >> 31:
                        continue

                    index = crate << 16 | slot << 8 | j

                    if index in cmos:
                        count = cmos[index]
                        rate = (value-count[0])/total_seconds(timestamp-count[1])

                        session.add(CMOSRate(index,rate,timestamp))

                    cmos[index] = value, timestamp
        elif id == BASE_ID:
            crate, slotmask, channelmask, error_flags, counts, busy, timestamp = \
                parse_base(rec)

            for i, slot in enumerate(i for i in range(16) if (slotmask >> i) & 1):
                for j, value in enumerate(map(int,counts[i])):
                    if not channelmask[slot] & (1 << j) or value >> 31:
                        continue

                    index = crate << 16 | slot << 8 | j

                    session.add(BaseCurrent(index,value-127,timestamp))

        expire = datetime.now() - timedelta(minutes=5) + timedelta(hours=5)
        # delete rows that are more than 5 minutes old
        session.query(CMOSRate).filter(CMOSRate.timestamp < expire).delete()
        session.query(BaseCurrent).filter(BaseCurrent.timestamp < expire).delete()
        try:
            session.commit()
        except Exception as e:
            print e
            session.rollback()
        finally:
            session.close()

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

processes = []
processes.append(Process(target=orca_producer))
for i in range(4):
    processes.append(Process(target=orca_consumer))

def start():
    for process in processes:
        process.start()

@atexit.register
def stop():
    for process in processes:
        process.terminate()

Session = scoped_session(sessionmaker(bind=engine,autoflush=False,autocommit=False))

if __name__ == '__main__':
    start()
    processes[0].join()
