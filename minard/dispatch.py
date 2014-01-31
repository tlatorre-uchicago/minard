from collections import deque
import time
from threading import Thread, Event
import ratzdab

ev = deque(maxlen=1000)

class ZDABDispatch(Thread):
    def __init__(self, hostname):
        Thread.__init__(self)
        self.hostname = hostname
        self._stop = Event()
        self.dispatcher = ratzdab.dispatch(self.hostname)

    def stop(self):
        self._stop.set()

    def run(self):
        while not self._stop.isSet():
            try:
                o = self.dispatcher.next(False)

                if not o:
                    time.sleep(0.1)
                    continue

                ev.appendleft(o.GetEV(0))
            except Exception as e:
                print e
                continue
