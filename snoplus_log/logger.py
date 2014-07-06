import logging
import logging.handlers
from flask import Flask, request
app = Flask(__name__)
from datetime import datetime
from redis import Redis
import json
from os.path import join
from minard.views import PROGRAMS

logging.addLevelName(21, 'SUCCESS')

redis = Redis()

PROGRAM_NAMES = [prog.name for prog in PROGRAMS]

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

@app.route('/', methods=['POST'])
def log():
    """
    Log a message to disk and optionally set an alarm. The POST request
    should have the arguments 'name', 'level', and 'message'. If the
    argument 'notify' is present or level >= 3, the message will trigger an
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
        id = redis.incr('/alarms/count') - 1

        alarm = {'id'     : id,
                 'level'  : lvl,
                 'message': msg,
                 'time'   : datetime.now().isoformat()}

        redis.setex('/alarms/{id}'.format(id=id), json.dumps(alarm), 24*60*60)

    return 'ok\n'

if __name__ == '__main__':
    # just for testing
    app.run(port=50001,debug=True)
