import redis
import sys

r = redis.StrictRedis(host='redis-' + sys.argv[2] + '.demo.rec.' + sys.argv[1]  + '.nip.io',
                port=443, db=0, ssl=True, password=sys.argv[3],
                ssl_keyfile='./client.key',
                ssl_certfile='./client.cert',
                ssl_ca_certs='./proxy_cert.pem')
print(r.info())
