#!/usr/bin/env python
import sys
from subprocess import call

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 5000

    call(['gunicorn','-b','0.0.0.0:%i' % port,'minard:app','-D'])
