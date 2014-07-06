import urllib
import urllib2
import base64
import threading
import logging

def post(url, data, auth=None):
    """
    Sends a POST request containing `data` to url. `auth` should be a
    tuple containing (username, password).
    """
    if not url.startswith('http://'):
        url = 'http://' + url

    request = urllib2.Request(url)
    if auth:
        base64string = base64.encode('%s:%s' % auth).replace('\n','')
        request.add_header('Authorization', 'Basic %s' % base64string)

    params = urllib.urlencode(data)
    response = urllib2.urlopen(request, params)
    return response.read()

class HTTPHandler(logging.Handler):
    def __init__(self, name, host, auth=None):
        logging.Handler.__init__(self)
        self.name = name
        self.host = host
        self.auth = auth


    def log(self, level, msg, *args, **kwargs):
        notify = kwargs.pop('notify', False)
        if notify:
            kwargs['extra'] = {'notify': True}
        logging.Handler.log(self, level, msg, *args, **kwargs)

    def emit(self, record):
        data = {'name': self.name, 'level': record.levelno, 'message': record.msg}
        if record.extra['notify']:
            data['notify'] = True
        response = post('{host}/monitoring/log'.format(host=self.host), data, self.auth)
        if response.strip() != 'ok':
            raise Exception('POST got response {response}'.format(response=response))

def post_heartbeat(host, name, auth=None):
    threading.Timer(5.0, post_heartbeat, args=(name, auth))
    data = {'name': name, 'status': 'ok'}
    response = post('{host}/monitoring/heartbeat'.format(host=host), data, auth)
    if response.strip() != 'ok':
        raise Exception('POST got response {response}'.format(response=response))

if __name__ == '__main__':
    import getpass
    import sys
    import itertools
    import optparse

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
    logging.getLogger().addHandler(HTTPHandler(name, host, auth))

    for line in itertools.starmap(sys.stdin.readline,itertools.repeat([])):
        logging.info(line)
