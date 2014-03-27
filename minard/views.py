from __future__ import division
from __future__ import print_function
from minard import app
from flask import render_template, jsonify, request, redirect, url_for, send_from_directory
from datetime import datetime, timedelta
from itertools import product
import time
import calendar
from redis import Redis
import sys
from os.path import join

try:
    from minard.database import init_db, db_session
    from minard.models import Clock, L2, Alarms, PMT, Nhit, Position

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

except Exception as e:
    print('failed to load MySQL database',file=sys.stderr)
    print(str(e),file=sys.stderr)

redis = Redis()

def total_seconds(td):
    """Returns the total number of seconds contained in the duration."""
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

def parseiso(timestr):
    """Convert an iso time string -> unix timestamp."""
    dt = datetime.strptime(timestr,'%Y-%m-%dT%H:%M:%S.%fZ')
    return calendar.timegm(dt.timetuple())

@app.route('/')
def index():
    return redirect(url_for('snostream'))

@app.route('/doc/')
@app.route('/doc/<filename>')
@app.route('/doc/_static/<filename>', defaults={'static': True})
def doc(filename='index.html', static=False):
    if static:
        path = join('doc/_static',filename)
    else:
        path = join('doc',filename)

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
    return render_template('l2_filter.html')

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
            for crate, card, channel in product(range(19),range(16),range(32))]

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

        count = int(redis.get('events/id:{0:d}:count'.format(now//60-1)))
        occ = [int(n)/count if n else 0 for n in occ]

        return jsonify(values=occ)

    if name == 'l2_info':
        id = request.args.get('id',None,type=str)

        if id is not None:
            info = db_session.query(L2).filter(L2.id == id).one()
        else:
            # grab latest
            info = db_session.query(L2).order_by(L2.id.desc()).first()

        return jsonify(value=dict(info))

    if name == 'nhit_l2':
        latest = Nhit.latest()
        hist = [getattr(latest,'nhit%i' % i) for i in range(30)]
        bins = range(5,300,10)
        result = dict(zip(bins,hist))
        return jsonify(value=result)

    if name == 'pos':
        latest = Position.latest()
        hist = [getattr(latest,'pos%i' % i) for i in range(13)]
        bins = range(25,650,50)
        result = dict(zip(bins,hist))
        return jsonify(value=result)

    if name == 'events':
        value = db_session.query(L2.entry_time, L2.events).order_by(L2.entry_time.desc())[:600]
        t, y = zip(*value)
        result = {'t': [x.isoformat() for x in t], 'y': y}
        return jsonify(value=result)

    if name == 'events_passed':
        value = db_session.query(L2.entry_time, L2.passed_events).order_by(L2.entry_time.desc())[:600]
        t, y = zip(*value)
        result = {'t': [x.isoformat() for x in t], 'y': y}
        return jsonify(value=result)

    if name == 'delta_t':
        value = db_session.query(L2).order_by(L2.entry_time.desc())[:600]
        result = {'t': [x.entry_time.isoformat() for x in value],
                  'y': [total_seconds(x.entry_time - x.get_clock()) for x in value]}
        return jsonify(value=result)

    if name == 'cmos' or name == 'base':
        p = redis.pipeline()
        for index in CHANNELS:
            p.get('%s/index:%i:value' % (name,index))
        values = p.execute()

        return jsonify(value=values)

    if name == 'alarms':
        alarms = db_session.query(Alarms)
        return jsonify(messages=[dict(x) for x in alarms])

@app.route('/metric/')
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

    if expr in ('gtid', 'run', 'subrun', 'heartbeat'):
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

