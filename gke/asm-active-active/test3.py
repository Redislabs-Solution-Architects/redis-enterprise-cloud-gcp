import redis
import sys

print(sys.argv[2])

r = redis.StrictRedis(host=sys.argv[1],
                port=sys.argv[2], db=0, password=sys.argv[3])
print(r.info())
