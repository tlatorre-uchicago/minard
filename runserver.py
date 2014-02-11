#!/usr/bin/env python
import sys
from subprocess import call

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 50000

    call(['gunicorn','-b','0.0.0.0:%i' % port,'minard:app','-D','--access-logfile','/tmp/minard_access.log','--error-logfile','/tmp/minard_error.log','-w','4'])
