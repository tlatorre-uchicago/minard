from __future__ import division
from __future__ import print_function
from minard import app
from flask import render_template, jsonify, request, redirect, url_for
from itertools import product
import time
from redis import Redis
from os.path import join
import json
from tools import total_seconds, parseiso
import requests
from collections import deque, namedtuple
from timeseries import get_timeseries, get_interval
import random
import operator

import pcadb
import ecadb

TRIGGER_NAMES = \
['100L',
 '100M',
 '100H',
 '20',
 '20LB',
 'ESUML',
 'ESUMH',
 'OWLN',
 'OWLEL',
 'OWLEH',
 'PULGT',
 'PRESCL',
 'PED',
 'PONG',
 'SYNC',
 'EXTA',
 'EXT2',
 'EXT3',
 'EXT4',
 'EXT5',
 'EXT6',
 'EXT7',
 'EXT8',
 'SRAW',
 'NCD',
 'SOFGT',
 'MISS']


class Program(object):
    def __init__(self, name, machine=None, link=None, description=None, expire=10):
        self.name = name
        self.machine = machine
        self.link = link
        self.description = description
        self.expire = expire

redis = Redis()

PROGRAMS = [Program('builder','builder1.sp.snolab.ca',
                    description="event builder"),
            Program('dispatch','builder1.sp.snolab.ca',
                    description="event dispatcher"),
            Program('L2-server','builder1.sp.snolab.ca',
                    description="builder -> buffer transfer"),
            Program('L2-client','buffer1.sp.snolab.ca',
                    description="L2 processor"),
            Program('L2-convert','buffer1.sp.snolab.ca',
                    description="zdab -> ROOT conversion"),
            Program('L1-delete','buffer1.sp.snolab.ca',
                    description="delete L1 files"),
            Program('dataflow', expire=20*60,
                    link='http://snoplus.westgrid.ca:5984/buffer/_design/buffer/index.html'),
            Program('builder_copy', 'buffer1.sp.snolab.ca',
                    description="builder -> buffer transfer"),
            Program('buffer_copy', 'buffer1.sp.snolab.ca',
                    description="buffer -> grid transfer"),
            Program('builder_delete', 'buffer1.sp.snolab.ca',
                    description="builder deletion script"),
            Program('PCA','nino.physics.berkeley.edu',
                    link='http://snopluspmts.physics.berkeley.edu/pca',
                    description="monitor PCA data"),
            Program('ECA','nino.physics.berkeley.edu',
                    link='http://snopluspmts.physics.berkeley.edu/eca',
                    description="monitor ECA data")]

@app.route('/status')
def status():
    return render_template('status.html', programs=PROGRAMS)

<<<<<<< HEAD
@app.route('/test_ajax')
def test_ajax():
    import sys
    print("Hello world!",file=sys.stderr)
    return jsonify(value='world',key='blah',this='that')
=======
@app.route('/graph')
def graph():
    name = request.args.get('name')
    start = request.args.get('start')
    stop = request.args.get('stop')
    step = request.args.get('step',1,type=int)
    return render_template('graph.html',name=name,start=start,stop=stop,step=step)
>>>>>>> 91da7013963e441e598bc29548fff68dd43219f0

@app.route('/get_status')
def get_status():
    if 'name' not in request.args:
        return 'must specify name', 400

    name = request.args['name']

    up = redis.get('uptime:{name}'.format(name=name))

    if up is None:
        uptime = None
    else:
        uptime = int(time.time()) - int(up)

    return jsonify(status=redis.get('heartbeat:{name}'.format(name=name)),uptime=uptime)

@app.route('/view_log')
def view_log():
    name = request.args.get('name', '???')
    return render_template('view_log.html',name=name)

@app.route('/log', methods=['POST'])
def log():
    """Forward a POST request to the log server at port 8081."""
    resp = requests.post('http://127.0.0.1:8081', headers=request.headers, data=request.form)
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

@app.route('/daq')
def daq():
    return render_template('daq.html')

@app.route('/alarms')
def alarms():
    return render_template('alarms.html')

CHANNELS = [crate << 9 | card << 5 | channel \
            for crate, card, channel in product(range(20),range(16),range(32))]

