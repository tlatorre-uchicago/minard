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

redis = Redis()

ON_POSIX = 'posix' in sys.builtin_module_names

home = os.environ['HOME']

def enqueue_output(out, queue):
    """Put output in a queue for non-blocking reads."""
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()

def tail_worker(stop):
    p = Popen(shlex.split('ssh -i %s/.ssh/id_rsa_builder -t -t snotdaq@snoplusbuilder1.snolab.ca tail_log data_temp' % home), stdout=PIPE, bufsize=1, close_fds=ON_POSIX)

    q = Queue()
    t = Thread(target=enqueue_output, args=(p.stdout,q))
    t.daemon = True
    t.start()

    while not stop.is_set():
        try:
            line = q.get(timeout=1.0)
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

stop = Event()
tail_process = Process(target=tail_worker,args=(stop,))
# process dies with the server
tail_process.daemon = True
tail_process.start() 
tail_process.join()

@atexit.register
def stop_worker():
    # try to gracefully exit
    stop.set()
    tail_process.join()
