#### This page contains instructions to add the second TLS REDB

Follow the instructions from the main [README](./README.md) to create a new TLS REDB instance in GCP Marketplace. Then follow the steps below to add support for the second TLS REDB:  


#### 1. Add a new TCP port to the Egress Gateway
Edit the Egress Gateway:
```
kubectl edit svc istio-egressgateway -n istio-system
```
Add the following section below port 16379:
```
  - name: redis-tls-16380
    port: 16380
    protocol: TCP
    targetPort: 16380
```
To confirm the new port:
```
kubectl get svc istio-egressgateway -n istio-system

NAME                  TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)               AGE
istio-egressgateway   ClusterIP   10.116.0.229   <none>        16379/TCP,16380/TCP   10m
```


#### 2. Create Kubernetes resources to configure Egress Gateway's TLS origination for the second TLS REDB 
```
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: redis-tls-19493-se
  namespace: istio-system
spec:
  hosts:
  - redis-19493.c17385.us-central1-mz.gcp.cloud.rlrcp.com
  ports:
  - number: 19493
    name: tcp-redis-tls-19493
    protocol: TCP
  resolution: DNS
  location: MESH_EXTERNAL
EOF
```
```
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: redis-tls-19493-dr
  namespace: istio-system
spec:
  host: redis-19493.c17385.us-central1-mz.gcp.cloud.rlrcp.com
  trafficPolicy:
    tls:
      mode: MUTUAL
      credentialName: redis-client-tls-19493
EOF
```
```
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: redis-tls-egressgateway-16380
  namespace: istio-system
spec:
  selector:
    istio: egress
  servers:
  - port:
      number: 16380
      name: tcp-redis-tls-16380
      protocol: TCP
    hosts:
    - '*'
EOF
```
```
kubectl apply -f - <<EOF
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: redis-tls-19493-egress-vs
  namespace: istio-system
spec:
  hosts:
  - redis-19493.c17385.us-central1-mz.gcp.cloud.rlrcp.com
  gateways:
  - redis-tls-egressgateway-16380
  - mesh
  tcp:
  - match:
    - gateways:
      - mesh
      port: 19493
    route:
    - destination:
        host: istio-egressgateway.istio-system.svc.cluster.local
        port:
          number: 16380
      weight: 100
  - match:
    - gateways:
      - redis-tls-egressgateway-16380
      port: 16380
    route:
    - destination:
        host: redis-19493.c17385.us-central1-mz.gcp.cloud.rlrcp.com
        port:
          number: 19493
      weight: 100
EOF
```
```
kubectl -n istio-system create secret generic \
redis-client-tls-19493 --from-file=tls.key=redislabs_user_private.key \
--from-file=tls.crt=redislabs_user.crt --from-file=ca.crt=redislabs_ca.pem
```


#### 3. Validate Egress Gateway's TLS origination for a secured mTLS REDB connection
Get a shell to the redis-client container:
```
kubectl exec -ti -n redis deploy/redis-client -c redis-client -- bash
```
Connect to the second TLS REDB instance with TLS origination configured through the Egress Gateway:
```
redis-cli -h <REPLACE_WITH_REDIS_HOST> -p <REPLACE_WITH_REDIS_PORT> -a <REPLACE_WITH_DEFAULT_USER_PASSWORD>

In my example,
redis-cli -h redis-19493.c17385.us-central1-mz.gcp.cloud.rlrcp.com -p 19493 -a [REDACTED]

Create a key-value pair:
set "watch" "panerai"
get "watch"

It shoud return "panerai"
```


