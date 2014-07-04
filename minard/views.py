from __future__ import division
from __future__ import print_function
from minard import app
from flask import render_template, jsonify, request, redirect, url_for
from datetime import datetime
from itertools import product
import time
from redis import Redis
import sys
from os.path import join
import json
from tools import total_seconds, parseiso
import requests
from collections import deque

redis = Redis()

@app.route('/view_log/<name>')
def view_log(name):
    return render_template('view_log.html', name=name)

@app.route('/log', methods=['POST'])
def log():
    """Forward a POST request to the log server at port 50001."""
    resp = requests.post('http://127.0.0.1:50001', headers=request.headers, data=request.form)
    return resp.content, resp.status_code, resp.headers.items()

@app.route('/tail')
def tail():
    name = request.args.get('name', None)

    if name is None:
        return 'must specify name', 400

    seek = request.args.get('seek', None, type=int)

    filename = join('/var/log/snoplus', name + '.log')

    try:
        f = open(filename)
    except IOError:
        return "couldn't find log file {filename}".format(filename=filename), 400

    if seek is None:
        # return last 100 lines
        lines = deque(f, maxlen=100)
    else:
        pos = f.tell()
        f.seek(0,2)
        end = f.tell()
        f.seek(pos)

        if seek > end:
            # log file rolled over
            try:
                prev_logfile = open(filename + '.1')
                prev_logfile.seek(seek)
                # add previous log file lines
                lines = prev_logfile.readlines()
            except IOError:
                return 'seek > log file length', 400

            # add new lines
            lines.extend(f.readlines())
        else:
            # seek to last position and readlines
            f.seek(seek)
            lines = f.readlines()

    return jsonify(seek=f.tell(), lines=list(lines))

@app.route('/')
def index():
    return redirect(url_for('snostream'))

@app.route('/supervisor')
@app.route('/supervisor/<path:path>')
def supervisor(path=None):
    if path is None:
        return redirect(url_for('supervisor', path='index.html'))

    resp = requests.get('http://127.0.0.1:9001' + request.full_path[11:])
    return resp.content, resp.status_code, resp.headers.items()

@app.route('/doc/')
@app.route('/doc/<filename>')
@app.route('/doc/<dir>/<filename>')
@app.route('/doc/<dir>/<subdir>/<filename>')
def doc(dir='', subdir='', filename='index.html'):
    path = join('doc', dir, subdir, filename)
    return app.send_static_file(path)

@app.route('/snostream')
def snostream():
    if not request.args.get('step'):
        return redirect(url_for('snostream',step=1,height=20,_external=True))
    step = request.args.get('step',1,type=int)
    height = request.args.get('height',40,type=int)
    return render_template('snostream.html',step=step,height=height)

@app.route('/nhit')
def nhit():
  return render_template('nhit.html')

@app.route('/l2_filter')
def l2_filter():
    if not request.args.get('step'):
        return redirect(url_for('l2_filter',step=1,height=20,_external=True))
    step = request.args.get('step',1,type=int)
    height = request.args.get('height',40,type=int)
    return render_template('l2_filter.html',step=step,height=height)

@app.route('/detector')
def detector():
    return render_template('detector.html')

@app.route('/daq/<name>')
def channels(name):
    if name == 'cmos':
        return render_template('channels.html', name=name, threshold=5000)
    elif name == 'base':
        return render_template('channels.html', name=name, threshold=80)

@app.route('/alarms')
def alarms():
    return render_template('alarms.html')

@app.route('/builder')
def builder():
    return render_template('builder.html')

CHANNELS = [crate << 9 | card << 5 | channel \
            for crate, card, channel in product(range(20),range(16),range(32))]

