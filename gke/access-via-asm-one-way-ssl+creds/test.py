import redis
import sys

r = redis.StrictRedis(
                host='redis-' + sys.argv[2] + '.demo.rec.' + sys.argv[1]  + '.nip.io',
                port=443, 
                db=0, 
                ssl=True, 
                username=sys.argv[3],
                password=sys.argv[4],
                ssl_ca_certs='./proxy_cert.pem')
print(r.info())
