import sys
from multiprocessing import Event, Process
from Queue import Queue, Empty
from threading import Thread
import shlex
from subprocess import Popen, PIPE
from redis import Redis
import time
import os
import atexit
from orca import orca_consumer, orca_producer

redis = Redis()

ON_POSIX = 'posix' in sys.builtin_module_names

home = os.environ['HOME']

def enqueue_output(out, queue):
    """Put output in a queue for non-blocking reads."""
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

def tail_worker(stop):
    user = 'snotdaq'
    host = 'snoplusbuilder1.snolab.ca'
    ssh_key = '%s/.ssh/id_rsa_builder' % home
    cmd = shlex.split('ssh -i %s %s@%s tail_log_ssh data_temp' % (ssh_key,user,host))
    p = Popen(cmd, stdout=PIPE,stderr=PIPE, bufsize=1, close_fds=ON_POSIX)

    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout,q))
    t.daemon = True
    t.start()

    while not stop.is_set():
        try:
            line = q.get(timeout=1.0)
            print line
        except Empty:
            continue
        else:
            i = redis.incr('builder/global:next')
            expire = int(time.time() + 10*60)
            redis.set('builder/uid:%i:msg' % i,line)
            redis.expireat('builder/uid:%i:msg' % i,expire)
            if not line:
                break

    p.kill()
    p.wait()

TRIGGER_NAMES = \
['100L','100M','100H','20','20LB','ESUML','ESUMH','OWLN','OWLEL','OWLEH','PULGT','PRESCL',
 'PED','PONG','SYNC','EXTA','EXT2','EXT3','EXT4','EXT5','EXT6','EXT7','EXT8','SRAW','NCD',
 'SOFGT','MISS']

def dispatch_worker(host='surf.sno.laurentian.ca'):
    import ratzdab

    dispatcher = ratzdab.dispatch(host)

    while True:
        o = dispatcher.next(False)

        if not o:
            time.sleep(0.01)
            continue

        if o.IsA() == ratzdab.ROOT.RAT.DS.Root.Class():
            ev = o.GetEV(0)

            p = redis.pipeline()
            p.lrange('gtids',0,-1)
            p.lpush('gtids',ev.eventID)
            p.ltrim('gtids',0,100)
            gtids = map(int,p.execute()[0])

            if ev.eventID in gtids:
                o.IsA().Destructor(o)
                continue

            trigger_word = ev.trigType

            now = int(time.time())

            p = redis.pipeline()
            for t in [1,60,3600]:
                uid = now//t
                expires = now + t*100000
                p.incr('time/{0:d}/{1:d}/trigger:TOTAL:count'.format(t,uid))
                p.expireat('time/{0:d}/{1:d}/trigger:TOTAL:count'.format(t,uid),expires)
                # nhit
                p.incrby('time/{0:d}/{1:d}/trigger:TOTAL:nhits'.format(t,uid),ev.nhits)
                p.expireat('time/{0:d}/{1:d}/trigger:TOTAL:nhits'.format(t,uid),expires)
                # charge
                p.incrbyfloat('time/{0:d}/{1:d}/trigger:TOTAL:q'.format(t,uid),ev.totalQ)
                p.expireat('time/{0:d}/{1:d}/trigger:TOTAL:q'.format(t,uid),expires)
                # run
                p.set('time/{0:d}/{1:d}/run'.format(t,uid),o.runID)
                p.expireat('time/{0:d}/{1:d}/run'.format(t,uid),expires)
                # subrun
                p.set('time/{0:d}/{1:d}/subrun'.format(t,uid),o.subRunID)
                p.expireat('time/{0:d}/{1:d}/subrun'.format(t,uid),expires)
                # gtid
                p.set('time/{0:d}/{1:d}/gtid'.format(t,uid),ev.eventID)
                p.expireat('time/{0:d}/{1:d}/gtid'.format(t,uid),expires)

            p.execute()

            p = redis.pipeline()
            for i in range(26):
                if ev.trigType & (1 << i):
                    name = TRIGGER_NAMES[i]
                    for t in [1,60,3600]:
                        uid = now//t
                        expires = now + t*100000
                        p.incr('time/{0:d}/{1:d}/trigger:{2}:count'.format(t,uid,name))
                        p.expireat('time/{0:d}/{1:d}/trigger:{2}:count'.format(t,uid,name),expires)
                        # nhit
                        p.incrby('time/{0:d}/{1:d}/trigger:{2}:nhits'.format(t,uid,name),ev.nhits)
                        p.expireat('time/{0:d}/{1:d}/trigger:{2}:nhits'.format(t,uid,name),expires)
                        # charge
                        p.incrbyfloat('time/{0:d}/{1:d}/trigger:{2}:q'.format(t,uid,name),ev.totalQ)
                        p.expireat('time/{0:d}/{1:d}/trigger:{2}:q'.format(t,uid,name),expires)
            p.execute()
            o.IsA().Destructor(o)

if __name__ == '__main__':
    _stop = Event()
    tail_process = Process(target=tail_worker,args=(_stop,))
    # process dies with the server
    #tail_process.daemon = True
    tail_process.start() 
    #tail_process.join()

    @atexit.register
    def stop_worker():
        # try to gracefully exit
        _stop.set()
        tail_process.join()

    processes = [Process(target=orca_producer),
                 Process(target=orca_consumer,args=(5557,)),
                 Process(target=orca_consumer,args=(5557,)),
                 Process(target=orca_consumer,args=(5558,)),
                 Process(target=orca_consumer,args=(5558,)),
                 Process(target=dispatch_worker),
                 Process(target=dispatch_worker)]

    def start():
        for process in processes:
            process.start()

    @atexit.register
    def stop():
        for process in processes:
            process.terminate()

    start()
    while True:
        for process in processes[:]:
            if not process.is_alive():
                processes.remove(process)
                p = Process(target=process._target,args=process._args)
                processes.append(p)
                p.start()

            print 'sleep'
            time.sleep(1)

    processes[0].join()
