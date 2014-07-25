import logging
import logging.handlers
from snoplus_log import app
from flask import request
from datetime import datetime
from redis import Redis
import json
from os.path import join
from minard.views import PROGRAMS
import time

logging.addLevelName(21, 'SUCCESS')

redis = Redis()

PROGRAM_NAMES = [prog.name for prog in PROGRAMS]

PROGRAM_DICT = dict((p.name, p) for p in PROGRAMS)

def get_logger(name):
    """Returns the logger for `name`."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    filename = join('/var/log/snoplus', name + '.log')
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(filename, maxBytes=5e6, backupCount=10)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    """Log heartbeat."""
    if 'name' not in request.form:
        return "must specify name\n", 400

    name = request.form['name']

    if 'status' not in request.form:
        return "must specify status\n", 400

    status = request.form['status']

    try:
        expire = PROGRAM_DICT[name].expire
    except KeyError:
        return "unknown name\n", 400

    # expire every expire seconds
    redis.setex('heartbeat:{name}'.format(name=name),status,expire)

    up = redis.get('uptime:{name}'.format(name=name))

    if up is None:
        redis.setex('uptime:{name}'.format(name=name),int(time.time()),expire)
    else:
        # still running, update expiration
        redis.expire('uptime:{name}'.format(name=name),expire)

    return 'ok\n'

@app.route('/log', methods=['POST'])
def log():
    """
    Log a message to disk and optionally set an alarm. The POST request
    should have the arguments 'name', 'level', and 'message'. If the
    argument 'notify' is present or level >= 40, the message will trigger an
    alarm.
    """
    name = request.form['name']

    if name not in PROGRAM_NAMES:
        return 'unknown program {name}\n'.format(name=name), 400

    logger = get_logger(name)

    lvl = int(request.form['level'])
    msg = request.form['message']

    # log it to disk
    logger.log(lvl,msg)

    if 'notify' in request.form or lvl >= 40:
        # post to redis
        id = redis.incr('alarms:count') - 1

        alarm = {'id'     : id,
                 'level'  : lvl,
                 'message': msg,
                 'time'   : datetime.now().isoformat()}

        redis.setex('alarms:{id}'.format(id=id), json.dumps(alarm), 24*60*60)

    return 'ok\n'
