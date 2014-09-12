from __future__ import print_function
import sys
from redis import Redis
import bisect
from redistools import maxcard, avgcard, maxcrate, avgcrate

redis = Redis()

# these are close to the optimal intervals for a 10 year timespan
# Suppose you want to save Y seconds of data, with a minimum resolution
# of 1 second and you can average the data over N different intervals.
# Also, you want to always be able to view atleast P different data
# points in the past for a given step size (this is roughly the number
# of pixels on your monitor, in the case of SNOPLUS, 4000).
# The optimal strategy for the intervals is to let the second interval, x, be
# x = Nth root of Y/P
# and then your intervals are [1,x,x**2,x**3,...,x**(N-1)]
# For our case, I chose Y = 315360000 (10 years), P = 4,000 (pixels)
# The optimal number of intervals N is actually somewhere around 20,
# but you get diminishing returns after 10, so this is easier.
INTERVALS = [1,3,9,29,90,280,867,2677,8267,25531]
EXPIRE = 3*4000

# intervals to store info per channel in a redis hash
HASH_INTERVALS = [5,60,24*60*60]
HASH_EXPIRE = 2000

def get_hash_interval(step):
    i = bisect.bisect_right(HASH_INTERVALS,step)-1
    return HASH_INTERVALS[i if i > 0 else 0]

def get_interval(step):
    i = bisect.bisect_right(INTERVALS,step)-1
    return INTERVALS[i if i > 0 else 0]

def get_hash_timeseries(name, start, stop, step, crate, card=None,
                        channel=None, method='avg', type=None):
    """
    Returns the time series for `name` from `start` to `stop` in
    increments of `step`.

    `start` and `stop` should be UNIX timestamps. `step` should have
    units of seconds.

    If `card` is None, return results for the entire crate by
    computing `method`, which may be `max` or `avg` for the maximum
    and average value respectively.

    If `channel` is None, return results for the entire card.
    """
    interval = get_hash_interval(step)

    p = redis.pipeline()
    for i in range(start, stop, step):
        key = 'ts:%i:%i:%s' % (interval, i//interval, name)

        if card is None:
            # crate
            p.hget(key + ':crate:' + method, crate)
        elif channel is None:
            # card
            p.hget(key + ':card:' + method, crate*512 + card*32)
        else:
            # channel
            i = crate*16*32 + card*32 + channel
            p.hget(key, i)

    values = p.execute()

    if type is None:
        return values

    return map(type, values)

def get_timeseries(name, start, stop, step, type=None):
    """
    Returns the time series for `name` from start to stop in increments of
    step. start, stop, and step should all be UNIX timestamps.
    """
    interval = get_interval(step)

    p = redis.pipeline()
    for i in range(start, stop, step):
        key = 'ts:%i:%i:%s' % (interval,i//interval,name)
        p.get(key)

    values = p.execute()

    if type is None:
        return values

    return map(type, values)

def get_timeseries_field(name, field, start, stop, step, type=None):
    """
    Returns the time series for `name` from start to stop in increments of
    step. start, stop, and step should all be UNIX timestamps.
    """
    interval = get_interval(step)

    p = redis.pipeline()
    for i in range(start, stop, step):
        key = 'ts:%i:%i:%s' % (interval,i//interval,name)
        p.hget(key, field)

    values = p.execute()

    if type is None:
        return values

    return map(type, values)

