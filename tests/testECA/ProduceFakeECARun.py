#!/usr/bin/env python
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

TIME_INDEX = 'eca_runs_by_time'
RUN_INDEX = 'eca_runs_by_number'


def main():
    # Post some fake data to the Redis DB for
    # fake run 8523, it's all fake
    # now = the time now
    now = time.time()
    # run_time = time now
    run_time = time.time()
    # Write the details to the DB,
    # start by building the hash
    eca_run_info = {
        'run_number': 8523,
        'analyze_time': now,
        'run_time': run_time,
        'run_status': 0,
        'run_type': 'PDST',
    }
    # Write, but make sure it expires after 1hour
    key = 'eca-run-%s' % 8523
    p = redis.pipeline()
    p.hmset(key, eca_run_info)
    p.expire(key, 3600)
    p.zadd(RUN_INDEX, key, float(8523))
    p.zadd(TIME_INDEX, key, float(run_time))
    p.execute()

if __name__ == "__main__":
    main(*sys.argv[1:])
