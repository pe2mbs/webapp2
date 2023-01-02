import redis


def test_redis():
    cnt = 0
    while True:
        r = redis.Redis(host='localhost', db=0)
        r.set('foo', 'bar')
        r.set('bar', cnt )
        print( f"get: {r.get('foo')}    {r.get('bar')}" )
        cnt += 1
        del r

    return



if __name__ == '__main__':
    test_redis()
