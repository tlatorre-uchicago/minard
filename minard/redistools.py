from redis import StrictRedis
from itertools import chain

redis = StrictRedis()

HMINCR = """
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

_hmincr = redis.register_script(HMINCR)
_hmdiv = redis.register_script(HMDIV)

def hmincr(key, mapping):
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
    return _hmincr(keys=[key],args=args)

def hmdiv(result, a, b, fields):
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
        {'a': '0.5', 'b': 1}
    """
    return _hmdiv(keys=[result,a,b], args=fields)
