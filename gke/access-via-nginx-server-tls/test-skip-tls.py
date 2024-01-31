import redis
import sys

r = redis.StrictRedis(host='redis-' + sys.argv[2] + '.demo.rec.' + sys.argv[1]  + '.nip.io',
                port=443, db=0, ssl=True, password=sys.argv[3],
                ssl_cert_reqs="none")
print(r.info())
