#!/usr/bin/env python
from __future__ import print_function
import urllib
import urllib2
import base64
import threading
import logging
import socket
from itertools import starmap, repeat

NOTIFY = {'notify': True}

def repeatfunc(func, times=None, *args):
    """Repeat calls to func with specified arguments.

    Example:  repeatfunc(random.random)
    """
    if times is None:
        return starmap(func, repeat(args))
    return starmap(func, repeat(args, times))

def post(url, data, auth=None, retries=10):
    """
    Sends a POST request containing `data` to url. `auth` should be a
    tuple containing (username, password).
    """
    if not url.startswith('http://'):
        url = 'http://' + url

    request = urllib2.Request(url)
    if auth:
        base64string = base64.encodestring('%s:%s' % auth).replace('\n','')
        request.add_header('Authorization', 'Basic %s' % base64string)

    params = urllib.urlencode(data)
    for i in range(retries):
        try:
            response = urllib2.urlopen(request, params)
        except urllib2.URLError, e:
            # python 2.6
            if i < retries-1:
                if isinstance(e, socket.timeout):
                    # try again
                    continue
                else:
                    # not timeout exception
                    raise
            else:
                # raise exception on last iteration
                raise
        except socket.timeout, e:
            # python 2.7
            if i < retries-1:
                continue
            else:
                # raise exception on last iteration
                raise

        return response.read()

class HTTPHandler(logging.Handler):
    """
    Sends log messages to the monitoring server using POST requests.
    If the log record has an attribute 'notify', then the log message
    will trigger an alert on the monitoring site.

    Example:
        logger.addHandler(HTTPHandler(name,host))
        logger.info("Hello, world!")
        logger.info("Hello, world!", extra=NOTIFY)
    """
    def __init__(self, name, host, auth=None):
        logging.Handler.__init__(self)
        self.name = name
        self.host = host
        self.auth = auth

    def emit(self, record):
        data = {'name': self.name, 'level': record.levelno, 'message': record.msg}
        if hasattr(record,'notify') and record.notify:
            data['notify'] = True
        response = post('{host}/monitoring/log'.format(host=self.host), data, self.auth)
        if response.strip() != 'ok':
            raise Exception('POST got response {response}'.format(response=response))

def post_heartbeat(host, name, auth=None):
    """
    Sends a POST request every second to the monitoring server
    indicating that the process is still running.
    """
    timer = threading.Timer(1.0, post_heartbeat, args=(host, name, auth))
    # set the thread as a daemon to exit the program cleanly
    # when the main thread finishes
    timer.daemon = True
    timer.start()
    data = {'name': name, 'status': 'ok'}
    response = post('{host}/monitoring/heartbeat'.format(host=host), data, auth)
    if response.strip() != 'ok':
        raise Exception('POST got response {response}'.format(response=response))

def set_up_root_logger(host, name, auth=None):
    """Sets up the root logger to send log messages to the monitoring server."""
    root_logger = logging.getLogger()
    root_logger.addHandler(HTTPHandler(name, host, auth))
    root_logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    import getpass
    import sys
    import optparse
    import sys
    import traceback

    parser = optparse.OptionParser()
    parser.add_option('--local', action='store_true', dest='local',
                      help='post heartbeat/logs to localhost')
    options, args = parser.parse_args()

    if len(args) < 1:
        sys.exit("must specify name")

    name = args[0]

    if options.local:
        host = 'localhost:50000'
        auth = None
    else:
        host = 'snopl.us'
        passwd = getpass.getpass()
        auth = 'snoplus', passwd

    post_heartbeat(host, name, auth)
    set_up_root_logger(host, name, auth)

    for line in repeatfunc(sys.stdin.readline):
        if not line:
            break
        try:
            logging.info(line.strip())
        except urllib2.URLError, e:
            print(traceback.format_exc(), file=sys.stderr)
            continue
