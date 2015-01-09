import json
import httplib
import pprint
import datetime
from datetime import date, timedelta
import sys
from redis import Redis
redis = Redis()
import time
import datetime
import calendar
import os
import subprocess
import string
import shutil
import glob

TIME_INDEX = 'pca_tellie_runs_by_time'
RUN_INDEX = 'pca_tellie_runs_by_number'


def main():
    # Post some fake data to the Redis DB for
    # fake run 1000, it's all fake
    # now = the time now
    now = time.time()
    # run_time = time now
    run_time = time.time()
    channel_number = 100
    fiber_number = 100
    # Write the details to the DB,
    # start by building the hash
    pca_run_info = {
        'run_number': 1000,
        'analyze_time': now,
        'run_time': run_time,
        'channel': channel_number,
        'fiber_status': '0',
        'fiber_number': '100',
        'pca_status': 0,
        'number_events': 200000,
        'nhit': 70,
        'av_occupancy': 0.5,
        'av_hit': 10000,
        'flag_av_hit': 0,
        'flag_av_occ': 0,
        'flag_nevents': 0,
        'flag_nhit_spread': 0,
        'flag_nhit_walk': 0,
    }
    # Write, but make sure it expires after 10min
    key = 'pca-tellie-run-%s' % 1000
    p = redis.pipeline()
    p.hmset(key, pca_run_info)
    p.expire(key, 3600)
    p.zadd(RUN_INDEX, key, float(1000))
    p.zadd(TIME_INDEX, key, float(run_time))
    p.execute()

if __name__ == "__main__":
    main(*sys.argv[1:])