@app.route('/query')
def query():
    name = request.args.get('name','',type=str)

    if name == 'dispatcher':
        return jsonify(name=redis.get('dispatcher'))

    if name == 'nhit':
        start = request.args.get('start',type=parseiso)

        now = int(time.time())

        p = redis.pipeline()
        for i in range(start,now):
            p.lrange('events/id:{0:d}:name:nhit'.format(i),0,-1)
        nhit = sum(p.execute(),[])
        return jsonify(value=nhit)

    if name == 'tail_log':
        start = request.args.get('id',None,type=int)
        stop = int(redis.get('builder/global:next'))

        if start is None or start > stop:
            start = stop - 100

        p = redis.pipeline()
        for i in range(start,stop):
            p.get('builder/id:%i:msg' % i)
        value = map(lambda x: x if x is not None else '',p.execute())
        return jsonify(value=value,id=stop)

    if name == 'occupancy':
        now = int(time.time())

        occ = []
        p = redis.pipeline()
        for channel in CHANNELS:
            p.get('events/id:{0:d}:channel:{1:d}'.format(now//60-1,channel))
        occ = p.execute()

        count = redis.get('events/id:{0:d}:count'.format(now//60-1))

        if count is not None:
            count = int(count)
        else:
            count = 0

        occ = [int(n)/count if n else 0 for n in occ]

        return jsonify(values=occ)

    if name == 'cmos' or name == 'base':
        p = redis.pipeline()
        for index in CHANNELS:
            p.get('%s/index:%i:value' % (name,index))
        values = p.execute()

        return jsonify(value=values)

@app.route('/get_alarm')
def get_alarm():
    try:
        latest = int(redis.get('/alarms/count'))
    except TypeError:
        return jsonify(alarms=[])

    if 'start' in request.args:
        start = request.args.get('start',type=int)

        if start < 0:
            start = latest - 1
    else:
        start = max(latest-100,0)

    alarms = []
    for i in range(start,latest):
        value = redis.get('/alarms/{0:d}'.format(i))

        if value:
            alarms.append(json.loads(value))

    return jsonify(alarms=alarms)

@app.route('/set_alarm', methods=['POST'])
def set_alarm():
    lvl = int(request.form['level'])
    msg = request.form['message']
    now = datetime.now().isoformat()

    if not 0 <= lvl <= 3:
        return 'level must be in [0,3]\n', 400

    id = redis.incr('/alarms/count')-1

    if len(msg) > 1024:
        msg = msg[:1024] + '...'

    alarm = {'id': id, 'level': lvl, 'message': msg, 'time': now}

    key = '/alarms/{0:d}'.format(id)
    redis.set(key, json.dumps(alarm))
    # expire alarms after 24 hours
    redis.expire(key, 24*60*60)

    return 'ok\n'

@app.route('/metric')
def metric():
    args = request.args

    expr = args.get('expr',type=str)
    start = args.get('start',type=parseiso)
    stop = args.get('stop',type=parseiso)
    now_client = args.get('now',type=parseiso)
    # convert ms -> sec
    step = args.get('step',type=int)//1000

    now = int(time.time())

    # adjust for clock skew
    dt = now_client - now
    start -= dt
    stop -= dt

    if step > 3600:
        t = 3600
    elif step > 60:
        t = 60
    else:
        t = 1

    if expr in ('gtid', 'run', 'subrun', 'heartbeat','l2-heartbeat'):
        p = redis.pipeline()
        for i in range(start,stop,step):
            p.get('stream/int:{0:d}:id:{1:d}:name:{2}'.format(t,i//t,expr))
        values = p.execute()
        return jsonify(values=values)

    try:
        trig, type = expr.split('-')
    except ValueError:
        trig = expr
        type = None

    p = redis.pipeline()
    for i in range(start,stop,step):
        if type is None:
            p.get('stream/int:{0:d}:id:{1:d}:name:{2}'.format(t,i//t,trig))
        else:
            p.get('stream/int:{0:d}:id:{1:d}:name:{2}:{3}'.format(t,i//t,trig,type))
    values = p.execute()

    if type is not None:
        p = redis.pipeline()
        for i in range(start,stop,step):
            p.get('stream/int:{0:d}:id:{1:d}:name:{2}'.format(t,i//t,trig))
        counts = p.execute()
        values = [float(a)/int(b) if a or b else 0 for a, b in zip(values,counts)]
    else:
        values = map(lambda x: int(x)/t if x else 0, values)

    return jsonify(values=values)

