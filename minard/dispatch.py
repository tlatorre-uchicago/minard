#!/usr/bin/env python
from __future__ import print_function, absolute_import
import time
from redis import Redis
from dispatch import Dispatch, unpack_trigger_type, unpack_header, unpack_pmt_record, RECORD_IDS
from collections import defaultdict
import zmq
import threading
from minard.timeseries import INTERVALS, EXPIRE, HASH_INTERVALS, HASH_EXPIRE
from minard.redistools import hmincrby, hdivk, setavgmax
import random

redis = Redis()

# triggers, note: the order here is important!
# the position of the trigger in the list corresponds to the bit in the
# trigger word.
# http://snopl.us/docs/rat/user_manual/html/node43.html
TRIGGER_NAMES = \
['100L',
 '100M',
 '100H',
 '20',
 '20LB',
 'ESUML',
 'ESUMH',
 'OWLN',
 'OWLEL',
 'OWLEH',
 'PULGT',
 'PRESCL',
 'PED',
 'PONG',
 'SYNC',
 'EXTA',
 'EXT2',
 'EXT3',
 'EXT4',
 'EXT5',
 'EXT6',
 'EXT7',
 'EXT8',
 'SRAW',
 'NCD',
 'SOFGT',
 'MISS']

def post(host):
    """Posts the dispatcher name to redis every 20 seconds."""
    redis.setex('dispatcher',host,60)
    timer = threading.Timer(20.0, post, args=[host])
    timer.daemon = True
    timer.start()

def push(host):
    """
    Connects to a dispatcher at ip address `host` and pushes the records to
    a ZMQ socket.
    """
    dispatcher = Dispatch(host)

    post(host)

    context = zmq.Context()
    zmq_socket = context.socket(zmq.PUSH)
    zmq_socket.bind('tcp://127.0.0.1:5560')

    for record in dispatcher:
        zmq_socket.send_pyobj((int(time.time()),record.raw))

def flush_cache(cache, cache_set, cache_nhit, cache_pmt, time):
    # for docs on redis pipeline see http://redis.io/topics/pipelining
    p = redis.pipeline()

    for name, hash in cache.items():
        keys = ['ts:%i:%i:%s' % (interval, time//interval, name)
                for interval in INTERVALS]

        if len(hash) > 0:
            hmincrby(keys, hash, client=p)
            
            for key, interval in zip(keys,INTERVALS):
                p.expire(key,interval*EXPIRE)

    for interval in INTERVALS:
        for name, hash in cache_set.items():
            key = 'ts:%i:%i:%s' % (interval, time//interval, name)
            if len(hash) > 0:
                p.hmset(key, hash)
                p.expire(key, interval*EXPIRE)

    keys = ['ts:%i:%i:occupancy:hits' % (interval, time//interval)
            for interval in HASH_INTERVALS]

    if len(cache_pmt) > 0:
        hmincrby(keys, cache_pmt, client=p)

    for interval in HASH_INTERVALS:
        key = 'ts:%i:%i:occupancy' % (interval, time//interval)
        p.incrby(key + ':count', cache['trig']['TOTAL'])
        # expire after just interval, because these will
        # occupancy will be set as hits/count
        p.expire(key + ':hits', interval)
        p.expire(key + ':count', interval)

        prev_key = 'ts:%i:%i:occupancy' % (interval,time//interval-1)
        if redis.incr(prev_key + ':lock') == 1:
            hdivk(prev_key, prev_key + ':hits', prev_key + ':count',
                  range(10240), format='%.2g', client=p)
            keys = setavgmax(prev_key, client=p)
            for k in keys:
                p.expire(k, HASH_EXPIRE*interval)
            p.expire(prev_key, HASH_EXPIRE*interval)
            p.expire(prev_key + ':lock', interval)

    if len(cache_nhit) > 0:
        # nhit distribution
        if len(cache_nhit) > 100:
            # if there are more than 100 events this second
            # randomly sample the nhit from 100 events
            cache_nhit = random.sample(cache_nhit,100)
        # see http://flask.pocoo.org/snippets/71/ for this design pattern
        p.lpush('ts:1:%i:nhit' % time, *cache_nhit)
        p.expire('ts:1:%i:nhit' % time, 3600)

    p.execute()

def pull():
    """Connects to a ZMQ socket and processes the dispatch stream."""
    context = zmq.Context()
    zmq_socket = context.socket(zmq.PULL)
    zmq_socket.connect('tcp://127.0.0.1:5560')

    cache = {}
    cache['trig'] = defaultdict(int)
    cache['trig:nhit'] = defaultdict(int)
    cache['trig:charge'] = defaultdict(int)
    cache_set = {}
    cache_set['trig'] = {}
    cache_nhit = []
    cache_pmt = defaultdict(int)

    then = None

    while True:
        try:
            now, record = zmq_socket.recv_pyobj(zmq.NOBLOCK)
        except zmq.ZMQError:
            record = None
            now = int(time.time())

        if then is None:
            then = now

        if now > then:
            # flush data to redis every second
            flush_cache(cache, cache_set, cache_nhit, cache_pmt, then)

            p = redis.pipeline()
            for interval in INTERVALS:
                key = 'ts:%i:%i:heartbeat' % (interval, then//interval)
                p.setex(key,1,interval*EXPIRE)
            p.execute()

            cache['trig'].clear()
            cache['trig:nhit'].clear()
            cache['trig:charge'].clear()
            cache_set['trig'].clear()
            cache_nhit = []
            cache_pmt.clear()
            then = now

        if record is None:
            # nothing to process, take a break
            time.sleep(0.01)
            continue

        record_id, data = unpack_header(record)

        if record_id != RECORD_IDS['PMT_RECORD']:
            continue

        pmt_gen = unpack_pmt_record(data)

        pev = next(pmt_gen)

        run = pev.RunNumber
        gtid = pev.TriggerCardData.BcGT
        nhit = pev.NPmtHit
        subrun = pev.DaqStatus # seriously :)
        trig = unpack_trigger_type(pev)

        cache_nhit += [nhit]

        qhs_sum = 0
        for pmt in pmt_gen:
            id = 16*32*pmt.CrateID + 32*pmt.BoardID + pmt.ChannelID
            cache_pmt[id] += 1

            qhs_sum += pmt.Qhs

        cache['trig']['TOTAL'] += 1
        cache['trig:nhit']['TOTAL'] += nhit
        cache['trig:charge']['TOTAL'] += qhs_sum
        cache_set['trig']['run'] = run
        cache_set['trig']['subrun'] = subrun
        cache_set['trig']['gtid'] = gtid

        for i, name in enumerate(TRIGGER_NAMES):
            if trig & (1 << i):
                cache['trig'][i] += 1
                cache['trig:nhit'][i] += nhit
                cache['trig:charge'][i] += qhs_sum

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process SNO+ events from a dispatch stream')
    parser.add_argument('action', help='push/pull')
    parser.add_argument('--host', default='builder1.sp.snolab.ca', help='hostname of the dispatcher')
    args = parser.parse_args()

    if args.action == 'push':
        push(args.host)
    else:
        pull()
