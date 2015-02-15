from redis import Redis

redis = Redis()

TIME_INDEX = 'pca_tellie_runs_by_time'
RUN_INDEX = 'pca_tellie_runs_by_number'

# For now, create a data-structure that holds the install-status for each
# fiber. Ugh. This needs to be included in tellie couchdb

FIBER_POSITION = [   
#    ['Fiber', 'Node', 'AB', 'IsInstalled', 'IsDead', 'Type', 'Note'],
    [0, 0, 'A', False, False, 'BULK', ''],
    [2, 2, 'A', True, False, 'BULK', ''],
    [3, 3, 'A', True, False, 'BULK', ''],
    [4, 4, 'A', False, False, 'BULK', ''],
    [5, 5, 'A', False, False, 'BULK', ''],
    [6, 6, 'A', False, False, 'BULK', ''],
    [7, 7, 'A', False, False, 'BULK', ''],
    [8, 8, 'A', True, False, 'BULK', ''],
    [9, 9, 'A', True, False, 'BULK', ''],
    [10, 10, 'A', True, False, 'BULK', ''],
    [11, 11, 'A', False, False, 'BULK', ''],
    [12, 12, 'A', False, False, 'BULK', ''],
    [13, 13, 'A', False, False, 'BULK', ''],
    [14, 14, 'A', True, False, 'BULK', ''],
    [15, 15, 'A', True, False, 'BULK', ''],
    [16, 16, 'A', True, False, 'BULK', ''],
    [17, 17, 'A', False, False, 'BULK', ''],
    [18, 18, 'A', False, False, 'BULK', ''],
    [19, 19, 'A', False, False, 'BULK', ''],
    [20, 20, 'A', True, False, 'BULK', ''],
    [21, 21, 'A', True, False, 'BULK', ''],
    [22, 22, 'A', True, False, 'BULK', ''],
    [23, 23, 'A', False, False, 'BULK', ''],
    [24, 24, 'A', False, False, 'BULK', ''],
    [25, 25, 'A', False, False, 'BULK', ''],
    [26, 28, 'A', True, False, 'BULK', ''],
    [27, 27, 'A', True, False, 'BULK', ''],
    [28, 26, 'A', True, False, 'BULK', ''],
    [29, 29, 'A', False, False, 'BULK', ''],
    [30, 30, 'A', False, False, 'BULK', ''],
    [31, 31, 'A', True, False, 'BULK', ''],
    [32, 32, 'A', False, False, 'BULK', ''],
    [33, 33, 'A', True, False, 'BULK', ''],
    [34, 34, 'A', True, False, 'BULK', ''],
    [35, 35, 'A', True, False, 'BULK', ''],
    [36, 36, 'A', True, False, 'BULK', ''],
    [37, 37, 'A', True, False, 'BULK', ''],
    [38, 38, 'A', True, False, 'BULK', ''],
    [39, 39, 'A', False, False, 'BULK', ''],
    [40, 40, 'A', True, False, 'BULK', ''],
    [41, 41, 'A', False, False, 'BULK', ''],
    [42, 42, 'A', True, False, 'BULK', ''],
    [43, 43, 'A', False, False, 'BULK', ''],
    [44, 44, 'A', True, False, 'BULK', ''],
    [45, 45, 'A', True, False, 'BULK', ''],
    [46, 46, 'A', True, False, 'BULK', ''],
    [47, 47, 'A', True, True, 'BULK', 'Now 101'],
    [48, 48, 'A', False, False, 'BULK', ''],
    [49, 49, 'A', True, False, 'BULK', ''],
    [50, 50, 'A', False, False, 'BULK', ''],
    [51, 51, 'A', True, False, 'BULK', ''],
    [52, 52, 'A', False, False, 'BULK', ''],
    [53, 53, 'A', True, False, 'BULK', ''],
    [54, 54, 'A', True, False, 'BULK', ''],
    [55, 55, 'A', True, False, 'BULK', ''],
    [56, 56, 'A', True, False, 'BULK', ''],
    [57, 57, 'A', False, False, 'BULK', ''],
    [58, 58, 'A', True, False, 'BULK', ''],
    [59, 59, 'A', False, False, 'BULK', ''],
    [60, 60, 'A', True, False, 'BULK', ''],
    [61, 61, 'A', False, False, 'BULK', ''],
    [62, 62, 'A', True, False, 'BULK', ''],
    [63, 63, 'A', True, False, 'BULK', ''],
    [64, 64, 'A', True, False, 'BULK', ''],
    [65, 65, 'A', False, False, 'BULK', ''],
    [66, 66, 'A', False, False, 'BULK', ''],
    [67, 67, 'A', False, False, 'BULK', ''],
    [68, 68, 'A', False, False, 'BULK', ''],
    [69, 69, 'A', False, False, 'BULK', ''],
    [70, 70, 'A', False, False, 'BULK', ''],
    [71, 71, 'A', True, False, 'BULK', ''],
    [72, 72, 'A', True, False, 'BULK', ''],
    [73, 73, 'A', True, False, 'BULK', ''],
    [74, 74, 'A', False, False, 'BULK', ''],
    [75, 75, 'A', True, False, 'BULK', ''],
    [76, 76, 'A', False, False, 'BULK', ''],
    [77, 77, 'A', True, False, 'BULK', ''],
    [78, 78, 'A', True, False, 'BULK', ''],
    [79, 79, 'A', True, False, 'BULK', ''],
    [80, 80, 'A', True, False, 'BULK', ''],
    [81, 81, 'A', True, False, 'BULK', ''],
    [82, 82, 'A', True, False, 'BULK', ''],
    [83, 83, 'A', True, False, 'BULK', ''],
    [84, 84, 'A', True, False, 'BULK', ''],
    [85, 85, 'A', True, False, 'BULK', ''],
    [86, 86, 'A', True, False, 'BULK', ''],
    [87, 87, 'A', True, False, 'BULK', ''],
    [88, 88, 'A', True, False, 'BULK', ''],
    [89, 89, 'A', True, False, 'BULK', ''],
    [90, 90, 'A', True, False, 'BULK', ''],
    [91, 91, 'A', True, False, 'BULK', ''],
    [92, 92, 'A', True, False, 'BULK', ''],
    [93, 91, 'A', True, False, 'SPARE', ''],
    [94, 67, 'A', False, False, 'SPARE', ''],
    [95, 70, 'A', False, False, 'SPARE', ''],
    [96, 82, 'A', True, False, 'SPARE', ''],
    [97, 85, 'A', False, False, 'SPARE', ''],
    [98, 88, 'A', True, False, 'SPARE', ''],
    [99, 85, 'A', True, False, 'SPARE', ''],
    [100, 0, 'A', True, False, 'SPARE', ''],
    [101, 47, 'A', True, False, 'SPARE', ''],
    [102, 52, 'A', False, False, 'SPARE', ''],
    [103, 58, 'A', False, False, 'SPARE', ''],
    [104, 75, 'A', False, False, 'SPARE', ''],
    [105, 76, 'A', False, False, 'SPARE', ''],
    [106, 10, 'A', False, False, 'SPARE', ''],
    [107, 16, 'A', False, False, 'SPARE', ''],
    [108, 22, 'A', False, False, 'SPARE', ''],
    [109, 28, 'A', False, False, 'SPARE', ''],
    [110, 31, 'A', False, False, 'SPARE', ''],
    [1, 111, 'A', True, False, 'NECK', ''],
    [112, 112, 'A', False, False, 'NECK', '']]

