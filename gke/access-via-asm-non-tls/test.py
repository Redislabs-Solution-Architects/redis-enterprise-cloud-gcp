import redis
import sys

r = redis.StrictRedis(host='redis-' + sys.argv[2] + '.demo.rec.' + sys.argv[1]  + '.nip.io',
                port=sys.argv[2], db=0, password=sys.argv[3])
print(r.info())
