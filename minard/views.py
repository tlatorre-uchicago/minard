from minard import app
from flask import render_template, jsonify, request 
from minard.orca import total_seconds, redis
from sqlalchemy.sql import select
from minard.database import init_db, db_session
from minard.models import *
from datetime import datetime, timedelta

init_db()

PROJECT_NAME = 'Minard'
DEBUG = True
SECRET_KEY = "=S\t3w>zKIVy0n]b1h,<%|@EHBgfRJQ;A\rLC'[\x0blPF!` ai}/4W"

app.config.from_object(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detector')
def hero():
    return render_template('detector.html')

@app.route('/daq/<name>')
def channels(name):
    if name == 'cmos':
        return render_template('channels.html',name=name, threshold=5000)
    elif name == 'base':
        return render_template('channels.html',name=name, threshold=80)

@app.route('/stream')
def stream():
    return render_template('stream.html')

@app.route('/alarms')
def alarms():
    return render_template('alarms.html')

@app.route('/builder')
def builder():
    return render_template('builder.html')

@app.route('/query')
def query():
    name = request.args.get('name','',type=str)

    if name == 'tail_log':
        start = request.args.get('id',0,type=int)
        stop = int(redis.get('builder/global:next'))
        if start > stop:
            # server restart
            start = 0
        p = redis.pipeline()
        for i in range(start,stop):
            p.get('builder/uid:%i:msg' % i)
        value = map(lambda x: x if x is not None else '',p.execute())
        return jsonify(value=value,id=stop)

    if name == 'sphere':
    	latest = PMT.latest()
	id, charge_occupancy = zip(*db_session.query(PMT.pmtid, PMT.chargeocc)\
            .filter(PMT.id == latest.id).filter(PMT.chargeocc != 0).all())
        return jsonify(id=id, values2=charge_occupancy)

    if name == 'l2_info':
        id = request.args.get('id',None,type=str)

        if id is not None:
            info = db_session.query(L2).filter(L2.id == id).one()
        else:
            info = db_session.query(L2).order_by(L2.id.desc()).first()

        return jsonify(value=dict(info))

    if name == 'nhit':
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
        indices = []
        for crate in range(19):
            for card in range(16):
                for channel in range(32):
                    index = crate << 16 | card << 8 | channel
                    p.get('%s/index:%i:value' % (name,index))
                    indices.append(index)
        indices, values = zip(*filter(lambda x: x[1] is not None, zip(indices,p.execute())))
        result = dict(zip(indices,map(int,values)))
        return jsonify(value=result)

    if name == 'alarms':
        alarms = db_session.query(Alarms)
        return jsonify(messages=[dict(x) for x in alarms])