def add_run_to_db(run_dict):
    '''
    Creates Redis entries for a run. Requires run_number and time keys in 
    run_dict
    '''
    key = 'pca-tellie-run-%s' % run_dict['run_number']
    p = redis.pipeline()
    p.hmset(key, run_dict)
    p.expire(key, 604800)
    p.zadd(RUN_INDEX, key, float(run_dict['run_number']))
    p.zadd(TIME_INDEX, key, float(run_dict['run_time']))
    return p.execute()  
    
def runs_after_time(time, maxtime = '+inf'):
    '''
    Returns Redis entries for all runs between time and maxtime. 
    Requires Redis instance, start-time and maximum time.
    '''
    keys = redis.zrangebyscore(TIME_INDEX, time, maxtime)
    p = redis.pipeline()
    for key in keys:
        p.hgetall(key)
    return p.execute()    
        
def runs_after_run(run, maxrun = '+inf'):
    '''
    Returns Redis entries for all runs between run and maxrun. 
    Requires Redis instance, start-run and maximum run.
    '''
    keys = redis.zrangebyscore(RUN_INDEX, run, maxrun)
    p = redis.pipeline()
    for key in keys:
        p.hgetall(key)
    return p.execute()    
    
def del_run_from_db(run_number):
    '''
    Delete run from Redis. Requires Redis instance and run number. 
    '''
    key = 'pca-tellie-run-%s' % run_number
    p = redis.pipeline()
    p.delete(key)
    p.zrem(RUN_INDEX, key)
    p.zrem(TIME_INDEX, key)
    return p.execute()
       
