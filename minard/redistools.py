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

_hmincr = redis.register_script(HMINCR)

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
