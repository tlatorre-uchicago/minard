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
    cmd = shlex.split('ssh -i %s %s@%s tail_log data_temp' % (ssh_key,user,host))
    p = Popen(cmd, stdout=PIPE,stderr=PIPE)#, bufsize=1, close_fds=ON_POSIX)
    #p = Popen(shlex.split('tail -f /tmp/minard_access.log'),stdout=PIPE)

    #q = Queue()
    #t = Thread(target=enqueue_output, args=(p.stdout,q))
    #t.daemon = True
    #t.start()

    while not stop.is_set():
        try:
            line = p.stdout.readline()#q.get(timeout=1.0)
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
            continue

        if o.IsA() == ratzdab.ROOT.RAT.DS.Root.Class():
            ev = o.GetEV(0)
            trigger_word = ev.trigType

            now = int(time.time())
            min = now//60
            sec_expires = now + 60*60
            min_expires = now + 60*60*24

            p = redis.pipeline()
            p.incr('time/sec/{0:d}/trigger:TOTAL:count'.format(now))
            p.expireat('time/sec/{0:d}/trigger:TOTAL:count'.format(now),sec_expires)
            p.incr('time/min/{0:d}/trigger:TOTAL:count'.format(min))
            p.expireat('time/min/{0:d}/trigger:TOTAL:count'.format(now),min_expires)
            p.execute()

            p = redis.pipeline()
            for i in range(26):
                if trigger_word & (1 << i):
                    name = TRIGGER_NAMES[i]
                    p.incr('time/sec/{0:d}/trigger:{1}:count'.format(now,name))
                    p.expireat('time/sec/{0:d}/trigger:{1}:count'.format(now,name),sec_expires)
                    p.incr('time/min/{0:d}/trigger:{1}:count'.format(min,name))
                    p.expireat('time/min/{0:d}/trigger:{1}:count'.format(min,name),min_expires)
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
