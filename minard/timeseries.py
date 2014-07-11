from redis import Redis
import bisect

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

def get_timeseries(name, start, stop, step, type=None):
    """
    Returns the time series for `name` from start to stop in increments of
    step. start, stop, and step should all be UNIX timestamps.
    """
    interval = INTERVALS[bisect.bisect_right(INTERVALS,step)-1]

    p = redis.pipeline()
    for i in range(start, stop, step):
        p.get('stream/int:{0}:id:{1}:name:{2}'.format(interval,i//interval,name))
    values = p.execute()

    if type is None:
        return values

    return map(type, values)

