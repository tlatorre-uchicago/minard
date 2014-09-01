from redis import StrictRedis
from itertools import chain

redis = StrictRedis()

HMINCRBY = """
local k
for i, v in ipairs(ARGV) do
    if i % 2 == 1 then
        k = v
    else
        redis.call('HINCRBY', KEYS[1], k, tonumber(v))
    end
end
return true
"""

HMDIV = """
for i, v in ipairs(ARGV) do
    local n = tonumber(redis.call('HGET', KEYS[2], v))
    local d = tonumber(redis.call('HGET', KEYS[3], v))
    redis.call('HSET', KEYS[1], v, n/d)
end
return true
"""

AVGCRATE = """
local crate = tonumber(ARGV[1])
local n = 0
local sum = 0
for card=0,16 do
    for channel=0,32 do
        -- i = crate << 9 | card << 5 | channel
        local i = crate*16*32 + 32*card + channel
        local v = redis.call('HGET', KEYS[1], i)
        if v then
            sum = sum + tonumber(v)
            n = n + 1
        end
    end
end

if n > 0 then
    return string.format('%g',sum/n)
else
    return nil
end
"""

MAXCRATE = """
local crate = tonumber(ARGV[1])
local max = nil
for card=0,16 do
    for channel=0,32 do
        -- i = crate << 9 | card << 5 | channel
        local i = crate*16*32 + 32*card + channel
        local v = redis.call('HGET', KEYS[1], i)
        if v then
            v = tonumber(v)

            if max == nil or v > max then
                max = v
            end
        end
    end
end

if max == nil then
    return max
else
    return string.format('%g', max)
end
"""

_hmincrby = redis.register_script(HMINCRBY)
_hmdiv = redis.register_script(HMDIV)
_avgcrate = redis.register_script(AVGCRATE)
_maxcrate = redis.register_script(MAXCRATE)

def maxcrate(key, crate, client=None):
    """Returns the maximum field value for channels in `crate`."""
    return _maxcrate(keys=[key], args=[crate], client=client)

def avgcrate(key, crate, client=None):
    """
    Averages the hash fields for channels in a crate.

    Example:
        >>> redis.hmset('spam', {3584: 1, 3589: 100, 9728: 1e6})
        True
        >>> avgcrate('spam', 7)
        '50.5'
        >>> avgcrate('spam',19)
        '1e+06'
        >>> avgcrate('spam',0)
        None
    """
    return _avgcrate(keys=[key], args=[crate], client=client)

def hmincrby(key, mapping, client=None):
    """
    Increment multiple fields in the hash stored at `key`.

    Example:
        >>> redis.hmset('spam', {'a': 0, 'b': 1})
        True
        >>> hmincr('spam', {'a': 10, 'b': 1})
        1L
        >>> redis.hgetall('spam')
        {'a': '10', 'b': '2'}
    """
    args = chain.from_iterable(mapping.items())
    return _hmincrby(keys=[key], args=args, client=client)

def hmdiv(result, a, b, fields, client=None):
    """
    Divide multiple fields in the hash stored at `a` by
    fields in `b` and store the result in `result`.

    Example:
        >>> redis.hmset('a', {'a': 1, 'b': 2})
        True
        >>> redis.hmset('b', {'a': 2, 'b': 2})
        True
        >>> hmdiv('c','a','b', ['a','b'])
        1L
        >>> redis.hgetall('c')
        {'a': '0.5', 'b': '1'}
    """
    return _hmdiv(keys=[result,a,b], args=fields, client=client)
