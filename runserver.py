#!/usr/bin/env python
from minard import app
import gevent
from gevent.wsgi import WSGIServer
import gevent.monkey
gevent.monkey.patch_all()

server = WSGIServer(('',5000),app)
server.serve_forever()
