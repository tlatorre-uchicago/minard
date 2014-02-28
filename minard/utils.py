from subprocess import call, PIPE, Popen
import os

def pkill(name):
    p = Popen(['pgrep','-f',name],stdout=PIPE)
    for pid in map(int,p.communicate()[0].split()):
        if pid != os.getpid():
            print 'killing process %i' % pid
            call(['kill',str(pid)])