@app.route('/query')
def query():
    name = request.args.get('name','',type=str)

    if name == 'dispatcher':
        return jsonify(name=redis.get('dispatcher'))

    if name == 'nhit':
        seconds = request.args.get('seconds',type=int)

        now = int(time.time())

        p = redis.pipeline()
        for i in range(seconds):
            p.lrange('ev:1:{ts}:nhit'.format(ts=now-i),0,-1)
        nhit = map(int,sum(p.execute(),[]))
        return jsonify(value=nhit)

    if name == 'occupancy':
        now = int(time.time())

        occ = []
        p = redis.pipeline()
        for channel in CHANNELS:
            p.get('ev:60:{0:d}:pmt:{1:d}'.format(now//60-1,channel))
        occ = p.execute()

        count = redis.get('ev:60:{0:d}:count'.format(now//60-1))

        if count is not None:
            count = int(count)
        else:
            count = 0

        occ = [int(n)/count if n else 0 for n in occ]

        return jsonify(values=occ)

    if name == 'cmos' or name == 'base':
        p = redis.pipeline()
        for index in CHANNELS:
            p.get('%s:%i:value' % (name,index))
        values = p.execute()

        return jsonify(value=values)

@app.route('/get_alarm')
def get_alarm():
    try:
        count = int(redis.get('alarms:count'))
    except TypeError:
        return jsonify(alarms=[],latest=-1)

    if 'start' in request.args:
        start = request.args.get('start',type=int)

        if start < 0:
            start = max(0,count + start)
    else:
        start = max(count-100,0)

    alarms = []
    for i in range(start,count):
        value = redis.get('alarms:{0:d}'.format(i))

        if value:
            alarms.append(json.loads(value))

    return jsonify(alarms=alarms,latest=count-1)

@app.route('/metric')
def metric():
    """Returns the time series for argument `expr` as a JSON list."""
    args = request.args

    expr = args['expr']
    start = args.get('start',type=parseiso)
    stop = args.get('stop',type=parseiso)
    now_client = args.get('now',type=parseiso)
    step = args.get('step',type=int)

    now = int(time.time())

    # adjust for clock skew
    dt = now_client - now
    start -= dt
    stop -= dt

    if expr in ('gtid', 'run', 'subrun', 'heartbeat','l2-heartbeat'):
        values = get_timeseries(expr,start,stop,step)
        return jsonify(values=values)

    if expr == u"0\u03bd\u03b2\u03b2":
        import random
        total = get_timeseries('TOTAL',start,stop,step)
        values = [int(random.random() < step/315360) if i else 0 for i in total]
        return jsonify(values=values)

    if '-' in expr:
        # e.g. PULGT-nhit, which means the average nhit for PULGT triggers
        # this is not a rate, so we divide by the # of PULGT triggers for
        # the interval instead of the interval length
        trig, _ = expr.split('-')
        values = get_timeseries(expr,start,stop,step)
        counts = get_timeseries(trig,start,stop,step)
        values = [float(a)/int(b) if a and b else None for a, b in zip(values,counts)]
    else:
        values = get_timeseries(expr,start,stop,step)
        interval = get_interval(step)
        if expr in TRIGGER_NAMES or expr in ('TOTAL','L1','L2','ORPHANS','BURSTS'):
            # trigger counts are zero by default
            values = map(lambda x: int(x)/interval if x else 0, values)
        else:
            values = map(lambda x: int(x)/interval if x else None, values)

    return jsonify(values=values)

@app.route('/eca')
def eca():

    def timefmt(time_string):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(float(time_string)))

    def testBit(int_type, offset):
        int_type = int(int_type)
        offset = int(offset)
        mask = 1 << offset
        return(int_type & mask)

    def parse_status(run_status, run_type):
        run_stauts = int(run_status)
        if run_type == 'PDST':
            #these are all the run-level status flags for PDST runs
            #some are worse to fail than others
            #decide monitoring pass/fail/do-over-if-time results based on which flags fail
            tooManyZeroEv = testBit(run_status,0)
            tooManyChWithFewEv = testBit(run_status,1)
            tooManyChFailBoardID = testBit(run_status,2)
            tooManyChFailQHS = testBit(run_status,3)
            tooManyChFailQHL = testBit(run_status,4)
            tooManyChFailQLX = testBit(run_status,5)
            tooManyChFailTAC = testBit(run_status,6)
            avgQHSbad = testBit(run_status,7)
            avgQHLbad = testBit(run_status,8)
            avgQLXbad = testBit(run_status,9)
            avgTACbad = testBit(run_status,10)
            avgQHSwidthBad = testBit(run_status,11)
            avgQHLwidthBad = testBit(run_status,12)
            avgQLXwidthBad = testBit(run_status,13)
            avgTACwidthBad = testBit(run_status,14)
            avgQHSdiffBad = testBit(run_status,15)
            avgQHLdiffBad = testBit(run_status,16)
            avgQLXdiffBad = testBit(run_status,17)
            avgTACdiffBad = testBit(run_status,18)
            tooManyFlaggedCh = testBit(run_status,19)
            UCbitSet = testBit(run_status,26)
            boardIDfail = testBit(run_status,27)
            sequencerIDfail = testBit(run_status,28)
            attemptDiffCheckFail = testBit(run_status,29)
            runNotComplete = testBit(run_status,30)
            attemptMergeFail = testBit(run_status,31)
            
            allflags=True
            for bit in range(0,32):
                thisbit = testBit(run_status,bit)
                if thisbit == 1:
                    allflags = False
                    break

            if allflags:
                return 1
            else:
                return 2  

        if run_type == 'TSLP':
            allflags=True
            for bit in range(0,32):
                thisbit = testBit(run_status,bit)
                if thisbit == 1:
                    allflags = False
                    break

            if allflags:
                return 1
            else:
                return 0  

    def statusfmt(status_int):
        if status_int == 0:
            return 'Fail'
        if status_int == 1:
            return 'Pass'
        if status_int == 2:
            return 'OK'
    
    def statusclass(status_int):
        if status_int == 0:
            return "danger"
        if status_int == 1:
            return "success"
        if status_int == 2:
            return "warning"

    runs = ecadb.runs_after_run(redis, 0)      

    return render_template('eca.html',runs=runs,parse_status=parse_status,timefmt=timefmt,statusfmt=statusfmt,statusclass=statusclass)
 
@app.route('/eca_run_detail')
#@app.route('/eca_run_detail?run=<run_number>')
@app.route('/eca_run_detail/<run_type>/<run_number>')
def eca_run_detail(run_type, run_number):
    if run_type == 'PDST': 
        return render_template('eca_run_detail_PDST.html',
                            run_type=run_type, run_number=run_number)      
    if run_type == 'TSLP': 
        return render_template('eca_run_detail_TSLP.html',
                            run_type=run_type, run_number=run_number)      

@app.route('/pcatellie', methods=['GET'])
def pcatellie():
    
    def timefmt(time_string):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(float(time_string)))
    
    def boolfmt(bool_string):
        bool_value = bool_string == '1'
        return "Pass" if not bool_value else "Fail"
    
    def boolclass(bool_string):
        bool_value = bool_string == '1'
        return "success" if not bool_value else "danger"
    
    start_run = request.args.get("start_run", 0)
    installed_only = request.args.get("installed_only", False)    
    runs = pcadb.runs_after_run(redis, start_run)      
    fibers = list()
    for fiber in pcadb.FIBER_POSITION:
        runs_for_fiber = [run for run in runs 
                          if int(run["fiber_number"]) == fiber[0]]
        sorted_runs = sorted(runs_for_fiber, 
                             key=lambda run: (run["pca_status"] == "True", int(run["run_number"])),
                             reverse=True)
        pca_run = sorted_runs[0]["run_number"] if sorted_runs else ""  
        pca_result = sorted_runs[0]["pca_status"] if sorted_runs else ""                   
        fibers.append({'fiber_number': fiber[0],
                       'node': fiber[1], 
                       'ab': fiber[2], 
                       'is_installed': fiber[3], 
                       'is_dead': fiber[4],
                       'fiber_type': fiber[5],
                       'pca_run': pca_run,
                       'pca_result': pca_result})
            
    # ['Fiber', 'Node', 'AB', 'IsInstalled', 'IsDead', 'Type'],
       
    return render_template('pcatellie.html',
                           runs=runs,
                           timefmt=timefmt,
                           boolfmt=boolfmt,
                           boolclass=boolclass,
                           fibers=fibers,
                           start_run=start_run,
                           installed_only=installed_only,
    )    
    
@app.route('/pca_run_detail/<run_number>')
def pca_run_detail(run_number):
    
    return render_template('pca_run_detail.html',
                            run_number=run_number)      

@app.route('/hello_world')
def hello_world():
    return render_template('hello_world.html')
    
@app.route('/hello_world_hist')    
def hello_world_hist():
    return jsonify(value=[random.gauss(0,1) for i in range(100)])
    
@app.route('/system_monitor')
def system_monitor():
    if not request.args.get('step'):
        return redirect(url_for('system_monitor',step=1,height=20,_external=True))
    step = request.args.get('step',1,type=int)
    height = request.args.get('height',40,type=int)
    return render_template('system_monitor.html',step=step,height=height)

@app.route('/hello_world_metric')
def hello_world_metric():
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

    if step > 60:
        t = 60
    else:
        t = 1

    p = redis.pipeline()
    for i in range(start,stop,step):
        p.get('stream/%i:%i:%s' % (t,i//t,expr))
    result = [float(x) if x else 0 for x in p.execute()]

    if t == 60:
        p = redis.pipeline()
        for i in range(start,stop,step):
            p.get('stream/60:%i:count' % (i//t))
        counts = [int(x) if x else 0 for x in p.execute()]
        result = [a/b for a, b in zip(result,counts)]

    return jsonify(values=result)    
